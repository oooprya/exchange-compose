import math
import re

from loguru import logger
from datetime import datetime, timedelta, timezone
from enum import Enum
from services.api import api

MIN_WHOLESALE_AMOUNT = 500


class Operation(str, Enum):
    BUY = "buy"
    SELL = "sell"


class ExchangeService:

    @staticmethod
    def normalize_cash_amount(
        amount: float,
        currency: str,
        operation: str = "buy",
    ) -> float:
        """Округляет USD до доступного оптового номинала 100."""
        currency = currency.lower().strip()

        if currency in ("usd", "usdnew"):
            return math.floor(amount / 100) * 100

        if operation.lower().strip() != Operation.BUY.value:
            return amount

        return math.floor(amount)

    def __init__(self):
        self._currencies = {}
        self._updated = None

    def normalize_amount(
        self,
        amount: float,
        raw_text: str = "",
        currency: str = "",
    ) -> float:
        """
        Нормализует разговорные суммы клиентов.

        Небольшие суммы с маркерами USD считаются тысячами:
        "10 син" -> 10000 USDNEW, "10 бел" -> 10000 USD.
        Явные обозначения тысяч работают для любой валюты.
        """

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return 0

        if amount <= 0:
            return amount

        text = (raw_text or "").lower().strip()
        currency = (currency or "").lower().strip()

        if re.search(
            r"(?<![а-яё])(?:к\.?|тыс\.?|тысяч(?:а|и)?)(?![а-яё])",
            text,
        ):
            number_match = re.search(
                r"(?<![\d.,])(\d+(?:[.,]\d+)?)\s*"
                r"(?:к\.?|тыс\.?|тысяч(?:а|и)?)(?![а-яё])",
                text,
            )

            if number_match:
                written_amount = float(
                    number_match.group(1).replace(",", ".")
                ) * 1000

                # The model may already expand "10к" to 10000.
                if amount == written_amount:
                    return amount

            return amount * 1000

        if currency in ("usd", "usdnew") and 1 <= amount <= 20:
            usd_markers = (
                "$",
                "дол",
                "доллар",
                "доллара",
                "долларов",
                "бакс",
                "баксов",
                "бел",
                "белый",
                "белые",
                "син",
                "синий",
                "синие",
            )

            if any(marker in text for marker in usd_markers):
                return amount * 1000

        return amount

    async def load_currencies(self):

        if (
            self._updated
            and datetime.now(timezone.utc) - self._updated
            < timedelta(hours=1)
        ):
            return

        data = await api.get(
            "/currency/",
            params={
                "limit": 100
            }
        )

        self._currencies.clear()

        for item in data.get("objects", []):

            code = item.get("code")

            if not code:
                continue

            self._currencies[code.lower()] = {
                "id": item["id"],
                "code": code.lower(),
                "name": item["name"],
            }

        self._updated = datetime.now(timezone.utc)

    async def get_currency(self, code: str):

        await self.load_currencies()

        if not code:
            return None

        return self._currencies.get(
            code.lower().strip()
        )

    CURRENCY_ALIASES = {
        # USD - Білий
        "белый": "usd",
        "бел": "usd",
        "белые": "usd",
        "б": "usd",
        "старый": "usd",
        "старые": "usd",
        "старый доллар": "usd",
        "старые доллары": "usd",

        # USD - Новий
        "синий": "usdnew",
        "син": "usdnew",
        "синие": "usdnew",
        "синих": "usdnew",
        "синих долларов": "usdnew",
        "с": "usdnew",
        "новый": "usdnew",
        "новые": "usdnew",
        "новый доллар": "usdnew",
        "новые доллары": "usdnew",


        # другие валюты
        "евро": "eur",
        "евро": "eur",
        "лей": "ron",
        "рум лей": "ron",
        "румынские леи": "ron",
        "злотый": "pln",
        "злотые": "pln",
        "синии": "usdnew",
        "фунты": "gbp",
    }

    async def get_usd_rates(self):
        """
        Получить одновременно курс белого и синего доллара.

        usd    = белый доллар
        usdnew = синий / новый доллар
        """

        white = await self.get_rate("usd")
        blue = await self.get_rate("usdnew")

        if not white.get("found") or not blue.get("found"):
            return {
                "found": False,
                "error": "Не удалось получить оба курса USD.",
                "white_found": white.get("found", False),
                "blue_found": blue.get("found", False),
            }

        return {
            "found": True,

            "white": {
                "currency": "USD",
                "type": "white",
                "name": white.get("currency_name"),
                "buy": white.get("buy"),
                "sell": white.get("sell"),
            },

            "blue": {
                "currency": "USDNEW",
                "type": "blue",
                "name": blue.get("currency_name"),
                "buy": blue.get("buy"),
                "sell": blue.get("sell"),
            },
        }

    async def resolve_currency(self, value: str):

        if not value:
            logger.warning("resolve_currency: пустое значение")
            return None

        original = value
        value = value.strip().lower()

        logger.info(
            f"resolve_currency: получено '{original}', normalized='{value}'"
        )

        # Прямой API code
        currency = await self.get_currency(value)

        if currency:
            logger.info(
                f"resolve_currency: '{value}' → "
                f"{currency['code']} / id={currency['id']} / "
                f"{currency['name']}"
            )
            return currency

        # Alias
        api_code = self.CURRENCY_ALIASES.get(value)

        if not api_code:
            logger.warning(
                f"resolve_currency: неизвестная валюта '{original}'"
            )
            return None

        logger.info(
            f"resolve_currency: alias '{original}' → '{api_code}'"
        )

        currency = await self.get_currency(api_code)

        if currency:
            logger.info(
                f"resolve_currency: найдено → "
                f"{currency['code']} / id={currency['id']} / "
                f"{currency['name']}"
            )
        else:
            logger.error(
                f"resolve_currency: API code '{api_code}' "
                f"не найден в currencies"
            )

        return currency

    # =========================================================
    # GET RATE
    # =========================================================

    async def get_rate(self, currency):
        currency_info = await self.resolve_currency(currency)

        if not currency_info:
            return {
                "found": False,
                "error": f"Неизвестная валюта: {currency}"
            }

        currency_id = currency_info["id"]

        response = await api.get(
            "/currencys/",
            params={"currency": currency_id}
        )

        if not response:
            return {
                "found": False,
                "error": "Курс не найден"
            }

        locations = []

        objects = response.get("objects", []) if isinstance(
            response, dict) else response

        for item in objects:
            buy = item.get("buy")
            sell = item.get("sell")

            if buy is None or sell is None:
                continue

            try:
                locations.append({
                    "address": item.get("address"),
                    "address_map": item.get("address_map"),
                    "working_hours": item.get("working_hours"),
                    "buy": float(buy),
                    "sell": float(sell),
                })
            except (TypeError, ValueError):
                continue

        if not locations:
            return {
                "found": False,
                "error": "Нет доступных курсов"
            }

        return {
            "found": True,
            "currency": currency_info["code"].upper(),
            "currency_name": currency_info["name"],
            "buy": max(item["buy"] for item in locations),
            "sell": min(item["sell"] for item in locations),
            "locations": locations,
        }

    async def calculate_exchange(
        self,
        items: list,
        operation: str
    ):
        """
        Универсальный расчет нескольких валют.

        items:

        [
            {
                "currency": "usd",
                "amount": 300
            },
            {
                "currency": "usdnew",
                "amount": 200
            },
            {
                "currency": "eur",
                "amount": 500
            }
        ]

        operation:

        buy
        sell

        balance никогда не возвращается.
        """

        if not items:
            return {
                "success": False,
                "error": "Не указаны валюты."
            }

        if operation not in ("buy", "sell"):
            return {
                "success": False,
                "error": "Неизвестная операция."
            }

        positions = []

        total_uah = 0
        has_usd_sale = operation == "buy" and any(
            (item.get("currency") or "").lower().strip()
            in ("usd", "usdnew")
            for item in items
        )

        for item in items:

            currency = item.get("currency")
            amount = float(item.get("amount", 0))
            amount = self.normalize_amount(
                amount=amount,
                raw_text=item.get("raw_text", ""),
                currency=currency or "",
            )

            amount = self.normalize_cash_amount(
                amount=amount,
                currency=currency or "",
                operation=operation,
            )

            if not currency:
                continue

            if amount <= 0:
                continue

            # --------------------------------
            # Определяем реальную валюту
            # --------------------------------

            currency_info = await self.resolve_currency(
                currency
            )

            if currency_info is None:

                return {
                    "success": False,
                    "error": (
                        f"Неизвестная валюта: {currency}"
                    )
                }

            real_code = currency_info["code"]

            # --------------------------------
            # Получаем курс
            # --------------------------------

            rate_data = await self.get_rate(
                real_code
            )

            if not rate_data.get("found"):

                return {
                    "success": False,
                    "error": (
                        f"Не удалось получить курс "
                        f"{currency_info['name']}"
                    )
                }

            # --------------------------------
            # Выбираем правильный курс
            # --------------------------------

            if operation == "sell":

                rate = rate_data.get("sell")

            else:

                rate = rate_data.get("buy")

            if rate is None:

                return {
                    "success": False,
                    "error": (
                        f"Нет курса для "
                        f"{currency_info['name']}"
                    )
                }

            rate = float(rate)

            # --------------------------------
            # Расчёт
            # --------------------------------

            uah = amount * rate

            total_uah += uah

            positions.append({
                "currency": real_code,
                "currency_name": currency_info["name"],
                "amount": amount,
                "rate": rate,
                "uah": round(uah, 2),
            })

        if not positions:

            return {
                "success": False,
                "error": "Не удалось определить валюты."
            }

        result = {
            "success": True,
            "operation": operation,
            "positions": positions,
            "total_uah": round(total_uah, 2),
        }

        if has_usd_sale:
            result["warning"] = (
                "⚠️ <b>Увага:</b> на купюри номіналом 1, 2, 5, 10, 20, 50 $, "
                "а також 1996 та 1999 р., з пошкодженнями "
                "(підписи, печаті, надірвані) оптовий курс не діє."
            )

        return result

    async def calculate_buy_for_uah(
        self,
        currency: str,
        uah_amount: float,
        raw_text: str = "",
    ):
        """
        Покупка иностранной валюты за гривну.

        Клиент указывает сумму UAH.
        Функция определяет, сколько валюты клиент получит.

        Минимальный опт:
            500 единиц иностранной валюты.

        Минимальная сумма UAH:
            500 * sell_rate
        """

        uah_amount = self.normalize_amount(
            amount=uah_amount,
            raw_text=raw_text,
            currency="uah",
        )

        if uah_amount <= 0:
            return {
                "success": False,
                "error": "Сумма гривны должна быть больше 0.",
            }

        # =========================================
        # Определяем валюту
        # =========================================

        currency_info = await self.resolve_currency(currency)

        if currency_info is None:
            return {
                "success": False,
                "error": f"Неизвестная валюта: {currency}",
            }

        # =========================================
        # Получаем кассы
        # =========================================

        data = await api.get(
            "/currencys/",
            params={
                "currency": currency_info["id"]
            }
        )

        objects = data.get("objects", [])

        if not objects:
            return {
                "success": False,
                "error": "Нет данных по этой валюте.",
            }

        offers = []

        for item in objects:

            # -------------------------------------
            # Курс продажи валюты клиенту
            # -------------------------------------

            try:
                sell_rate = float(item["sell"])
            except (TypeError, ValueError, KeyError):
                continue

            if sell_rate <= 0:
                continue

            # -------------------------------------
            # Минимальная сумма гривны
            # -------------------------------------

            minimum_uah = MIN_WHOLESALE_AMOUNT * sell_rate

            # -------------------------------------
            # Проверяем минимальный опт
            # -------------------------------------

            if uah_amount < minimum_uah:
                continue

            # -------------------------------------
            # Сколько валюты получит клиент
            # -------------------------------------

            currency_amount = self.normalize_cash_amount(
                amount=uah_amount / sell_rate,
                currency=currency_info["code"],
            )

            if currency_amount < MIN_WHOLESALE_AMOUNT:
                continue

            uah_to_pay = round(currency_amount * sell_rate, 2)
            uah_change = round(uah_amount - uah_to_pay, 2)

            # -------------------------------------
            # Проверяем остаток валюты
            # -------------------------------------

            try:
                balance = float(item.get("balance") or 0)
            except (TypeError, ValueError):
                balance = 0

            if balance < currency_amount:
                continue

            offers.append({
                "address": item.get("address"),
                "address_map": item.get("address_map"),
                "working_hours": item.get("working_hours"),

                "currency": item.get("code"),
                "currency_name": item.get(
                    "currency_name",
                    currency_info["name"]
                ),

                "uah_amount": round(uah_amount, 2),

                "currency_amount": currency_amount,

                "uah_to_pay": uah_to_pay,

                "uah_change": uah_change,

                "rate": sell_rate,

                "minimum_currency_amount": MIN_WHOLESALE_AMOUNT,

                "minimum_uah_amount": round(
                    minimum_uah,
                    2
                ),
            })

        # =========================================
        # Нет подходящей кассы
        # =========================================

        if not offers:

            # Получаем минимальный UAH по лучшему доступному курсу
            rates = []

            for item in objects:

                try:
                    sell_rate = float(item["sell"])
                except (TypeError, ValueError, KeyError):
                    continue

                if sell_rate > 0:
                    rates.append(sell_rate)

            if rates:

                best_rate = min(rates)

                minimum_uah = (
                    MIN_WHOLESALE_AMOUNT * best_rate
                )

                return {
                    "success": False,

                    "error": "minimum_amount",

                    "currency": currency_info["code"].upper(),

                    "currency_name": currency_info["name"],

                    "requested_uah": round(
                        uah_amount,
                        2
                    ),

                    "minimum_currency_amount": (
                        MIN_WHOLESALE_AMOUNT
                    ),

                    "minimum_uah_amount": round(
                        minimum_uah,
                        2
                    ),
                }

            return {
                "success": False,
                "error": "Нет доступных курсов.",
            }

        # =========================================
        # Выбираем лучший вариант
        # =========================================

        # Для одинаковой суммы UAH лучший курс =
        # минимальный sell → больше валюты клиенту.

        offers.sort(
            key=lambda x: x["currency_amount"],
            reverse=True
        )

        best = offers[0]

        return {
            "success": True,

            "operation": "buy",

            "currency": currency_info["code"].upper(),

            "currency_name": currency_info["name"],

            "uah_amount": round(
                uah_amount,
                2
            ),

            "currency_amount": best[
                "currency_amount"
            ],

            "uah_to_pay": best["uah_to_pay"],

            "uah_change": best["uah_change"],

            "rate": best["rate"],

            "minimum_currency_amount": (
                MIN_WHOLESALE_AMOUNT
            ),

            "minimum_uah_amount": best[
                "minimum_uah_amount"
            ],

            "address": best["address"],

            "address_map": best["address_map"],

            "working_hours": best[
                "working_hours"
            ],

            "offers": offers,
        }

    # =========================================================
    # FIND OFFER
    # =========================================================

    async def find_offer(
        self,
        currency: str,
        amount: float,
        operation: str,
        raw_text: str = "",
    ):
        """
        Найти обменники, где можно выполнить операцию.

        SELL:
            Обменник продаёт валюту клиенту.
            Проверяем balance >= amount.

        BUY:
            Обменник покупает валюту у клиента.
            Проверяем total_uah >= amount * buy_rate.

        balance и total_uah используются только внутри.
        Клиенту они никогда не возвращаются.
        """

        # =====================================================
        # 1. Проверяем operation
        # =====================================================

        operation = operation.lower().strip()

        if operation not in ("buy", "sell"):
            return {
                "found": False,
                "count": 0,
                "offers": [],
                "error": "Неизвестный тип операции",
            }

        # =====================================================
        # 2. Проверяем сумму
        # =====================================================

        try:
            amount = float(amount)
        except (TypeError, ValueError):

            return {
                "found": False,
                "count": 0,
                "offers": [],
                "error": "Некорректная сумма",
            }

        amount = self.normalize_amount(
            amount=amount,
            raw_text=raw_text,
            currency=currency,
        )

        amount = self.normalize_cash_amount(
            amount=amount,
            currency=currency,
            operation=operation,
        )

        if amount <= 0:

            return {
                "found": False,
                "count": 0,
                "offers": [],
                "error": "Сумма должна быть больше нуля",
            }

        # =====================================================
        # 3. Минимальный опт
        # =====================================================

        if amount < MIN_WHOLESALE_AMOUNT:

            return {
                "found": False,
                "count": 0,
                "offers": [],
                "error": "minimum_amount",
                "minimum_amount": MIN_WHOLESALE_AMOUNT,
                "requested_amount": amount,
            }

        # =====================================================
        # 4. Определяем валюту
        # =====================================================

        currency_info = await self.resolve_currency(currency)

        if currency_info is None:

            return {
                "found": False,
                "count": 0,
                "currency": currency,
                "amount": amount,
                "operation": operation,
                "offers": [],
                "error": f"Неизвестная валюта: {currency}",
            }

        # =====================================================
        # 5. Получаем точки
        # =====================================================

        data = await api.get(
            "/currencys/",
            params={
                "currency": currency_info["id"]
            }
        )

        objects = data.get("objects", [])

        if not objects:

            return {
                "found": False,
                "count": 0,
                "currency": currency_info["code"],
                "currency_name": currency_info["name"],
                "amount": amount,
                "operation": operation,
                "offers": [],
                "error": "Нет данных по этой валюте",
            }

        # =====================================================
        # 6. Ищем подходящие обменники
        # =====================================================

        offers = []

        for item in objects:

            # -------------------------------------------------
            # Курс покупки
            # -------------------------------------------------

            try:
                buy = float(item.get("buy"))
            except (TypeError, ValueError):
                buy = None

            # -------------------------------------------------
            # Курс продажи
            # -------------------------------------------------

            try:
                sell = float(item.get("sell"))
            except (TypeError, ValueError):
                sell = None

            # -------------------------------------------------
            # Остаток валюты
            # -------------------------------------------------

            try:
                balance = float(item.get("balance") or 0)
            except (TypeError, ValueError):
                balance = 0

            # -------------------------------------------------
            # Баланс гривны
            # -------------------------------------------------

            try:
                total_uah = float(item.get("total_uah") or 0)
            except (TypeError, ValueError):
                total_uah = 0


            if operation == "sell":

                # Обменник продаёт валюту клиенту.
                #
                # Обменник должен иметь нужное количество
                # иностранной валюты.

                if sell is None:
                    continue

                if balance < amount:
                    continue

                rate = sell

                uah_required = round(
                    amount * rate,
                    2
                )

            else:

                # Обменник покупает валюту у клиента.
                #
                # Обменник должен иметь достаточно гривны,
                # чтобы рассчитаться с клиентом.

                if buy is None:
                    continue

                uah_required = round(
                    amount * buy,
                    2
                )

                if total_uah < uah_required:
                    continue

                rate = buy

            # =================================================
            # Добавляем предложение
            # =================================================

            offers.append({
                "address": item.get("address"),
                "address_map": item.get("address_map"),
                "working_hours": item.get("working_hours"),

                "currency": item.get("code"),
                "currency_name": item.get(
                    "currency_name",
                    currency_info["name"]
                ),

                "amount": amount,

                "operation": operation,

                "rate": rate,

                "buy": buy,
                "sell": sell,

                # Для клиента полезно знать,
                # сколько гривен нужно/получит.
                "uah_total": uah_required,
            })

        # =====================================================
        # 7. Нет подходящих обменников
        # =====================================================

        if not offers:

            return {
                "found": False,
                "count": 0,

                "currency": currency_info["code"],
                "currency_name": currency_info["name"],

                "amount": amount,
                "operation": operation,

                "offers": [],

                "error": (
                    "Нет обменников, где можно выполнить "
                    "операцию на указанную сумму."
                ),
            }

        # =====================================================
        # 8. Возвращаем предложения
        # =====================================================

        return {
            "found": True,

            "currency": currency_info["code"],
            "currency_name": currency_info["name"],

            "amount": amount,
            "operation": operation,

            "count": len(offers),
            "offers": offers,
        }

    async def calculate_cross_exchange(
        self,
        sell_currency: str,
        buy_currency: str,
        amount: float,
        raw_text: str = "",
    ):
        """
        Кросс-обмен.

        sell_currency:
            валюта, которую клиент отдаёт.

        buy_currency:
            валюта, которую клиент получает.

        amount:
            сумма валюты, которую клиент отдаёт.
        """

        amount = self.normalize_amount(
            amount=amount,
            raw_text=raw_text,
            currency=sell_currency,
        )

        if amount < MIN_WHOLESALE_AMOUNT:
            return {
                "success": False,
                "error": "Сумма должна быть больше 0.",
            }

        sell_info = await self.resolve_currency(sell_currency)
        buy_info = await self.resolve_currency(buy_currency)

        if not sell_info:
            return {
                "success": False,
                "error": f"Неизвестная валюта: {sell_currency}",
            }

        if not buy_info:
            return {
                "success": False,
                "error": f"Неизвестная валюта: {buy_currency}",
            }

        sell_code = sell_info["code"].lower()
        buy_code = buy_info["code"].lower()

        # =========================================
        # Ищем прямой кросс
        # =========================================

        # Кроссовые записи используют общий код USD. Версия доллара
        # (usd или usdnew) выбирается отдельно через base_currency.
        sell_cross_code = "usd" if sell_code == "usdnew" else sell_code
        buy_cross_code = "usd" if buy_code == "usdnew" else buy_code

        direct_code = f"{sell_cross_code}-{buy_cross_code}"
        reverse_code = f"{buy_cross_code}-{sell_cross_code}"

        data = await api.get(
            "/currencys/",
            params={
                "limit": 100,
            }
        )

        objects = data.get("objects", [])

        direct = None
        reverse = None

        for item in objects:

            code = (item.get("code") or "").lower()

            if code == direct_code:
                direct = item

            elif code == reverse_code:
                reverse = item

        # =========================================
        # Вариант 1
        # Есть прямой кросс
        # =========================================

        if direct:

            try:
                buy_rate = float(direct["buy"])
                sell_rate = float(direct["sell"])
            except (TypeError, ValueError, KeyError):

                return {
                    "success": False,
                    "error": f"Некорректный курс {direct_code}",
                }

            # EUR 1000 * Вы отримуйте 1 161

            buy_amount = amount * buy_rate
            logger.info(
                f"EUR 1000 * Вы отримуйте 1 161 amount '{amount}' buy_rate '{buy_rate}'")

            return {
                "success": True,

                "sell_currency": sell_code.upper(),
                "sell_currency_name": sell_info["name"],

                "buy_currency": buy_code.upper(),
                "buy_currency_name": buy_info["name"],

                "sell_amount": round(amount, 2),
                "buy_amount": round(buy_amount, 2),

                "cross_rate": sell_rate,

                "cross_code": direct_code,

                "buy_rate": buy_rate,
                "sell_rate": sell_rate,

                "address": direct.get("address"),
                "address_map": direct.get("address_map"),
                "working_hours": direct.get("working_hours"),
            }

        # =========================================
        # Вариант 2
        # Есть обратный кросс
        # =========================================

        if reverse:

            try:
                buy_rate = float(reverse["buy"])
                sell_rate = float(reverse["sell"])
            except (TypeError, ValueError, KeyError):

                return {
                    "success": False,
                    "error": f"Некорректный курс {reverse_code}",
                }

            # Например API имеет:
            #
            # EUR 1000 / Ви віддаєте 1 164
            #

            buy_amount = amount * sell_rate

            logger.info(
                f"EUR 1000 * Ви віддаєте 1 164 amount '{amount}' buy_rate '{sell_rate}'")

            cross_rate = sell_rate

            return {
                "success": True,

                "sell_currency": sell_code.upper(),
                "sell_currency_name": sell_info["name"],

                "buy_currency": buy_code.upper(),
                "buy_currency_name": buy_info["name"],

                "sell_amount": round(amount, 2),
                "buy_amount": round(buy_amount, 2),

                "cross_rate": round(cross_rate, 6),

                "cross_code": reverse_code,

                "buy_rate": buy_rate,
                "sell_rate": sell_rate,

                "address": reverse.get("address"),
                "address_map": reverse.get("address_map"),
                "working_hours": reverse.get("working_hours"),
            }

        # =========================================
        # Кросса нет
        # =========================================

        return {
            "success": False,

            "sell_currency": sell_code.upper(),
            "buy_currency": buy_code.upper(),

            "error": (
                f"Кросс {sell_code.upper()}/{buy_code.upper()} "
                f"не найден в API."
            ),
        }

    # =========================================================
    # CREATE ORDER
    # =========================================================

    async def create_order(
        self,
        currency: str,
        amount: float,
        name: str,
        phone: str,
        address: str,
        rate: float,
        operation: str = "sell",
        raw_text: str = "",
    ):
        """
        Создание заказа через существующий Django API.
        """

        if not isinstance(address, str) or not address.strip():
            return {
                "success": False,
                "error": "Для брони необходимо выбрать адрес обменника.",
            }

        amount = self.normalize_amount(
            amount=amount,
            raw_text=raw_text,
            currency=currency,
        )

        amount = self.normalize_cash_amount(
            amount=amount,
            currency=currency,
            operation=operation,
        )

        currency_info = await self.resolve_currency(
            currency
        )

        if currency_info is None:

            return {
                "success": False,
                "error": f"Неизвестная валюта: {currency}"
            }

        if operation.lower().strip() == Operation.SELL.value:
            # Обменник продает валюту клиенту.
            buy_or_sell = "Продаж"
        else:
            # Обменник покупает валюту у клиента.
            buy_or_sell = "Купівля"

        payload = {
            "address_exchanger": address,

            "buy_or_sell": buy_or_sell,

            "currency_name": currency_info["name"],

            "exchange_rate": str(rate),

            "order_sum": amount,

            "clients_telephone": phone,
        }

        data = await api.post(
            "/orders/",
            payload
        )

        return {
            "success": True,

            "order_id": data.get("id"),

            "address": address,

            "currency": currency_info["code"].upper(),

            "currency_name": currency_info["name"],

            "amount": amount,

            "rate": rate,
        }

    # =========================================================
    # CANCEL ORDER
    # =========================================================

    async def cancel_order(self, order_id: int):

        data = await api.patch(
            f"/orders/{order_id}/",
            {
                "status": "cancel"
            }
        )

        return {
            "success": True,
            "order_id": order_id,
            "data": data,
        }

    # =========================================================
    # ORDER STATUS
    # =========================================================

    async def order_status(self, order_id: int):

        return await api.get(
            f"/orders/{order_id}/"
        )


exchange = ExchangeService()


# =============================================================
# WRAPPER FOR TOOL CALLING
# =============================================================


async def get_rate(currency: str):

    return await exchange.get_rate(currency)


async def get_usd_rates():
    return await exchange.get_usd_rates()


async def create_order(
    currency: str,
    amount: float,
    name: str,
    phone: str,
    address: str,
    rate: float,
    operation: str = "sell",
    raw_text: str = "",
):

    return await exchange.create_order(
        currency=currency,
        amount=amount,
        name=name,
        phone=phone,
        address=address,
        rate=rate,
        operation=operation,
        raw_text=raw_text,
    )
