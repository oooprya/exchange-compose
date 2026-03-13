# from decimal import Decimal
# from django.shortcuts import redirect, render
# from django.db.models import Sum
# from django.http import JsonResponse
# from django.utils import timezone
# from django.contrib import messages
# from .models import Shift, CashBalance


# from wholesale.services.balance_service import get_dashboard_balances


# def dashboard_balances_api(request):
#     if not request.user.is_authenticated:
#         return JsonResponse({"error": "Unauthorized"}, status=401)

#     return JsonResponse(get_dashboard_balances())


# def dashboard_callback(request, context):

#     user = request.user

#     # доступ только менеджеру или суперюзеру
#     if not (user.is_superuser or getattr(user, "staffprofile", None) and user.staffprofile.role == "senior"):
#         return context

#     staff = getattr(user, "staffprofile", None)

#     active_shift = None
#     if staff:
#         active_shift = (
#             Shift.objects
#             .select_related("staff__user", "node")
#             .filter(staff=staff, is_open=True)
#             .first()
#         )

#     context["active_shift"] = active_shift

#     # Собираем остатки по всем кассам
#     balances = (
#         CashBalance.objects
#         .exclude(currency__code__in=["usd", "usd-old"])
#         .select_related("node__exchange_point", "currency")
#         .order_by(
#             "node__exchange_point",
#             "node__name",
#             "currency__sort_order"
#         )
#     )
#     usd_total = (
#         CashBalance.objects
#         .filter(currency__code__in=["usd", "usd-old", "usd-new"])
#         .aggregate(total=Sum("balance"))
#     ).get("total") or 0

#     usd_new = (
#         CashBalance.objects
#         .filter(currency__code="usd-new")
#         .aggregate(total=Sum("balance"))
#     ).get("total") or 0

#     usd_old = (
#         CashBalance.objects
#         .filter(currency__code="usd-old")
#         .aggregate(total=Sum("balance"))
#     ).get("total") or 0

#     grouped = {}

#     for b in balances:
#         ep = b.node.exchange_point.address
#         node = b.node.name

#         grouped.setdefault(ep, {})
#         grouped[ep].setdefault(node, [])
#         grouped[ep][node].append(b)

#     context["dashboard_balances"] = grouped
#     context["usd_total"] = usd_total
#     context["usd_new"] = usd_new
#     context["usd_old"] = usd_old

#     return context


# def close_shift_view(request):

#     cashier = getattr(request.user, "StaffProfile", None)

#     if not cashier:
#         messages.error(request, "Профиль кассира не найден.")
#         return redirect("/admin/")

#     shift = Shift.objects.filter(
#         cashier=cashier,
#         is_open=True
#     ).first()

#     if not shift:
#         messages.error(request, "Нет открытой смены.")
#         return redirect("/admin/")

#     report = {}
#     balances = CashBalance.objects.filter(
#         node=shift.node
#     ).select_related("currency")

#     for b in balances:
#         start = Decimal(shift.opening_balances.get(b.currency.code, "0"))
#         end = b.balance

#         report[b.currency.code] = {
#             "start": start,
#             "end": end,
#             "diff": end - start
#         }

#     shift.is_open = False
#     shift.closed_at = timezone.now()
#     shift.save()

#     request.session["shift_report"] = report

#     messages.success(request, "Смена успешно закрыта.")

#     return redirect("/admin/shift-report/")


# def shift_report_view(request):

#     report = request.session.get("shift_report")

#     return render(request, "admin/shift_report.html", {
#         "report": report
#     })


from decimal import Decimal
from django.shortcuts import redirect, render
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from wholesale.services.balance_service import BalanceService

from .models import Shift, CashBalance


@login_required
def dashboard_balances_api(request):
    """
    Используется только для первоначальной загрузки,
    realtime работает через WebSocket.
    """

    balances = (
        CashBalance.objects
        .select_related("node", "currency")
        .values(
            "node_id",
            "currency__code"
        )
        .annotate(total=Sum("balance"))
    )

    return JsonResponse({
        "balances": list(balances)
    })


def dashboard_callback(request, context):

    user = request.user

    if not (
        user.is_superuser or
        (hasattr(user, "staffprofile") and user.staffprofile.role == "senior")
    ):
        return context

    # Получаем все балансы
    balances = (
        CashBalance.objects
        .select_related(
            "node__exchange_point",
            "currency"
        )
        # .exclude(currency__code__in=["usd", "usd-old"])
        .order_by(
            "node__exchange_point__address",
            "node__name",
            "currency__sort_order"
        )
    )

    grouped = {}

    for b in balances:

        exchange_address = b.node.exchange_point.address
        node_name = b.node.name

        grouped.setdefault(exchange_address, {})
        grouped[exchange_address].setdefault(node_name, [])
        grouped[exchange_address][node_name].append(b)

    context["dashboard_balances"] = grouped

    return context


@login_required
def close_shift_view(request):

    staff = getattr(request.user, "staffprofile", None)

    if not staff:
        messages.error(request, "Профиль кассира не найден.")
        return redirect("/admin/")

    shift = (
        Shift.objects
        .filter(staff=staff, is_open=True)
        .first()
    )

    if not shift:
        messages.error(request, "Нет открытой смены.")
        return redirect("/admin/")

    # формируем отчёт
    report = {}

    balances = (
        CashBalance.objects
        .filter(node=shift.node)
        .select_related("currency")
    )

    for b in balances:
        start = Decimal(
            shift.opening_balances.get(b.currency.code, "0")
        )
        end = b.balance

        report[b.currency.code] = {
            "start": start,
            "end": end,
            "diff": end - start
        }

    shift.is_open = False
    shift.closed_at = timezone.now()
    shift.save(update_fields=["is_open", "closed_at"])

    request.session["shift_report"] = report

    messages.success(request, "Смена успешно закрыта.")

    return redirect("/admin/shift-report/")


@login_required
def shift_report_view(request):

    report = request.session.get("shift_report")

    return render(
        request,
        "admin/shift_report.html",
        {"report": report}
    )
