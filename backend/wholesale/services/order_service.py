from django.db import transaction
from wholesale.models import WholesaleOrder
from wholesale.services.balance_service import BalanceService, broadcast_balance, get_node_balances


class OrderService:

    @staticmethod
    @transaction.atomic
    def create_order(
        shift,
        currency,
        order_type,
        amount_currency,
        rate=None,
        amount_base=None,
        comment="",
        base_currency=None
    ):

        if order_type in {"buy", "sell"} and not rate:
            raise ValueError("Курс обязателен")

        amount_base = (
            amount_currency * rate
            if rate else amount_currency
        )

        order = WholesaleOrder.objects.create(
            shift=shift,
            currency=currency,
            order_type=order_type,
            amount_currency=amount_currency,
            rate=rate,
            amount_base=amount_base,
            comment=comment,
            base_currency=base_currency,
        )
        # обновляем баланс с информацией о версии базовой валюты
        BalanceService.apply_order(order, base_currency=base_currency)

        # # 🔴 обновляем dashboard
        broadcast_balance(
            get_node_balances(
                node_id=order.shift.node_id,
                staff=order.shift.staff,
                opened_at=order.shift.opened_at
            )
        )

        return order
