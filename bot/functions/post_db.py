#!/bin/bash
import asyncio
from pytz import timezone
from datetime import datetime
from functions.all_fun import update_course, parser_exchanger, minute_condition
import hashlib
from loguru import logger


all_currencys = [
    {
        "code": "usd",
        "name": "USD - Долар"
    },
    {
        "code": "usb",
        "name": "USD - Синій долар"
    },
    {
        "code": "eur",
        "name": "EUR - Евро"
    },

    {
        "code": "gbp",
        "name": "GBP - Фунт стерлингов"
    },
    {
        "code": "chf",
        "name": "CHF - Швейцарский франк"
    },
    {
        "code": "pln",
        "name": "PLN - Польский злотый"
    },
    {
        "code": "cad",
        "name": "CAD - Канадский доллар"
    },
    {
        "code": "ron",
        "name": "RON - Румынский лей"
    },
    {
        "code": "mdl",
        "name": "MDL - Молдавский лей"
    },
    {
        "code": "bgn",
        "name": "BGN - Болгарский лев"
    },
    {
        "code": "nok",
        "name": "NOK - Норвежская крона"
    },
    {
        "code": "czk",
        "name": "CZK - Чешская крона"
    },
    {
        "code": "cny",
        "name": "CNY - Китайский юань"
    },
    {
        "code": "try",
        "name": "TRY - Турецкая лира"
    },
    {
        "code": "sek",
        "name": "SEK - Шведская крона"
    },
    {
        "code": "dkk",
        "name": "DKK - Датская крона"
    },
    {
        "code": "ils",
        "name": "ILS - Израильский шекель"
    },
    {
        "code": "huf",
        "name": "HUF - Венгерский форинт"
    },
    {
        "code": "aed",
        "name": "AED - Дирхам ОАЭ"
    },
    {
        "code": "aud",
        "name": "AUD - Австралийский доллар"
    },
    {
        "code": "usd-eur",
        "name": "Долар - Евро"
    },
    {
        "code": "chf-usd",
        "name": "Швейцарский франк - Долар"
    },
    {
        "code": "gbp-usd",
        "name": "Фунт стерлингов - Долар"
    }
]

# for curr in all_currencys:
#     x = requests.post(f'{getenv("API")}/api/v1/currency/',
#                       json=curr, headers=headers)
#     logger.debug(f'{curr} - {x.status_code}')




@logger.catch
async def post_db():

    await update_course(parser_exchanger())
    # Хранение предыдущего хеша
    previous_hash = None

    while True:
        # Получаем текущее время
        now = datetime.now(timezone('Europe/Kiev'))
        # Список часов, в которые нужно отправлять сообщения
        logger.debug(now.strftime("%H:%M:%S"))

        # Проверяем, находится ли текущее время в пределах 8:00 - 21:00
        if now.hour >= 8 and now.hour < 21:
            # Выполняем нужные действия
            logger.debug("Выполняем задачу в", now.strftime("%H:%M:%S"))

            # Вычисляем текущий хеш
            current_hash = hashlib.md5(
                f"{parser_exchanger()}".encode('utf-8')).hexdigest()

            # Сравниваем с предыдущим хешем
            if previous_hash is not None:
                if current_hash != previous_hash:
                    logger.debug(f"Новые курсы! Новый хеш: {current_hash}")
                    await update_course(parser_exchanger())
                else:
                    logger.debug(f"Курсы не изменились. {previous_hash}")
                    if minute_condition:
                        await update_course(parser_exchanger())

            # Обновляем предыдущий хеш
            previous_hash = current_hash

            # Ждем 5 минут (300 секунд)
            await asyncio.sleep(300)
        else:
            # Если текущее время вне диапазона, ждем 1 минуту перед следующей проверкой
            await asyncio.sleep(60)