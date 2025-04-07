from aiogram import types, F, Router
from decimal import Decimal
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove
from aiogram.filters import Command
from functions.all_fun import set_correction
from functions import orders, post_db
from allkeyboard.all_keyboard import get_armor, get_contact, kb_status_order, order_accepted
import requests

from os import getenv
from functions.db_main import Database
from loguru import logger

orders_url = f'{getenv("API")}/api/v1/orders/?status=new'
get_status = f'{getenv("API")}/api/v1/orders/?status=accepted'

headers = {"Authorization": f"ApiKey {getenv('API_KEY')}"}

router = Router()

db = Database()

chat_id_name = getenv("Admin")


@router.message(Command("start"))
async def start_handler(msg: Message):
    try:
        # Получаем информацию о пользователе
        chat_id = msg.from_user.id
        username = msg.from_user.username or "Без username"

        # Проверяем существование пользователя
        exists, user_data = db.user_exists(chat_id)

        if exists:
            logger.debug(user_data)
            if user_data[3] == "client":
                if user_data[4] == '':
                    await msg.answer(text='Щоб побачити свою бронь Натисніть кнопку 📲 Надіслати свій контакт кнопка в меню 👇 👇 👇',
                                    reply_markup=get_contact())
                    return
                await msg.answer(text=f"🎉 Ласкаво просимо, {msg.from_user.first_name}!✨\n\nДля перевірки броні\nнатисніть кнопку 👇🏻👇🏻👇🏻",
                                 reply_markup=get_armor(chat_id))
                return
            if user_data[3] == "moderator":
                await msg.answer(text=f"Добро пожаловать {msg.from_user.first_name}!\n\n",
                                 reply_markup=order_accepted())
                return
            logger.debug("Вы уже зарегистрированы в системе.")
            return

        # Добавляем пользователя с ролью по умолчанию
        result = db.add_user(
            chat_id=chat_id,
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


@logger.catch
async def status_orders(data_id, data_status):
    order_patch = {"status": f"{data_status}"}
    x = requests.patch(f'{getenv("API")}/api/v1/orders/{data_id}/',
                       json=order_patch, headers=headers)
    logger.debug(x.status_code)
    return order_patch


@logger.catch
@router.callback_query()
async def callbacks_all_trip(callback: types.CallbackQuery):
    """ Обработка callback Данных """
    logger.debug(callback.data)
    order_id = callback.data.split("_")[1]
    status = callback.data.split("_")[0]
    order_id.zfill(4)
    if callback.data == f"accepted_{order_id}":

        await status_orders(order_id, status)
        await callback.bot.edit_message_text(
            chat_id=callback.from_user.id,
            text=f"Замовлення {order_id.zfill(4)} ✅ Прийняте\n\n➕ добавлено в ℹ️ Прийняте замовлення ",
            message_id=callback.message.message_id)

        logger.debug(order_id)

    logger.info(callback.from_user)
    if callback.data == f'getarmor_{callback.data.split("_")[1]}':

        exists, user_data = db.user_exists(callback.data.split("_")[1])
        if exists:
            if user_data[3] == "client":
                logger.debug(user_data)
                order, order_data = db.get_orders(clients_telephone=user_data[4])
                logger.debug(order_data)
                if order:
                    # Вы отримуйте
                    id, address_exchanger,  currency_name, buy_or_sell, exchange_rate, order_sum = f"{order_data[0]}".zfill(4), order_data[3], order_data[4], order_data[5], order_data[6], order_data[7]
                    send_order = f"🛎 <b>Ваше замовлення</b> {id}\n\n🏦{address_exchanger}\n{currency_name} \n🫳{buy_or_sell} по {exchange_rate} \nCума <b>{order_sum}</b>\n\n"
                    await callback.bot.send_message(chat_id=callback.from_user.id, text=send_order)


    if callback.data == f"cancel_{order_id}":
        await status_orders(order_id, status)
        await callback.bot.edit_message_text(chat_id=callback.from_user.id, text=f"Відмінити замовлення №{order_id.zfill(4)}", message_id=callback.message.message_id)

        logger.debug(order_id)

    if callback.data == f"completed_{order_id}":
        await status_orders(order_id, status)
        await callback.bot.edit_message_text(chat_id=callback.from_user.id, text=f"✅ Виконано замовлення №{order_id.zfill(4)}", message_id=callback.message.message_id)
        logger.debug(f'{order_id} {callback.from_user}')

all_orders =f"<a href='{getenv('API')}/admin/currency/orders/'>Все заказы</a>"



@router.message(F.text == "ℹ️ Прийняте замовлення")
async def ger_accepted_(message: types.Message):
    help_text = f"💬 <b>В даном разделе Вы увитите принятые заказы:</b>\n\n1 В случии если клиент не пришол за бронью - Менаджер нажимает на кнопку под заказом Отменить.\n2 В случии если клиент пришол за бронью - Менаджер вибирает кнопку Заказ виполнен\n {all_orders}"

    await message.answer(text=help_text)
    res = requests.get(get_status)
    data = res.json()
    orders = data.get('objects')
    count = 1
    logger.debug(orders)
    if orders:
        for order in orders:
            id = f"{order.get('id')}".zfill(4)
            send_order = f"🏷 {count} <b>Прийняте замовлення</b> {id}\n\n🏦{order.get('address_exchanger')}\n{order.get('currency_name')} \n🫳{order.get('buy_or_sell')} по {order.get('exchange_rate')} \nCумма <b>{order.get('order_sum')}</b>\n\n📲{order.get('сlients_telephone')}"
            get_id = order.get('id')
            await message.answer(text=send_order,  reply_markup=kb_status_order(get_id))
            count += 1
    if orders == []:
        await message.answer(text='Немає Прийнятих замовлень')





@router.message(lambda message: message.text.startswith("Разница="))
async def set_difference(message: types.Message):
    chat_id = get_users_data(role="moderator")
    if chat_id == message.from_user.id:
        try:
            kop = message.text.split('=')[1].strip()
            value = Decimal(kop) / 100  # переводим копейки в гривны
            set_correction(value)
            await message.answer(f"✅ Разница успешно установлена на {value} грн")
        except Exception as e:
            await message.answer("❌ Неверный формат. Используй: Разница=25")
        logger.info(kop)



@router.message(F.text == "on_order_send_message")
async def echo_handler(message: types.Message):
    logger.info(message.text)
    chat_id = get_users_data(role="moderator")
    logger.info(chat_id)
    await orders.order_send_message(chat_id)


def get_users_data(role: str):
    """Проверяем роль"""
    res, user_data = db.exists_role(role)
    if res:
        return user_data[1]

@router.message(F.text == "on_post_db")
async def echo_handler(msg: types.Message):
    logger.info(msg.text)
    await post_db.post_db()

@router.message()
async def echo_handler(msg: types.Message):

    if msg.contact:
            db.update_phone_user(chat_id=msg.from_user.id, clients_telephone=msg.contact.phone_number)
            await msg.answer(f"Дякуємо за ваш номер \n📲{msg.contact.phone_number}",
                                 reply_markup=ReplyKeyboardRemove())
            await msg.answer(text=f"✨ Ласкаво просимо!\n\n {msg.from_user.first_name} Для перевірки броні\nнатисніть кнопку 👇🏻👇🏻👇🏻",
                                 reply_markup=get_armor(msg.from_user.id))
