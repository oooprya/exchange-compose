# from django.db.models import Sum
# from django.core.cache import cache

from decimal import Decimal
from currency.models import Currency

from asgiref.sync import async_to_sync
from django.db.models import Sum, Q
from wholesale.models import CashBalance, CashMovement
from channels.layers import get_channel_layer
from wholesale.models import CashBalance, Shift
from django.core.exceptions import ValidationError


def broadcast_balance(node_id, data):

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"node_{node_id}",
        {
            "type": "balance_update",
            "data": data,
        }
    )

# BALANCE_CACHE_KEY = "dashboard_all_balances"


# def get_dashboard_balances():
#     data = cache.get(BALANCE_CACHE_KEY)

#     if data:
#         return data

#     balances = (
#         CashBalance.objects
#         .values("currency__code", "currency__name")
#         .annotate(total=Sum("balance"))
#     )

#     usd_total = (
#         CashBalance.objects
#         .filter(currency__code__in=["usd", "usd-old", "usd-new"])
#         .aggregate(total=Sum("balance"))
#         .get("total") or 0
#     )

#     data = {
#         "balances": list(balances),
#         "usd_total": float(usd_total),
#     }

#     cache.set(BALANCE_CACHE_KEY, data, 10)  # кэш 10 секунд
#     return data

class BalanceService:

    # @staticmethod
    # def get_node_balances(node_id):

    #     balances = (
    #         CashBalance.objects
    #         .filter(node_id=node_id)
    #         .select_related("currency")
    #     )

    #     usd_qs = balances.filter(
    #         currency__code__in=["usd", "usd-new", "usd-old"]
    #     )

    #     usd_total = usd_qs.aggregate(
    #         total=Sum("balance")
    #     )["total"] or 0

    #     usd_new = usd_qs.filter(
    #         currency__code="usd-new"
    #     ).aggregate(
    #         total=Sum("balance")
    #     )["total"] or 0

    #     usd_old = usd_qs.filter(
    #         currency__code="usd-old"
    #     ).aggregate(
    #         total=Sum("balance")
    #     )["total"] or 0

    #     active_shift = (
    #         Shift.objects
    #         .filter(node_id=node_id, is_open=True)
    #         .select_related("staff__user")
    #         .first()
    #     )

    #     cashier_name = None
    #     if active_shift:
    #         cashier_name = (
    #             active_shift.staff.user.get_full_name()
    #             or active_shift.staff.user.username
    #         )

    #     return {
    #         "node_id": node_id,
    #         "balances": [
    #             {
    #                 "currency": b.currency.code,
    #                 "amount": float(b.balance)
    #             }
    #             for b in balances
    #         ],
    #         "usd": {
    #             "total": float(usd_total),
    #             "new": float(usd_new),
    #             "old": float(usd_old),
    #         },
    #         "cashier": cashier_name
    #     }

    @staticmethod
    def get_node_balances(node_id):

        balances_qs = (
            CashBalance.objects
            .filter(node_id=node_id)
            .select_related("currency")
        )

        balances = [
            {
                "currency": b.currency.code,
                "amount": float(b.balance)
            }
            for b in balances_qs
        ]

        # USD агрегаты
        usd = balances_qs.filter(currency__code__startswith="usd")

        usd_agg = usd.aggregate(
            total=Sum("balance"),
            new=Sum("balance", filter=Q(currency__code="usd-new")),
            old=Sum("balance", filter=Q(currency__code="usd-old")),
        )

        # активная смена
        active_shift = (
            Shift.objects
            .filter(node_id=node_id, is_open=True)
            .select_related("staff__user")
            .first()
        )

        cashier = None
        phone = None

        if active_shift:
            user = active_shift.staff.user
            cashier = user.get_full_name() or user.username
            phone = active_shift.staff.telephone

        return {
            "node_id": node_id,
            "balances": balances,
            "usd": {
                "total": float(usd_agg["total"] or 0),
                "new": float(usd_agg["new"] or 0),
                "old": float(usd_agg["old"] or 0),
            },
            "cashier": cashier,
            "phone": phone
        }

    # broadcast обновления
    @staticmethod
    def broadcast_node(node_id):

        channel_layer = get_channel_layer()

        data = BalanceService.get_node_balances(node_id)

        async_to_sync(channel_layer.group_send)(
            "dashboard_global",
            {
                "type": "dashboard_update",
                "data": data
            }
        )

    @staticmethod
    def apply_order(order):
        """
        buy  – касса получает валюту, отдаёт UAH
        sell – касса отдаёт валюту, получает UAH
        in   – приход в кассу
        out  – расход из кассы
        """

        node = order.shift.node
        currency = order.currency
        amount = order.amount_currency
        amount_base = order.amount_base or Decimal("0")

        uah = Currency.objects.get(code="uah")

        # Блокируем строки
        currency_balance, _ = CashBalance.objects.select_for_update().get_or_create(
            node=node,
            currency=currency,
            defaults={"balance": Decimal("0")}
        )

        # Для buy/sell нужен UAH
        if order.order_type in ["buy", "sell"]:
            uah_balance, _ = CashBalance.objects.select_for_update().get_or_create(
                node=node,
                currency=uah,
                defaults={"balance": Decimal("0")}
            )

        # =========================
        # BUY
        # =========================
        if order.order_type == "buy":

            if uah_balance.balance < amount_base:
                raise ValidationError("Недостаточно гривны в кассе")

            currency_balance.balance += amount
            uah_balance.balance -= amount_base

            uah_balance.save()

        # =========================
        # SELL
        # =========================
        elif order.order_type == "sell":

            if currency_balance.balance < amount:
                raise ValidationError("Недостаточно валюты в кассе")

            currency_balance.balance -= amount
            uah_balance.balance += amount_base

            uah_balance.save()

        # =========================
        # IN
        # =========================
        elif order.order_type == "in":
            currency_balance.balance += amount

        # =========================
        # OUT
        # =========================
        elif order.order_type == "out":

            if currency_balance.balance < amount:
                raise ValidationError("Недостаточно средств в кассе")

            currency_balance.balance -= amount

        currency_balance.save()

        # Лог движения
        CashMovement.objects.create(
            node=node,
            currency=currency,
            movement_type=order.order_type,
            amount=amount
        )
