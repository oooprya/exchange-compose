from decimal import Decimal
from currency.models import Currency

from asgiref.sync import async_to_sync
from django.db.models import Sum, Q
from wholesale.models import CashBalance, CashMovement
from channels.layers import get_channel_layer
from wholesale.models import CashBalance, Shift
from django.core.exceptions import ValidationError


def get_node_balances(node_id, staff=None, opened_at=None):

    balances = (
        CashBalance.objects
        .filter(node_id=node_id)
        .select_related("currency")
    )

    result = {}

    if staff:
        user = staff.user

        cashier = user.get_full_name() or user.username
        phone = staff.telephone
        opened_at = (opened_at.strftime("%H:%M") if opened_at else None
                     )
    for b in balances:
        result[b.currency.code] = float(b.balance)

    usd_total = (
        balances
        .filter(currency__code__icontains="usd")
        .aggregate(total=Sum("balance"))
        .get("total") or 0
    )

    return {
        "node_id": node_id,
        "cashier": cashier,
        "phone": phone,
        "opened_at": opened_at,
        "balances": result,
        "usd_total": float(usd_total)

    }


def broadcast_node(node_id):

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"dashboard_node_{node_id}",
        {
            "type": "balance_update",
            "data": get_node_balances(node_id)
        }
    )


def broadcast_balance(data):

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "dashboard_global",
        {
            "type": "balance_update",
            "data": data
        }
    )


class BalanceService:

    #     @staticmethod
    #     def broadcast_node():

    #         channel_layer = get_channel_layer()

    #         data = BalanceService.get_dashboard_balances()
    #         print("broadcast", data)

    #         async_to_sync(channel_layer.group_send)(

    #             "dashboard_balances",
    #             {
    #                 "type": "balance_update",
    #                 "data": data,
    #             }
    #         )

    @staticmethod
    def get_dashboard_balances():

        balances_qs = (
            CashBalance.objects
            .select_related("currency", "node", "node__exchange_point")
        )

        nodes_data = {}

        # --- Балансы ---
        for b in balances_qs:

            if not b.balance or b.balance == 0:
                continue

            node = b.node

            if node.id not in nodes_data:
                nodes_data[node.id] = {
                    "node_id": node.id,
                    "node_name": node.name,
                    "exchange_point": node.exchange_point,
                    "balances": [],
                    "usd": {"total": 0, "new": 0, "old": 0},
                    "cashier": None,
                    "phone": None,
                    "opened_at": None
                }

            nodes_data[node.id]["balances"].append({
                "currency": b.currency.code,
                "amount": float(b.balance)
            })

        # --- USD агрегаты ---
        for node_id in nodes_data:

            usd_qs = balances_qs.filter(
                node_id=node_id,
                currency__code__startswith="usd"
            )

            usd_agg = usd_qs.aggregate(
                total=Sum("balance"),
                new=Sum("balance", filter=Q(currency__code="usd-new")),
                old=Sum("balance", filter=Q(currency__code="usd-old")),
            )

            nodes_data[node_id]["usd"] = {
                "total": float(usd_agg["total"] or 0),
                "new": float(usd_agg["new"] or 0),
                "old": float(usd_agg["old"] or 0),
            }

        # --- Открытые смены ---
        shifts = (
            Shift.objects
            .filter(is_open=True)
            .select_related("node", "staff__user")
        )

        for shift in shifts:

            node_id = shift.node.id

            if node_id in nodes_data:

                user = shift.staff.user

                nodes_data[node_id]["cashier"] = (
                    user.get_full_name() or user.username
                )

                nodes_data[node_id]["phone"] = shift.staff.telephone

                nodes_data[node_id]["opened_at"] = (
                    shift.opened_at.strftime("%H:%M")
                    if shift.opened_at else None
                )

        return list(nodes_data.values())

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

        # IN → приход
        elif order.order_type == "in":

            currency_balance.balance += amount

        # =========================
        # OUT
        # =========================
        elif order.order_type == "out":

            if currency_balance.balance < amount:
                raise ValidationError("Недостаточно средств в кассе")

            currency_balance.balance -= amount
            print(f'amount {amount}')

        currency_balance.save()

        # Лог движения
        CashMovement.objects.create(
            node=node,
            currency=currency,
            movement_type=order.order_type,
            amount=amount
        )
