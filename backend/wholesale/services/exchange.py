from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from currency.models import Currency
from wholesale.models import CashBalance, CashMovement


def process_exchange(order):
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

    with transaction.atomic():

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
