from decimal import Decimal
from currency.models import Currency
from django.utils.timezone import localtime
from asgiref.sync import async_to_sync
from django.db.models import Sum, Q
from channels.layers import get_channel_layer
from django.core.exceptions import ValidationError
from wholesale.models import CashBalance, CashMovement, Shift


def get_node_balances(node_id, staff=None, opened_at=None):

    balances = (
        CashBalance.objects
        .filter(node_id=node_id)
        .select_related("currency")
    )

    result = {}

    opened_at_str = None

    if staff:
        user = staff.user
        cashier = user.get_full_name() or user.username
        phone = staff.telephone

        if opened_at:
            opened_at_str = localtime(opened_at).strftime("%H:%M")

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
        "opened_at": opened_at_str,
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

            if not node:
                continue

            if node.id not in nodes_data:
                nodes_data[node.id] = {
                    "node_id": node.id,
                    "node_name": node.name,
                    "exchange_point": node.exchange_point if node.exchange_point else None,
                    "balances": [],
                    "usd": {"total": 0, "new": 0, "old": 0},
                    "cashier": None,
                    "phone": None,
                    "opened_at": None
                }

            nodes_data[node.id]["balances"].append({
                "currency": b.currency.code,
                "currency_name": b.currency.name,
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
                new=Sum("balance", filter=Q(currency__code="usdnew")),
                old=Sum("balance", filter=Q(currency__code="usdold")),
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

            if not shift.node:
                continue

            node_id = shift.node.id

            if node_id in nodes_data:

                user = shift.staff.user

                nodes_data[node_id]["cashier"] = (
                    user.get_full_name() or user.username
                )

                nodes_data[node_id]["phone"] = shift.staff.telephone

                nodes_data[node_id]["opened_at"] = (
                    localtime(shift.opened_at).strftime("%H:%M")
                    if shift.opened_at else None
                )

        return list(nodes_data.values())

    @staticmethod
    def apply_order(order, base_currency=None):
        """
        Обычные курсы:
            buy  – касса получает валюту, отдаёт UAH
            sell – касса отдаёт валюту, получает UAH
            in   – приход в кассу
            out  – расход из кассы

        Кроссовые курсы (USD-EUR):
            buy  – касса получает первую валюту (EUR), отдаёт вторую (USD/USD-new)
            sell – касса отдаёт первую валюту (EUR), получает вторую (USD/USD-new)
        """

        node = order.shift.node
        currency = order.currency
        amount = order.amount_currency
        amount_base = order.amount_base or Decimal("0")

        # Комментарий для записей в истории движений
        movement_comment = order.comment or (
            f"{order.get_order_type_display()} {order.amount_currency} {order.currency}"
            + (f" → {order.amount_base} {order.base_currency}" if order.base_currency else "")
        )

        is_cross_rate = '-' in (currency.code or '')

        if is_cross_rate:
            parts = currency.code.split('-')

            if parts[0] == "usd":
                base_code = parts[0]
                quote_code = parts[1]
            elif parts[1] == "usd":
                base_code = parts[1]
                quote_code = parts[0]

            try:
                # Используем передаваемую версию базовой валюты (USD, USD-new и т.д.)
                if not base_currency:
                    base_currency = Currency.objects.get(code=base_code)
                quote_currency = Currency.objects.get(code=quote_code)
            except Currency.DoesNotExist:
                raise ValidationError(
                    f"Валюта {base_code} или {quote_code} не найдена")

            # Получаем балансы обеих валют
            base_balance, _ = CashBalance.objects.select_for_update().get_or_create(
                node=node,
                currency=base_currency,
                defaults={"balance": Decimal("0")}
            )

            quote_balance, _ = CashBalance.objects.select_for_update().get_or_create(
                node=node,
                currency=quote_currency,
                defaults={"balance": Decimal("0")}
            )

            if order.order_type == "buy":
                # Касса КУПИЛА quote (EUR): +amount, ОТДАЛА base (USD): -amount_base
                if base_balance.balance < amount_base:
                    raise ValidationError(
                        f"Недостаточно {base_currency.code} в кассе")

                quote_balance.balance += amount
                base_balance.balance -= amount_base

            elif order.order_type == "sell":
                # Касса ПРОДАЛА quote (EUR): -amount, ПОЛУЧИЛА base (USD): +amount_base
                if quote_balance.balance < amount:
                    raise ValidationError(f"Недостаточно {quote_code} в кассе")

                quote_balance.balance -= amount
                base_balance.balance += amount_base

            print(f'quote_balance  {quote_balance} {base_balance}')

            quote_balance.save()
            base_balance.save()

            # Комментарий к движению (используем существующий комментарий заказа, если есть)
            movement_comment = order.comment or (
                f"{order.get_order_type_display()} {order.amount_currency} {order.currency}"
                + (f" → {order.amount_base} {order.base_currency}" if order.base_currency else "")
            )

            # Логирование обеих операций
            CashMovement.objects.create(
                node=node,
                currency=quote_currency,
                movement_type=order.order_type,
                amount=amount,
                comment=movement_comment,
            )

            # Для кросс-курсов вторая валюта отражает противоположное движение:
            # - при покупке (buy) мы забираем базовую валюту → отображаем как sell
            # - при продаже (sell) мы выдаём базовую валюту → отображаем как buy
            base_movement_type = (
                "sell" if order.order_type == "buy" else
                "buy" if order.order_type == "sell" else
                order.order_type
            )

            CashMovement.objects.create(
                node=node,
                currency=base_currency,
                movement_type=base_movement_type,
                amount=amount_base,
                comment=movement_comment,
            )

        else:
            # ==========================================
            # ОБЫЧНЫЙ КУРС (с UAH)
            # ==========================================
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
                amount=amount,
                comment=movement_comment,
            )

    @staticmethod
    def validate_order(order, base_currency=None):

        node = order.shift.node
        currency = order.currency
        amount = order.amount_currency
        amount_base = order.amount_base or Decimal("0")

        is_cross_rate = '-' in (currency.code or '')

        if is_cross_rate:

            parts = currency.code.split('-')
            base_code = parts[0]
            quote_code = parts[1]

            if not base_currency:
                base_currency = Currency.objects.get(code=base_code)

            quote_currency = Currency.objects.get(code=quote_code)

            base_balance = CashBalance.objects.filter(
                node=node, currency=base_currency
            ).first()

            quote_balance = CashBalance.objects.filter(
                node=node, currency=quote_currency
            ).first()

            if order.order_type == "buy":
                if not base_balance or base_balance.balance < amount_base:
                    raise ValidationError(f"Недостаточно {base_currency.code}")

            elif order.order_type == "sell":
                if not quote_balance or quote_balance.balance < amount:
                    raise ValidationError(f"Недостаточно {quote_code}")
