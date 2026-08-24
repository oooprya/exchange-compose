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
        "name": "find_offer",
        "description": (
            "Найти обменник, где можно купить или продать "
            "указанную сумму валюты. "
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
                        "buy — клиент хочет купить валюту. "
                        "sell — клиент хочет продать валюту."
                    )
                }
            },
            "required": [
                "currency",
                "amount",
                "operation"
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
                "Белый доллар = usd, синий доллар = usdnew."
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
                                }
                            },
                            "required": [
                                "currency",
                                "amount"
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
                            "buy — клиент покупает валюту у обменника. "
                            "sell — клиент продает валюту обменнику."
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
            "Рассчитать обмен двух валют по кросс-курсу."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "sell_currency": {
                    "type": "string",
                    "description": (
                        "Валюта, которую клиент отдаёт обменнику."
                    )
                },
                "buy_currency": {
                    "type": "string",
                    "description": (
                        "Валюта, которую клиент получает."
                    )
                },
                "amount": {
                    "type": "number",
                    "description": (
                        "Количество валюты, которую клиент хочет получить."
                    )
                }
            },
            "required": [
                "sell_currency",
                "buy_currency",
                "amount"
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

    logger.info(
        "Executing tool: {} | arguments={} | chat_id={}",
        name,
        arguments,
        chat_id,
    )

    # ==========================================================
    # GET RATE
    # ==========================================================

    if name == "get_rate":

        result = await exchange.get_rate(
            arguments["currency"]
        )

        logger.info(
            "get_rate result: {}",
            result,
        )

        return result

    # ==========================================================
    # FIND OFFER
    # ==========================================================

    if name == "find_offer":

        result = await exchange.find_offer(
            currency=arguments["currency"],
            amount=arguments["amount"],
            operation=arguments["operation"],
        )

        logger.info(
            "find_offer result: {}",
            result,
        )

        return result

    # ==========================================================
    # CUSTOMER DATA
    # ==========================================================

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

        logger.info(
            "get_customer_data result: {}",
            result,
        )

        return result

    # ==========================================================
    # CALCULATE EXCHANGE
    # ==========================================================

    if name == "calculate_exchange":

        result = await exchange.calculate_exchange(
            items=arguments["items"],
            operation=arguments["operation"],
        )

        logger.info(
            "calculate_exchange result: {}",
            result,
        )

        return result

    # ==========================================================
    # CREATE ORDER
    # ==========================================================

    if name == "create_order":

        result = await exchange.create_order(

            currency=arguments["currency"],

            amount=arguments["amount"],

            name=arguments["name"],

            phone=arguments["phone"],

            address=arguments["address"],

            rate=arguments["rate"],

            operation=arguments["operation"],
        )

        logger.info(
            "create_order result: {}",
            result,
        )

        return result

    # ==========================================================
    # UNKNOWN TOOL
    # ==========================================================

    raise ValueError(
        f"Неизвестная функция: {name}"
    )
