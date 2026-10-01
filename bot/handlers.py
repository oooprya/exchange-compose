import aiohttp
import asyncio
import requests
from loguru import logger
from decimal import Decimal
from datetime import datetime
from zoneinfo import ZoneInfo

from ai.memory import memory
from ai.manager import manager
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import types, F, Router
from functions import orders, post_db

from aiogram.types import ReplyKeyboardRemove
from aiogram.exceptions import TelegramBadRequest
from config import db, API_URL_CURRENCYS, API_BASE, USD_PATTERN, ADMIN_CHAT_ID, PATTERN, EUR_PATTERN, B_PATTERN, API_URL
from functions.all_fun import update_currency_usd, status_orders, parse_trade_message
from allkeyboard.all_keyboard import get_armor, get_contact, kb_status_order, order_accepted
from services.constants import ORDER_STATUS


router = Router()


@router.business_message()
async def ai_chat(message: Message):
    chat_id = str(message.from_user.id)
    text = (message.text or "").strip().lower()

    greetings = {
        "здравствуйте",
        "здравствуй",
        "добрый день",
        "доброе утро",
        "привет",
        "добрый вечер",
    }

    if text in greetings:
        await asyncio.sleep(2)

        hour = datetime.now(
            ZoneInfo("Europe/Kyiv")
        ).hour

        if hour < 12:
            greeting = "Доброго ранку!"
        elif hour < 17:
            greeting = "Доброго дня!"
        else:
            greeting = "Доброго вечора!"

        memory.add(chat_id, "user", message.text)
        memory.add(chat_id, "assistant", greeting)
        await message.answer(greeting)
        return

    answer = await manager.chat_delayed(
        chat_id=chat_id,
        text=message.text,
        delay=8.0,
    )

    if answer:
        await message.answer(answer, parse_mode="HTML")


@router.message(Command("start"))
async def start_handler(msg: Message):
    try:
        # Получаем информацию о пользователе
        new_chat_id = str(msg.from_user.id)
        username = msg.from_user.username or "Без username"

        # Проверяем существование пользователя
        exists, user_data = db.user_exists(new_chat_id)

        if exists:
            logger.debug(user_data)
            if user_data[3] == "moderator":
                await msg.answer(text=f"Добро пожаловать {msg.from_user.first_name}!\n\n",
                                 reply_markup=order_accepted())
                return
            if user_data[3] == "client":
                if user_data[4] == '':
                    await msg.answer(text='Щоб побачити свою бронь Натисніть кнопку 📲 Надіслати свій контакт кнопка в меню 👇 👇 👇',
                                     reply_markup=get_contact())
                    return
                await msg.answer(text=f"🎉 Ласкаво просимо, {msg.from_user.first_name}!✨\n\nДля перевірки броні\nнатисніть кнопку 👇🏻👇🏻👇🏻",
                                 reply_markup=get_armor(new_chat_id))
                return
            logger.debug("Вы уже зарегистрированы в системе.")
            return

        # Добавляем пользователя с ролью по умолчанию
        result = db.add_user(
            chat_id=new_chat_id,
            chat_id_name=username,
            role="client",  # Роль по умолчанию
            clients_telephone=""
        )

        if result:
            logger.debug("Вы успешно зарегистрированы!")
            await msg.answer(text='Щоб побачити свою бронь Натисніть кнопку 📲 Надіслати свій контакт кнопка в меню 👇 👇 👇',
                             reply_markup=get_contact())
        else:
            logger.error("Не удалось зарегистрировать пользователя.")
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {e}")
        await msg.answer("Произошла ошибка при регистрации.")


def build_client_status_message(
    status,
    order_id,
    currency="",
    amount="",
    address="",
    rate=""
):
    template = ORDER_STATUS.get(status, {}).get(
        "client_text",
        "Статус оновлено"
    )

    return template.format(
        id=str(order_id).zfill(4),
        currency=currency,
        amount=amount,
        address=address,
        rate=rate,
    )


async def show_client_orders(callback, clients_telephone):
    exists, user_data = db.user_exists(callback.data.split("_")[1])
    order, order_data = db.get_orders(clients_telephone)
    logger.debug(exists, user_data, order, order_data)


async def process_order_status(
    callback,
    order_id,
    status,
):
    await status_orders(order_id, status)

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.answer(
        f"Статус змінено: {status}"
    )


@logger.catch
@router.callback_query()
async def callbacks_all_trip(callback: types.CallbackQuery):
    """ Обработка callback Данных """
    logger.debug(callback.data)
    order_id = callback.data.split("_")[1]
    status = callback.data.split("_")[0]
    order_id.zfill(4)
    STATUS = (
        ('new', '✉️ Надіслано'),
        ('ordersent', '✉️ Надіслано'),
        ('accepted', '✅ Прийнято'),
        ('completed', '🛍 Виконано'),
        ('cancel', '❌ Скасовано'),
        ('noshow', '🤷‍♂️ Не пришел'),
    )
    STATUS_DICT = dict(STATUS)

    if callback.data == f"accepted_{order_id}":

        await status_orders(order_id, status)

        order, order_data = db.get_order_by_id(order_id)

        if order:

            order_id, status, client_phone, address,  currency, buy_or_sell, rate, amount = f"{order_data[0]}".zfill(
                4), order_data[1],  order_data[2], order_data[3], order_data[4], order_data[5], order_data[6], order_data[7]

            # убрать кнопки
            try:
                await callback.message.edit_reply_markup(reply_markup=None)
            except TelegramBadRequest:
                pass

            try:
                await callback.message.edit_text(
                    callback.message.text +
                    f"\n\n✅ Замовлення прийнято!: <b>@{callback.from_user.username}</b>",
                    parse_mode="HTML"
                )
            except TelegramBadRequest:
                pass

            exists, client_chat_id = db.get_chat_id_by_phone(client_phone)
            logger.debug(client_chat_id)

            if exists:

                await callback.bot.send_message(
                    chat_id=client_chat_id,
                    text=build_client_status_message(
                        status, order_id, currency=currency, amount=amount, address=address, rate=rate)
                )

            else:
                logger.warning(
                    f"Телефон {client_phone} не привязан к Telegram")

            try:
                await callback.answer(f"✅ Ви прийняли бронь №{order_id}")
            except TelegramBadRequest as e:
                if "message is not modified" in e.message:
                    await callback.answer("Кто-то уже принял этот заказ!", show_alert=True)

        logger.debug(order_id)

    logger.info(callback.from_user)
    if callback.data == f'getarmor_{callback.data.split("_")[1]}':

        exists, user_data = db.user_exists(callback.data.split("_")[1])
        if exists:
            if user_data[3] == "client":
                logger.debug(user_data)
                order, order_data = db.get_orders(
                    clients_telephone=user_data[4])
                logger.debug(order_data)
                if order:
                    count = 1
                    for orders in order_data:

                        # Вы отримуйте
                        id, status, address_exchanger,  currency_name, buy_or_sell, exchange_rate, order_sum = f"{orders[0]}".zfill(
                            4), orders[1], orders[3], orders[4], orders[5], orders[6], orders[7]
                        logger.debug(
                            f'Ви отримаєте на руки {exchange_rate * order_sum}')

                        text = ""
                        if status not in {'completed', 'cancel', 'noshow'}:
                            text = "\n\n🕒 Бронь дійсна: до 90 хвилин \n\n👉 Приходьте до зазначеного пункту та покажіть це повідомлення оператору."

                        send_order = f"🔐 {count} <b> Ваша бронь:</b> {id} \nСтатус: {STATUS_DICT[f'{status}']}\n\n💱 Валюта: \
                        {currency_name}\n💵 Сума: <b>{order_sum}</b>\n📍 Пункт обміну: {address_exchanger}\n{buy_or_sell} по {exchange_rate} {text}"
                        await callback.bot.send_message(chat_id=callback.from_user.id, text=send_order)

                        count += 1

                else:
                    book_course = f"<a href='{API_BASE}?utm_source=telegram&utm_medium=privat_obmen_bot&utm_campaign=link&utm_id=link'>Забронювати курс</a>"
                    await callback.bot.send_message(chat_id=callback.from_user.id,
                                                    text=f"ℹ️ Якщо ви не бачите свою броню, то ваш номер телефону в телеграмі не співпадає з номером телефону броні.\n\n\nЗабронюйте курс за вигідним значенням — і ми зафіксуємо його на зручний для вас час.\n👇👇👇\n\n {book_course}")

    if callback.data == f"noshow_{order_id}":
        # убрать кнопки
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass
        await status_orders(order_id, status)
        await callback.bot.edit_message_text(chat_id=callback.from_user.id, text=f"Не пришел замовлення №{order_id.zfill(4)}", message_id=callback.message.message_id)

    if callback.data == f"cancel_{order_id}":

        # убрать кнопки
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass

        await status_orders(order_id, status)

        try:
            await callback.message.edit_text(
                callback.message.text +
                f"\n\n❌ Відміна замовлення <b>@{callback.from_user.username}</b>",
                parse_mode="HTML"
            )
        except TelegramBadRequest:
            pass

        order, order_data = db.get_order_by_id(order_id)

        if order:

            order_id, status, client_phone, address,  currency, buy_or_sell, rate, amount = f"{order_data[0]}".zfill(
                4), order_data[1],  order_data[2], order_data[3], order_data[4], order_data[5], order_data[6], order_data[7]

            exists, client_chat_id = db.get_chat_id_by_phone(client_phone)

            if exists:

                await callback.bot.send_message(
                    chat_id=client_chat_id,
                    text=build_client_status_message(
                        status, order_id, currency=currency, amount=amount, address=address, rate=rate)
                )
            else:
                logger.warning(
                    f"Телефон {client_phone} не привязан к Telegram")

    if callback.data == f"completed_{order_id}":
        await status_orders(order_id, status)

        # убрать кнопки
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass

        try:
            await callback.message.edit_text(
                callback.message.text +
                f"\n\n✅ Виконано замовлення!: <b>@{callback.from_user.username}</b>",
                parse_mode="HTML"
            )
        except TelegramBadRequest:
            pass

        # await callback.bot.edit_message_text(chat_id=callback.from_user.id, text=f"✅ Виконано замовлення №{order_id.zfill(4)}", message_id=callback.message.message_id)
        logger.debug(f'{order_id} {callback.from_user}')
        order, order_data = db.get_order_by_id(order_id)

        if order:

            order_id, status, client_phone, address,  currency, buy_or_sell, rate, amount = f"{order_data[0]}".zfill(
                4), order_data[1],  order_data[2], order_data[3], order_data[4], order_data[5], order_data[6], order_data[7]

            exists, client_chat_id = db.get_chat_id_by_phone(client_phone)
            logger.debug(client_chat_id)

            if exists:

                await callback.bot.send_message(
                    chat_id=client_chat_id,
                    text=build_client_status_message(
                        status, order_id, currency=currency, amount=amount, address=address, rate=rate)
                )


@router.message(F.text == "ℹ️ Прийняте замовлення")
@router.message(Command("orders"))
async def get_accepted(message: types.Message):

    isorder, order_data = db.get_orders_status(status="accepted")
    count = 1
    # logger.debug(order_data)
    if isorder:
        for order in order_data:
            # logger.debug(order)
            id = str(order[0])
            send_order = f"🏷 {count} <b>Прийняте замовлення</b> {id.zfill(4)}\n\n🏦{order[3]}\n{order[4]} \n<b>{order[5]}</b> по {order[6]} \nCумма <b>{order[7]}</b>\n\n📲+{order[2]}"
            get_id = order[0]
            await message.answer(text=send_order,  reply_markup=kb_status_order(get_id))
            count += 1
    else:
        await message.answer(text='Немає Прийнятих замовлень')


def get_usd_currency():
    try:
        response = requests.get(f'{API_URL}/currencys/')
        response.raise_for_status()  # Проверка наличия ошибок
        # Обработка ответа
    except requests.exceptions.RequestException as e:
        print('Произошла ошибка при выполнении запроса:', e)

    if response.status_code == 200:
        usd_data = response.json()
        usd = usd_data.get("objects")[0]
        return usd


@router.message(F.text.startswith("USD="))
async def setDifference(message: types.Message):
    chat_id = orders.get_users_data(role="moderator")
    logger.debug(f'{chat_id=} {message.from_user.id=}')

    if message.from_user.id == int(chat_id) or message.from_user.id == int(ADMIN_CHAT_ID):

        try:
            data = message.text.split('=')[1].strip()
            buy_str, sell_str = data.split('/')

            if await update_currency_usd(Decimal(buy_str), Decimal(sell_str)):
                await message.answer(f'✅ Курс USD - Долар установлен {buy_str}/{sell_str}')

        except Exception as e:
            logger.debug(e)
            await message.answer(f'❌ Неверный формат. Пример: USD=41.25/41.50')


async def start_background_tasks():

    logger.info("Запуск фоновых задач...")

    asyncio.create_task(
        post_db.post_db()
    )

    asyncio.create_task(
        orders.order_send_message()
    )

    logger.success(
        "Все фоновые задачи запущены"
    )


async def get_api_rate(currency: str):
    """
    Ожидаемый ответ API:
    {
      "objects": [
        {
          "code": "usd",
          "buy": "42.10",
          "sell": "42.25"
        }
      ]
    }
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL_CURRENCYS, timeout=10) as resp:
                if resp.status != 200:
                    logger.error(f"API error {resp.status}")
                    return None

                data = await resp.json()

                if "objects" not in data:
                    logger.error("objects not found in API")
                    return None

                for item in data["objects"]:
                    if item.get("code", "").lower() == currency.lower():
                        return {
                            "buy": float(item["buy"]),
                            "sell": float(item["sell"])
                        }

                return None

    except Exception as e:
        logger.error(f"API request failed: {e}")
        return None


@router.channel_post()
async def channel_handler(msg: types.Message):
    text = msg.text or ""
    usd_match = USD_PATTERN.search(text)
    logger.debug(text)
    if not usd_match:
        return None

    buy = usd_match.group(1)
    sell = usd_match.group(2)

    await update_currency_usd(Decimal(buy), Decimal(sell))


@router.message()
async def echo_handler(msg: types.Message):
    if msg.contact:
        telephone = msg.contact.phone_number

        if telephone[0] == '+':
            telephone = telephone[1:]

        db.update_phone_user(
            chat_id=str(msg.from_user.id),
            clients_telephone=telephone
        )

        await msg.answer(f"Дякуємо за ваш номер \n📲{msg.contact.phone_number}",
                         reply_markup=ReplyKeyboardRemove())
        await msg.answer(text=f"✨ Ласкаво просимо!\n\n {msg.from_user.first_name} Для перевірки броні\nнатисніть кнопку 👇🏻👇🏻👇🏻",
                         reply_markup=get_armor(str(msg.from_user.id)))
    if msg.text:
        text = msg.text.strip().lower()

        logger.info(text)

        match = PATTERN.match(text)
        if not match:
            return  # не похоже на нашу команду — молчим

        amount = int(match.group(1))
        currency = match.group(2)
        rate = float(match.group(3).replace(',', '.'))

        # -------------------------
        # Определяем currency code
        # -------------------------
        if "син" in text:
            currency = "usdnew"
        elif "нов" in text:
            currency = "usdnew"
        elif B_PATTERN.search(text):
            currency = "usd"
        elif EUR_PATTERN.search(text):
            currency = "eur"
        else:
            logger.debug("⚠️ Не смог определить валюту")
            # await msg.reply("⚠️ Не смог определить валюту")
            return

        logger.debug(
            f"Parsed → amount={amount}, currency={currency}, rate={rate}")

        api = await get_api_rate(currency)

        if api is None:
            # await msg.reply("⚠️ Не удалось получить курс из API")
            logger.debug("⚠️ Не удалось получить курс из API")
            return

        # защита от плавающей точки
        EPS = 0.001
        is_valid = False
        success_msg = ""  # Переменная для текста успеха

        # Логика:
        # минус  → Каса продает → проверяем SELL
        # плюс   → Каса покупает → проверяем BUY
        if amount < 0:
            expected = api["sell"]
            direction = "Продажа"
            # Для продажи: если курс БОЛЬШЕ или равен API, это ОК
            if rate >= expected - EPS:
                is_valid = True
                success_msg = "✅ ОК, отличная продажа"
        else:
            expected = api["buy"]
            direction = "Покупка"
            if rate <= expected + EPS:
                is_valid = True
                success_msg = "✅ ОК, отличная покупка"

        if is_valid:
            await msg.reply(success_msg)
            logger.debug(success_msg)
        else:
            # await msg.reply(
            #     f"❌ Нет, {direction}: {expected}"
            # )
            logger.debug(f"❌ Нет, {direction}: {expected}")
