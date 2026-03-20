import json
import requests
from bs4 import BeautifulSoup
from typing import Optional
from decimal import Decimal
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger
from pytz import timezone
from datetime import datetime

from services.formatter import format_currency_row
from services.constants import EXCHANGER_NOVYI_RYNOK, DISCOUNT_EUR, DISCOUNT_USD, DISCOUNT_USD_NEW


from config import API_URL_CURRENCYS, HEADERS, PARSER_EXCHANGER, EXPRIVATUA, ADMIN_CHAT_ID, TELEGRAM_TOKEN, API_BASE, TRADE_PATTERN


now = datetime.now(timezone('Europe/Kiev'))
# Список часов, в которые нужно отправлять сообщения
target_hours = list(range(9, 20))  # от 9 до 19 включительно


NOVYI_RYNOK = '/obmen/markevicha-32-novyi-rynok'
MELNYTSKA = '/obmen/melnytska-1-tavriya-v'
UTM_ALL_KURS = '?utm_source=telegram&utm_medium=private_obmen&utm_campaign=all_kurs'
UTM_RESERV = '?utm_source=telegram&utm_medium=private_obmen&utm_campaign=reserv&utm_id=reserv'


@logger.catch
def apply_discount(code: str, buy: Decimal, exchanger: str) -> Decimal:
    if exchanger[-2] != EXCHANGER_NOVYI_RYNOK:
        return buy

    if code == "usd":
        return buy - DISCOUNT_USD
    if code == "usdnew":
        return buy - DISCOUNT_USD_NEW
    if code == "eur":
        return buy - DISCOUNT_EUR

    return buy


@logger.catch
async def send_currency(new_text):
    bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))

    async with bot.session:  # or `bot.context()`
        main_kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🛎 Забронювати курс",
                                     url=f'{API_BASE}{UTM_RESERV}',
                                     callback_data="event")
            ]
        ],)

        await bot.send_message(chat_id=EXPRIVATUA,  # int(ADMIN_CHAT_ID) chat_id=EXPRIVATUA
                               text=new_text,
                               reply_markup=main_kb)


@logger.catch
def edit_currency(url: str, payload: dict) -> None:
    """Обновляет курс на сайте patch"""
    response = requests.patch(
        url,
        json=payload,
        headers=HEADERS

    )
    logger.debug(f"payload={payload} {response.status_code}")


@logger.catch
async def status_orders(data_id, data_status):
    order_patch = {"status": f"{data_status}"}
    x = requests.patch(f'{API_BASE}/api/v1/orders/{data_id}/',
                       json=order_patch, headers=HEADERS)
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
    url = PARSER_EXCHANGER

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
        add_curr = dict(id=count,
                        currency=curr['currency'],
                        buy=str(curr['rate']['buy']['value']
                                ).replace(',', '.'),
                        sell=str(curr['rate']['sell']
                                 ['value']).replace(',', '.')
                        )
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


@logger.catch
async def update_currency_usd(new_buy: Decimal, new_sell: Decimal) -> bool:
    """
    Обновляет USD курс, если он изменился.
    Возвращает True, если данные были обновлены.
    """

    data_api = get_api_data(API_URL_CURRENCYS)

    # data_api = await get_currencies()
    updated = False
    message_rows: list[str] = []

    for curr in data_api.get("objects", []):

        current_buy = Decimal(curr["buy"])
        current_sell = Decimal(curr["sell"])

        curr_buy = curr.get("buy")
        curr_sell = curr.get("sell")

        buy_with_discount = apply_discount(
            code=curr.get("code"),
            buy=new_buy,
            exchanger=curr.get("exchanger", "")
        )

        if curr.get("exchanger", "")[-2] == EXCHANGER_NOVYI_RYNOK:
            if curr.get("code") == "usd":
                curr_buy = apply_discount(
                    code=curr.get("code"),
                    buy=new_buy,
                    exchanger=curr.get("exchanger", "")
                )
                curr_sell = new_sell

            row, index = format_currency_row(
                curr.get("code"),
                str(curr_buy),
                str(curr_sell)
            )

            if row:
                logger.debug(
                    f'{curr.get("code")} {curr.get("buy")} {curr.get("sell")} - {index} {row}')
                message_rows.insert(index, row)

        if curr.get("code") != "usd":
            continue

        # Если изменений нет — ничего не делаем
        if (
            buy_with_discount == current_buy
            and new_sell == current_sell
        ):
            logger.debug(
                f"USD без изменений: {current_buy}/{current_sell}"
            )
            continue

        payload = {
            "buy": str(buy_with_discount),
            "sell": str(new_sell),
            "updatedAt": "",
        }

        edit_currency(
            f"{API_BASE}/api/v1/currencys/{curr['id']}/",
            payload
        )

        updated = True

    if message_rows:

        # Собираем финальное сообщение
        add_text_message = ''.join(message_rows)

        new_currency = build_currency_message(
            add_text_currency=add_text_message,
            gold_price=None
        )
        await send_currency(new_currency)

    return updated


@logger.catch
async def update_course(data_pars):
    """Обновляем курс если курс не равен текущему"""

    data_api = get_api_data(API_URL_CURRENCYS)

    for curr in data_pars:
        for curr_api in data_api["objects"]:

            curr_code = curr_api['code']

            if curr['currency'] == curr_code or f"{curr['currency']}new" == curr_code:

                if curr['buy'] != curr_api['buy'] or curr['sell'] != curr_api['sell']:

                    logger.debug(
                        f"{curr_api['id']} {curr_code} minfin {curr['buy']}/{curr['sell']} -> сайт {curr_api['buy']}/{curr_api['sell']}")

                    new_buy = curr['buy']
                    new_sell = curr['sell']

                    if curr_code != 'usd':

                        new_buy = apply_discount(
                            curr_api['code'],
                            Decimal(curr['buy']),
                            curr_api['exchanger']
                        )

                        ed_curr = {
                            "buy": str(new_buy),
                            "sell": str(new_sell),
                            "updatedAt": ""
                        }

                        edit_currency(
                            f'{API_BASE}/api/v1/currencys/{curr_api["id"]}/', ed_curr)

    # logger.info(f"{add_text_currency}")

    # new_currency = build_currency_message(
    #     usd_white_row=usd_white_row,
    #     add_text_currency=add_text_currency,
    #     gold_price=result,  # или None если золото временно не нужно
    # )

    # if flag:
    #     await send_currency(new_currency)


def build_currency_message(
    add_text_currency: str,
    gold_price: Optional[float] = None,
) -> str:
    """
    Формирует итоговое сообщение с курсами валют для Telegram.
    """

    message = (
        "<b>💰 Курс від 500$/€/£/₣</b>\n"
        f"{add_text_currency}"
    )

    # 🥇 Золото — опционально
    if gold_price is not None:
        message += (
            f"🥇 🇺🇸 GOLD {float(round(gold_price, 2)) - 4} / "
            f"{round(gold_price, 2)} $/g\n\n"
        )

    # ⚠️ Информационный блок
    message += (
        "\n⚠️ На купюри номіналом 1, 2, 5, 10, 20, 50 $ оптовий курс не діє\n\n"
        "💵 Приймаємо зношенi купюри з min%\n\n"
        "Звертайтесь за номером телефону:\n"
        "📲 0634765088  @VitalikPrivat"
    )

    return message


def parse_trade_message(text: str) -> list[dict]:

    trades = []

    for sign, amount, curr, color, rate in TRADE_PATTERN.findall(text):
        amount = int(amount)
        rate = Decimal(rate)

        operation = "buy" if sign == "+" else "sell"

        # currency code
        if curr in ("дол", "usd"):
            currency = "usdnew" if color == "син" else "usd"
        elif curr in ("евро", "eur"):
            currency = "eur"
        else:
            continue

        trades.append({
            "amount": amount,
            "currency": currency,
            "rate": rate,
            "operation": operation,
        })

    return trades
