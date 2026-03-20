from datetime import timedelta
from django.db.models import Sum
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import ValidationError
from django.db import transaction

from django.contrib.auth.decorators import login_required

from wholesale.services.balance_service import BalanceService

from .models import CashBalance, WholesaleOrder


@transaction.atomic
def reverse_order(request, order_id):

    order = get_object_or_404(WholesaleOrder, id=order_id)

    # проверка 45 минут
    if timezone.now() - order.created_at > timedelta(minutes=45):
        raise ValidationError("Время сторно истекло")

    # только последний
    last_order = WholesaleOrder.objects.order_by("-created_at").first()
    if order.id != last_order.id:
        raise ValidationError("Можно сторнировать только последнюю операцию")

    reverse_type = {
        "buy": "sell",
        "sell": "buy",
        "in": "out",
        "out": "in"
    }[order.order_type]

    reverse_order = WholesaleOrder.objects.create(
        shift=order.shift,
        currency=order.currency,
        order_type=reverse_type,
        amount_currency=order.amount_currency,
        amount_base=order.amount_base,
        rate=order.rate
    )

    BalanceService.apply_order(reverse_order)

    return redirect(request.META.get("HTTP_REFERER", "/admin/"))


@login_required
def dashboard_balances_api(request):
    """
    Используется только для первоначальной загрузки,
    realtime работает через WebSocket.
    """

    balances = (
        CashBalance.objects
        .values(
            "node_id",
            "currency__code"
        )
        .annotate(total=Sum("balance"))
    )

    return JsonResponse({"balances": list(balances)})


def dashboard_callback(request, context):

    user = request.user
    staff = getattr(user, "staffprofile", None)

    dashboard = BalanceService.get_dashboard_balances() or []
    # 🔐 Пока что показываем панель только суперюзерам и старшим.
    # Кассиру нужно показать только его открытую кассу (если есть).
    if user.is_superuser or (staff and staff.role == "senior"):
        context["dashboard_balances"] = dashboard
        return context

    if staff and staff.role == "cashier":
        # Показываем только балансы по тем кассам, к которым у кассира есть доступ.
        allowed_node_ids = set(staff.nodes.filter(
            is_active=True).values_list("id", flat=True))
        context["dashboard_balances"] = [
            node for node in dashboard if node.get("node_id") in allowed_node_ids
        ]

    return context
