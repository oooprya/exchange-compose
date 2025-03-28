#!/bin/bash
import asyncio
import requests
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from os import getenv
from pytz import timezone
from aiogram import Bot
from aiogram.enums import ParseMode
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import hashlib
import time
import json
from loguru import logger

url_currencys = f'{getenv("API")}/api/v1/currencys/?limit=100'
url_gold = getenv("URL_GOLD")

logger.info(getenv("API"))

headers = {"Authorization": f"ApiKey {getenv('API_KEY')}"}

# logger.add("post_db.log", colorize=True,
#            format="{time:YYYY-MM-DD HH:mm:ss} {name} {line} {level} {message} ", level="DEBUG", rotation="500 KB", compression="zip")


# data_id = 1
# for exchanger in exchangers:
#     x = requests.post(f'{getenv("API")}/api/v1/exchangers/',
#                       json=exchanger, headers=headers)
#     print(f'{data_id} Добавить Обмінник:  {x.status_code}')
#     data_id += 1


# def add_exchanger(data_id, exchanger_location, exchanger_address_map, exchanger_working_hours):
#     exchanger_post = dict(id=data_id,
#                           address=exchanger_location,
#                           address_map=exchanger_address_map,
#                           working_hours=exchanger_working_hours)

#     x = requests.post(f'{getenv("API")}/v1/exchangers/', json = exchanger_post, headers = headers)
#     print(f'{data_id} Добавить Обмінник: {exchanger_location} : {exchanger_post} {x.status_code}')









@logger.catch
async def send_currency(new_text):
    bot = Bot(token=getenv("TOKEN"), default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))
    async with bot.session:  # or `bot.context()`
        # await bot.send_message(chat_id=getenv("Admin"),  text=new_text)
        main_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
        InlineKeyboardButton(text = "💰 Забронювати на сайті",
                             url=f'{getenv("API")}',
                             callback_data="event")
        ]
        ],)


        await bot.send_message(chat_id='-1002443613215',  text=new_text, reply_markup=main_kb )

@logger.catch
def edit_currency(url, new_json) -> None:
    now_time = time.monotonic()
    x = requests.patch(url, json=new_json, headers=headers)
    logger.debug(f"{new_json} {x.status_code}")
    logger.debug(f'Прошло времени {time.monotonic() - now_time }')

@logger.catch
def get_data(url, teg: str, parser_class: str):
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
    r = s.get(url)
    bs = BeautifulSoup(r.text, 'html.parser')
    res = bs.find(teg, class_=parser_class).text
    return res

@logger.catch
def parser_exchanger():
    """ Парсим нужный обменик """
    url = getenv("PARSER_EXCHANGER")

    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
    r = s.get(url)
    bs = BeautifulSoup(r.text, 'html.parser')
    exchangers = bs.find('script', id='__NEXT_DATA__').text
    data = json.loads(exchangers)

    data_pars = data["props"]['initialState']['operations']['operation']['branchRates']
    new_data_pars = []
    count = 1
    for curr in data_pars:
        add_curr = dict(id=count, currency=curr['currency'],
                        buy=str(curr['rate']['buy']['value']).replace(',', '.'),
                        sell=str(curr['rate']['sell']['value']).replace(',', '.'))
        new_data_pars.append(add_curr)
        count += 1

    return new_data_pars


@logger.catch
def add_course():
    """Добавляем курс на сайт"""
    data_api = get_api_data(f'{getenv("API")}/api/v1/currency?limit=50')
    total_count = get_api_data(f'{getenv("API")}/api/v1/exchangers/')

    exchanger_id = 1
    currency_id = 1
    for curr in range(total_count["meta"]["total_count"]):

        for curr in parser_exchanger():
            for curr_api in data_api["objects"]:

                if curr['currency'] == curr_api['code']:
                    currency = {
                        "buy": curr['buy'],
                        "currency": f"/api/v1/currency/{curr_api['id']}/",
                        "exchanger": f"/api/v1/exchangers/{exchanger_id}/",
                        "sell": curr['sell'],
                        "sum": 100000
                    }
                    x = requests.post(f'{getenv("API")}/api/v1/currencys/',
                                      json=currency,
                                      headers=headers)
                    logger.debug(x.status_code)
                    logger.debug(
                        f"exchanger_id {exchanger_id } {curr_api['id']} {curr_api['code']} buy {curr['buy']}  sell {curr['sell']}")
            currency_id += 1
            logger.debug(curr['currency'])
        exchanger_id += 1

@logger.catch
def get_api_data(api_url):
    """Функция для получения данных из API"""
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()  # Предполагаем, что ответ в формате JSON
    else:
        logger.error("Ошибка при получении данных из API")
        return {}

@logger.catch
def add_all_currency() -> bool:
    all_currencys = [ { "code": "usd", "name": "USD - Долар" }, { "code": "usb", "name": "USD - Синій долар" }, { "code": "eur", "name": "EUR - Евро" }, { "code": "gbp", "name": "GBP - Фунт стерлингов" }, { "code": "chf", "name": "CHF - Швейцарский франк" }, { "code": "pln", "name": "PLN - Польский злотый" }, { "code": "cad", "name": "CAD - Канадский доллар" }, { "code": "ron", "name": "RON - Румынский лей" }, { "code": "mdl", "name": "MDL - Молдавский лей" }, { "code": "bgn", "name": "BGN - Болгарский лев" }, { "code": "nok", "name": "NOK - Норвежская крона" }, { "code": "czk", "name": "CZK - Чешская крона" }, { "code": "cny", "name": "CNY - Китайский юань" }, { "code": "try", "name": "TRY - Турецкая лира" }, { "code": "sek", "name": "SEK - Шведская крона" }, { "code": "dkk", "name": "DKK - Датская крона" }, { "code": "ils", "name": "ILS - Израильский шекель" }, { "code": "huf", "name": "HUF - Венгерский форинт" }, { "code": "aed", "name": "AED - Дирхам ОАЭ" }, { "code": "aud", "name": "AUD - Австралийский доллар" }, { "code": "usd-eur", "name": "Долар - Евро" }, { "code": "chf-usd", "name": "Швейцарский франк - Долар" }, { "code": "gbp-usd", "name": "Фунт стерлингов - Долар" } ]
    try:
        currency_data = get_api_data(f'{getenv("API")}/api/v1/currency/')
        logger.debug(currency_data)
        if currency_data["objects"] == []:
            for curr in all_currencys:
                x = requests.post(f'{getenv("API")}/api/v1/currency/',
                                json=curr, headers=headers)
                logger.debug(f'{curr} - {x.status_code}')

            return True
        return False
    except:
        logger.error(currency_data)





@logger.catch
async def update_course(data_pars):
    """Обновляем курс если курс не равен текущему"""
    get_currency = []
    gold = get_data(url_gold, "div", 'nd-fq-last-container nd-fq-last')

    # Задаем значения
    divisor = 31.11
    percentage = 6.5 / 100  # Преобразуем процент в десятичную дробь

    # Выполняем расчет
    result = (float(gold) / divisor) * (1 + percentage)

    data_api = get_api_data(url_currencys)

    currency_map = {
        'usd': ("🇺🇸/🇺🇦 USD: {buy}/{sell}\n", 1),
        'eur': ("🇪🇺/🇺🇦 EUR: {buy}/{sell}\n", 2),
        'usd-eur': ("🇺🇸/🇪🇺 $/€: {buy}/{sell}\n", 3),
        'gbp-usd': ("🇺🇸/🇬🇧 $/£: {buy}/{sell}\n", 4),
        'chf-usd': ("🇺🇸/🇨🇭 $/Fr: {buy}/{sell}\n\n", 5),
        'gbp': ("🇬🇧/🇺🇦 GBP: {buy}/{sell}\n", 6),
        'chf': ("🇨🇭/🇺🇦 CHF: {buy}/{sell}\n", 7),
        'pln': ("🇵🇱/🇺🇦 PLN: {buy}/{sell}\n", 8),
        'ron': ("🇷🇴/🇺🇦 RON: {buy}/{sell}\n", 9),
        'mdl': ("🇲🇩/🇺🇦 MLD: {buy}/{sell}\n", 10),
        'cad': ("🇨🇦/🇺🇦 CAD: {buy}/{sell}\n", 11),
        'nok': ("🇳🇴/🇺🇦 NOK: {buy}/{sell}\n", 12),
        'aud': ("🇦🇺/🇺🇦 AUD: {buy}/{sell}\n", 13),
        'dkk': ("🇩🇰/🇺🇦 DKK: {buy}/{sell}\n", 14),
        'cny': ("🇨🇳/🇺🇦 CNY: {buy}/{sell}\n", 15),
        'try': ("🇹🇷/🇺🇦 TRY: {buy}/{sell}\n", 16),
        'ils': ("🇮🇱/🇺🇦 ILS: {buy}/{sell}\n", 17),
        'czk': ("🇨🇿/🇺🇦 CZK: {buy}/{sell}\n", 18),
        'huf': ("🇭🇺/🇺🇦 HUF: {buy}/{sell}\n", 19),
        'sek': ("🇸🇪/🇺🇦 SEK: {buy}/{sell}\n", 20),
        'aed': ("🇦🇪/🇺🇦 AED: {buy}/{sell}\n", 21),
        'bgn': ("🇧🇬/🇺🇦 BGN: {buy}/{sell}\n", 22),
    }

    if data_api:
        for curr in data_pars:
            for curr_api in data_api["objects"]:
                if curr['currency'] == curr_api['code']:
                    if curr['buy'] != curr_api['buy'] or curr['sell'] != curr_api['sell']:
                        logger.debug(
                            f"{curr_api['id']} buy {curr_api['code']} {curr['buy']} = {curr_api['buy']} sell {curr['sell'] == curr_api['sell']}  {curr['sell']} = {curr_api['sell']}")
                        ed_curr = {
                            "buy": f"{curr['buy']}",
                            "sell": f"{curr['sell']}",
                            "updatedAt": ""
                        }
                        edit_currency(
                            f'{getenv("API")}/api/v1/currencys/{curr_api["id"]}/', ed_curr)

            formatted_str, index = currency_map.get(curr['currency'], (None, None))

            if formatted_str:
                if index is None:
                    get_currency.append(formatted_str.format(**curr))
                else:
                    get_currency.insert(index, formatted_str.format(**curr))

    add_text_currency = ''
    for add in get_currency:
        add_text_currency += add

    new_currency = f"💰💰Обмін валют Privat💰💰\n\nКурс від 500$/€/£/₣\n{add_text_currency}🥇 /🇺🇸 GOLD {float(round(result, 2)) - 4}/{round(result, 2)} $/g\n\nНа купюри номіналом 1, 2, 5, 10, 20, 50 $ оптовий курс не діє\n\nПриймаємо зношенi купюри з min %\n\nМенеджер\n💬💬0967228090 💬 @PrivatObmenOd\nІндивідуальні пропозиції,  якість  обслуговування :\nКерівник\n💬💬0634765088 💬 @VitalikPrivat"
    await send_currency(new_currency)

@logger.catch
async def post_to_db():
    next = add_all_currency()

    if next:
        try:
            data_api = get_api_data(f'{getenv("API")}/api/v1/currencys/')
            if data_api["objects"] == []:
                """Если в базе нет курсов"""
                logger.debug(data_api)
                add_course()
        except:
            logger.debug(data_api)
    # await update_course(parser_exchanger())
    # Хранение предыдущего хеша
    previous_hash = None

    while True:
        # Получаем текущее время
        now = datetime.now(timezone('Europe/Kiev'))
        logger.debug(now.strftime("%H:%M:%S"))
        # print(hashlib.md5(f"{parser_exchanger()}".encode('utf-8')).hexdigest())

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

            # Обновляем предыдущий хеш
            previous_hash = current_hash

            # Ждем 5 минут (300 секунд)
            await asyncio.sleep(300)
        else:
            # Если текущее время вне диапазона, ждем 1 минуту перед следующей проверкой
            await asyncio.sleep(60)