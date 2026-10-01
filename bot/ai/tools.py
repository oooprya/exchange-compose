from loguru import logger
from services.exchange import exchange

TOOLS = [
    {
        "type": "function",
        "name": "get_rate",
        "description": (
            "Получить текущий курс указанной валюты "
            "по всем доступным обменникам."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "currency": {
                    "type": "string",
                    "description": (
                        "Код валюты. Например: EUR, USD, PLN."
                    )
                }
            },
            "required": ["currency"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_usd_rates",
        "description": (
            "Получить одновременно актуальный оптовый курс "
            "белого USD и синего USD. "
            "Используй, когда клиент спрашивает общий курс доллара "
            "без уточнения разновидности, например: "
            "'Какой курс $', 'курс доллара', 'доллар почём'."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "calculate_buy_for_uah",
        "description": (
            "Рассчитать, какое максимальное количество иностранной "
            "валюты клиент может получить за указанную сумму гривны. "
            "Используется, когда клиент указывает сумму в UAH, "
            "например: '750000 грн, сколько долларов я получу'. "
            "Для покупки валюты используется курс sell. "
            "Покупка USD и USDNEW округляется вниз до 100 единиц, "
            "другие валюты округляются вниз до целых единиц; "
            "результат также содержит сумму к оплате и сдачу. "
            "Всегда передавай raw_text без изменений, например '50к грн'."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "currency": {
                    "type": "string",
                    "description": "Валюта, которую клиент хочет купить. Например usd, usdnew, eur, gbp."
                },
                "uah_amount": {
                    "type": "number",
                    "description": "Сумма гривны, которую клиент хочет обменять."
                },
                "raw_text": {
                    "type": "string",
                    "description": "Исходная фраза клиента с суммой, например: 50к грн."
                }
            },
            "required": [
                "currency",
                "uah_amount",
                "raw_text"
            ],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "find_offer",
        "description": (
            "Найти обменник, где можно купить или продать "
            "указанную сумму валюты. "
            "Всегда вызывай функцию, если клиент указал сумму и валюту, "
            "даже если amount меньше 500: сервис сам нормализует сумму "
            "по raw_text и только потом проверяет минимальный опт. "
            "Для USD и USDNEW сумма округляется вниз до ближайших 100 "
            "единиц, потому что мелкие купюры не принимаются по оптовому курсу. "
            "Функция проверяет внутренний остаток валюты, "
            "но остаток никогда не показывается клиенту."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "currency": {
                    "type": "string",
                    "description": (
                        "Код валюты. Например: EUR, USD, PLN."
                    )
                },
                "amount": {
                    "type": "number",
                    "description": (
                        "Количество валюты."
                    )
                },
                "operation": {
                    "type": "string",
                    "enum": ["buy", "sell"],
                    "description": (
                        "sell — обменник продает валюту клиенту, "
                        "клиент покупает. "
                        "buy — обменник покупает валюту у клиента, "
                        "клиент продает."
                    )
                },
                "raw_text": {
                    "type": "string",
                    "description": (
                        "Исходная фраза клиента с суммой, например: "
                        "10 син или 15 тыс евро."
                    )
                }
            },
            "required": [
                "currency",
                "amount",
                "operation",
                "raw_text"
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "calculate_exchange",
        "description": (
                "Рассчитать общую сумму обмена для одной или нескольких валют. "
                "Используй, если клиент спрашивает, сколько гривен получится "
                "при продаже нескольких валют или сколько гривен нужно заплатить "
                "при покупке нескольких валют. "
                "Поддерживает несколько позиций одновременно, например: "
                "300 белых долларов + 200 синих долларов + 500 евро. "
                "Белый доллар = usd, синий доллар = usdnew. "
                "Для USD при оптовой покупке и продаже сумма округляется "
                "вниз до ближайших 100 единиц. "
                "При operation=buy, если есть USD или USDNEW, результат "
                "содержит обязательное поле warning: его нужно показать "
                "клиенту после расчета."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                    "items": {
                        "type": "array",
                        "description": "Список валют и количеств.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "currency": {
                                    "type": "string",
                                    "description": (
                                        "Код валюты из API. "
                                        "Например: usd, usdnew, eur, pln."
                                    )
                                },
                                "amount": {
                                    "type": "number",
                                    "description": "Количество валюты."
                                },
                                "raw_text": {
                                    "type": "string",
                                    "description": "Исходная фраза для этой суммы, например: 10 син."
                                }
                            },
                            "required": [
                                "currency",
                                "amount",
                                "raw_text"
                            ],
                            "additionalProperties": False
                        }
                    },
                "operation": {
                        "type": "string",
                        "enum": [
                            "buy",
                            "sell"
                        ],
                        "description": (
                            "sell — обменник продает валюту клиенту, "
                            "клиент покупает. "
                            "buy — обменник покупает валюту у клиента, "
                            "клиент продает."
                        )
                        }
            },
            "required": [
                "items",
                "operation"
            ],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "calculate_cross_exchange",
        "description": (
            "Рассчитать обмен двух валют по кросс-курсу. "
            "Всегда передавай raw_text без изменений."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "sell_currency": {
                    "type": "string",
                    "description": (
                        "Валюта, которую клиент отдает. "
                        "Например EUR."
                    ),
                },
                "buy_currency": {
                    "type": "string",
                    "description": (
                        "Валюта, которую клиент получает. "
                        "Например USD."
                    ),
                },
                "amount": {
                    "type": "number",
                    "description": (
                        "Сумма валюты, которую клиент отдает."
                    )
                },
                "raw_text": {
                    "type": "string",
                    "description": "Исходная фраза клиента с суммой, например: 10 син."
                }
            },
            "required": [
                "sell_currency",
                "buy_currency",
                "amount",
                "raw_text"
            ],
            "additionalProperties": False
        },
        "strict": True
    },

    {
        "type": "function",
        "name": "get_customer_data",
        "description": "Получить сохраненные данные клиента (имя и телефон) из БД",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },

    {
        "type": "function",
        "name": "create_order",
        "description": (
            "Создать бронь после подтверждения клиента."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "currency": {
                    "type": "string"
                },
                "amount": {
                    "type": "number"
                },
                "name": {
                    "type": "string"
                },
                "phone": {
                    "type": "string"
                },
                "address": {
                    "type": "string"
                },
                "rate": {
                    "type": "number"
                },
                "raw_text": {
                    "type": "string",
                    "description": "Исходная фраза клиента с суммой, например: 10 син."
                },
                "operation": {
                    "type": "string",
                    "enum": ["buy", "sell"]
                }
            },
            "required": [
                "currency",
                "amount",
                "name",
                "phone",
                "address",
                "rate",
                "raw_text",
                "operation"
            ],
            "additionalProperties": False,
        },
        "strict": True,
    },

]


async def execute_tool(
    name: str,
    arguments: dict,
    chat_id: str | None = None,
):

    if name == "get_rate":
        result = await exchange.get_rate(
            currency=arguments["currency"],
        )
        return result

    if name == "get_usd_rates":
        return await exchange.get_usd_rates()

    if name == "calculate_buy_for_uah":

        result = await exchange.calculate_buy_for_uah(
            currency=arguments["currency"],
            uah_amount=float(arguments["uah_amount"]),
            raw_text=arguments.get("raw_text", ""),
        )

        return result

    if name == "find_offer":

        result = await exchange.find_offer(
            currency=arguments["currency"],
            amount=arguments["amount"],
            operation=arguments["operation"],
            raw_text=arguments.get("raw_text", ""),
        )

        return result

    if name == "get_customer_data":

        if not chat_id:

            logger.warning(
                "get_customer_data: chat_id отсутствует"
            )

            return {
                "found": False,
                "error": "chat_id не передан",
            }

        result = await exchange.get_customer_data(
            chat_id=chat_id
        )
        return result

    if name == "calculate_exchange":

        result = await exchange.calculate_exchange(
            items=arguments["items"],
            operation=arguments["operation"],
        )
        return result

    if name == "calculate_cross_exchange":

        result = await exchange.calculate_cross_exchange(
            sell_currency=arguments["sell_currency"],
            buy_currency=arguments["buy_currency"],
            amount=float(arguments["amount"]),
            raw_text=arguments.get("raw_text", ""),
        )

        return result

    if name == "create_order":

        result = await exchange.create_order(

            currency=arguments["currency"],

            amount=arguments["amount"],

            name=arguments["name"],

            phone=arguments["phone"],

            address=arguments["address"],

            rate=arguments["rate"],

            operation=arguments["operation"],
            raw_text=arguments.get("raw_text", ""),
        )

        return result

    raise ValueError(
        f"Неизвестная функция: {name}"
    )
