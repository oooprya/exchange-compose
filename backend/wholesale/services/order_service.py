from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from wholesale.models import WholesaleOrder
from wholesale.services.balance_service import BalanceService, broadcast_balance, get_node_balances


class OrderService:

    @staticmethod
    @transaction.atomic
    def reverse_order(order):
        """
        Сторно ордера: откат баланса через CashMovement.
        """
        if order.is_reversed:
            raise ValueError("Операция уже сторнирована")

        if order.created_at < timezone.now() - timedelta(hours=8):
            raise ValueError("Прошло более 8 часов, сторно невозможно")

        # Откатываем баланс
        BalanceService.reverse_order(order)

        # Помечаем ордер
        order.is_reversed = True
        order.save(update_fields=["is_reversed"])

        # WebSocket уведомление
        broadcast_balance(
            get_node_balances(
                node_id=order.shift.node_id,
                staff=order.shift.staff,
                opened_at=order.shift.opened_at
            )
        )

        return order

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

        if amount_currency <= 0:
            raise ValidationError("Сумма должна быть больше нуля")

        if order_type in {"buy", "sell"} and not rate:
            raise ValueError("Курс обязателен")

        if amount_base is None:
            amount_base = (
                (amount_currency * rate).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
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
        # Пополняем поле profit для дальнейшей агрегации
        # Условная формула: for 'sell' profit = amount_base, for 'buy' profit = -amount_base, others 0
        if order_type == 'sell':
            order.profit = amount_base
        elif order_type == 'buy':
            order.profit = -amount_base
        else:
            order.profit = Decimal('0')
        order.save(update_fields=['profit'])
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

    @staticmethod
    @transaction.atomic
    def create_collection_order(shift, items, comment, order_type="collect"):
        """Create one journal order while applying several currency balances."""
        if not items:
            raise ValidationError("Не выбрана ни одна валюта")

        first_item = items[0]
        collection_items = [
            {
                "currency_id": item["currency"].pk,
                "currency_code": item["currency"].code,
                "currency_name": item["currency"].name,
                "amount": str(item["amount"]),
            }
            for item in items
        ]
        total_amount = sum((item["amount"] for item in items), Decimal("0"))

        order = WholesaleOrder.objects.create(
            shift=shift,
            currency=first_item["currency"],
            order_type=order_type,
            amount_currency=total_amount,
            amount_base=total_amount,
            comment=comment,
            collection_items=collection_items,
            profit=Decimal("0"),
        )

        BalanceService.apply_order(order)
        broadcast_balance(
            get_node_balances(
                node_id=shift.node_id,
                staff=shift.staff,
                opened_at=shift.opened_at,
            )
        )
        return order
