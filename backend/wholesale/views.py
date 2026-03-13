from django.db.models import Sum
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
from wholesale.services.balance_service import BalanceService
from .models import CashBalance


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

    if not (
        user.is_superuser or
        (hasattr(user, "staffprofile") and user.staffprofile.role == "senior")
    ):
        return context

    context["dashboard_balances"] = BalanceService.get_dashboard_balances()

    return context
