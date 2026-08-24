#!/bin/bash
import asyncio
from pytz import timezone
from datetime import datetime
from functions.all_fun import update_course, parser_exchanger
import hashlib
from loguru import logger


@logger.catch
async def post_db():
    # Начальная инициализация
    previous_hash = None

    tz = timezone('Europe/Kiev')
    await update_course(parser_exchanger())

    while True:
        # Получаем текущее время
        now = datetime.now(tz)

        # Работаем только с 8:00 до 20:00
        if now.hour >= 8 and now.hour < 20:
            # Получаем данные и хеш
            data = parser_exchanger()

            # Вычисляем текущий хеш
            current_hash = hashlib.md5(
                f"{data}".encode('utf-8')).hexdigest()

            # Выполняем нужные действия
            logger.debug(
                f"Выполняем задачу в {now} {current_hash} {previous_hash}")

            # Сравниваем с предыдущим хешем
            if previous_hash is not None:
                if current_hash != previous_hash:
                    logger.info(f"Обновление курса! Новый хеш: {current_hash}")
                    await update_course(data)

            # Обновляем предыдущий хеш
            previous_hash = current_hash

            # Ждем 5 минут (300 секунд)
            await asyncio.sleep(300)
        else:
            # Вне рабочего времени — проверяем раз в минуту
            await asyncio.sleep(60)
