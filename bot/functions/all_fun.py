import requests
import json
import requests
from bs4 import BeautifulSoup
from decimal import Decimal
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger
from pytz import timezone
from datetime import datetime
from os import getenv

url_currencys = f'{getenv("API")}/api/v1/currencys/?limit=100'
headers = {"Authorization": f"ApiKey {getenv('API_KEY')}"}


now = datetime.now(timezone('Europe/Kiev'))
# Список часов, в которые нужно отправлять сообщения
target_hours = list(range(9, 20))  # от 9 до 19 включительно
minute_condition = (now.hour == 8 and now.minute == 45) or (now.hour in target_hours and now.minute == 0)

private_obmen = getenv("PRIVATE_OBMEN")
exprivatUa = getenv("EXPRIVATUA")


UTM_ALL_KURS = '?utm_source=telegram&utm_medium=private_obmen&utm_campaign=all_kurs'
UTM_RESERV = '?utm_source=telegram&utm_medium=private_obmen&utm_campaign=reserv&utm_id=reserv'


# Глобальная переменная
correction_value = Decimal('0.15')


def set_correction(value):
    global correction_value
    correction_value = Decimal(value)


def get_correction():
    return correction_value


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
                        f"exchanger_id {exchanger_id } / {curr_api['id']} / {curr_api['code']} buy {curr['buy']}  sell {curr['sell']}")
            currency_id += 1
            logger.debug(curr['currency'])
        exchanger_id += 1


@logger.catch
async def send_currency(new_text):
    bot = Bot(token=getenv("TOKEN"), default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))
    async with bot.session:  # or `bot.context()`
        main_kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Курс всіх валют",
                                     url=f'{getenv("API")}{UTM_ALL_KURS}',
                                     callback_data="event")
            ],
            [
                InlineKeyboardButton(text="🛎 Забронювати курс",
                                     url=f'{getenv("API")}{UTM_RESERV}',
                                     callback_data="event")
            ]
        ],)

        await bot.send_message(chat_id=exprivatUa,
                            text=new_text,
                            reply_markup=main_kb)


@logger.catch
def edit_currency(url, new_json) -> None:
    """Обновляет курс на сайте patch"""
    x = requests.patch(url, json=new_json, headers=headers)
    logger.debug(f"{new_json} / {x.status_code}")


@logger.catch
async def status_orders(data_id, data_status):
    order_patch = {"status": f"{data_status}"}
    x = requests.patch(f'{getenv("API")}/api/v1/orders/{data_id}/',
                       json=order_patch, headers=headers)
    logger.debug(x.status_code)
    return order_patch


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
                        buy=str(curr['rate']['buy']['value']
                                ).replace(',', '.'),
                        sell=str(curr['rate']['sell']['value']).replace(',', '.'))
        new_data_pars.append(add_curr)
        count += 1

    return new_data_pars



@logger.catch
def get_api_data(api_url):
    """Функция для получения данных из API"""
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()  # Предполагаем, что ответ в формате JSON
    else:
        logger.error("Ошибка при получении данных из API")
        return {}


try:
    data_api = get_api_data(f'{getenv("API")}/api/v1/currencys/')
    if data_api["objects"] == []:
        """Если в базе нет курсов"""
        logger.debug(data_api)
        add_course()
except:
    logger.debug(data_api)

@logger.catch
async def send_msg_currency():
    pass

@logger.catch
async def update_course(data_pars):
    """Обновляем курс если курс не равен текущему"""
    get_currency = []
    gold = get_data(getenv("URL_GOLD"), "div",
                    'nd-fq-last-container nd-fq-last')

    # Задаем значения
    divisor = 31.11
    percentage = 6.5 / 100  # Преобразуем процент в десятичную дробь


    # Выполняем расчет
    result = (float(gold) / divisor) * (1 + float(percentage))

    data_api = get_api_data(url_currencys)
    correction_value = get_correction()

    currency_map = {
        'usd': ("🇺🇸 🇺🇦 USD: {buy} / {sell}\n", 1),
        'eur': ("🇪🇺 🇺🇦 EUR: {buy} / {sell}\n", 2),
        'usd-eur': ("🇺🇸 🇪🇺 $/€: {buy} / {sell}\n", 3),
        'gbp-usd': ("🇺🇸 🇬🇧 $/£: {buy} / {sell}\n", 4),
        'chf-usd': ("🇺🇸 🇨🇭 $/₣: {buy} / {sell}\n\n", 5),
        'gbp': ("🇬🇧 🇺🇦 GBP: {buy} / {sell}\n", 6),
        'chf': ("🇨🇭 🇺🇦 CHF: {buy} / {sell}\n", 7),
        'pln': ("🇵🇱 🇺🇦 PLN: {buy} / {sell}\n", 8),
        'ron': ("🇷🇴 🇺🇦 RON: {buy} / {sell}\n", 9),
        'mdl': ("🇲🇩 🇺🇦 MLD: {buy} / {sell}\n", 10),
        'cad': ("🇨🇦 🇺🇦 CAD: {buy} / {sell}\n", 11),
        'nok': ("🇳🇴 🇺🇦 NOK: {buy} / {sell}\n", 12),
    }
    flag = False
    for curr in data_pars:
        for curr_api in data_api["objects"]:

            if curr['currency'] == curr_api['code']:
                if curr['buy'] != curr_api['buy'] or curr['sell'] != curr_api['sell']:
                    logger.debug(f"{curr_api['id']} {curr_api['code']} buy {curr['buy']} = {curr_api['buy']} sell {curr['sell']} = {curr_api['sell']}")

                    if curr_api['code'] == 'usd':
                        new_buy = Decimal(curr['buy']) - correction_value
                        new_sell = Decimal(curr['sell']) - correction_value

                        logger.debug(f"{curr_api['buy']} - {new_buy} / {new_sell} - {curr_api['sell']}")

                        if new_buy == Decimal(curr_api['buy']) and new_sell == Decimal(curr_api['sell']):
                            break

                        ed_curr = {
                            "buy": f"{new_buy}",
                            "sell": f"{new_sell}",
                            "updatedAt": ""
                        }
                    else:
                        ed_curr = {
                            "buy": f"{curr['buy']}",
                            "sell": f"{curr['sell']}",
                            "updatedAt": ""
                        }
                    edit_currency(f'{getenv("API")}/api/v1/currencys/{curr_api["id"]}/', ed_curr)

                    if curr_api['code'] == 'usd' or curr_api['code'] == 'eur':
                        flag = True


        # Добавляем строку для Telegram
        formatted_str, index = currency_map.get(curr['currency'], (None, None))
        if formatted_str:
            if index == 1:
                # Обновляем словарь curr, чтобы новые значения использовались в сообщении
                get_currency.insert(index, formatted_str.format(
                    buy=new_buy,
                    sell=new_sell
                ))
            else:
                get_currency.insert(index, formatted_str.format(
                    buy=curr['buy'],
                    sell=curr['sell']
                ))

    # Собираем финальное сообщение
    add_text_currency = ''.join(get_currency)

    new_currency = (
        f"<b>💰 Курс від 500$/€/£/₣</b>\n\n{add_text_currency}"
        f"🥇 🇺🇸 GOLD {float(round(result, 2)) - 4} / {round(result, 2)} $/g\n\n"
        "⚠️ На купюри номіналом 1, 2, 5, 10, 20, 50 $ оптовий курс не діє\n\n"
        "💵 Приймаємо зношенi купюри з min%\n\n"
        "Менеджер\n📲 0967228090  @PrivatObmenOd\n\n"
        "Індивідуальні пропозиції, якість обслуговування :\n"
        "Керівник\n📲 0634765088  @VitalikPrivat"
    )

    if flag or minute_condition:
        await send_currency(new_currency)
        logger.debug(now.strftime("%H:%M:%S"))
