from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters import Command
from functions.orders import order_send_message
from functions.post_db import post_to_db
from db_main import Database
import requests
from os import getenv
from loguru import logger

orders_url = f'{getenv("API")}/api/v1/orders/?status=new'
get_status = f'{getenv("API")}/api/v1/orders/?status=accepted'

headers = {"Authorization": f"ApiKey {getenv('API_KEY')}"}

router = Router()



# getenv("ULIA") Head Admin PrivatObmenOd
chat_id_name = getenv("Admin")


db = Database()

@router.message(Command("start"))
async def start_handler(msg: Message):

    try:
        # Получаем информацию о пользователе
        chat_id = msg.from_user.id
        username = msg.from_user.username or "Без username"

        # Проверяем существование пользователя
        exists, user_data = db.user_exists(chat_id)

        if exists:
            if user_data[3] == "client":
                await msg.answer(text=f"✨ Добро пожаловать!\n\n {msg.from_user.first_name} Вам доступны все функции для клиентов. \n\n",
                                 reply_markup=get_armor(chat_id))
                return
            if user_data[3] == "moderator":
                await msg.answer(text=f"Добро пожаловать {msg.from_user.first_name}!\n\n",
                                 reply_markup=api_res())
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
def get_contact():
    kb = [
        [
            KeyboardButton(text='📲 Отправить свой контакт', request_contact=True)
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True, one_time_keyboard=True,
        input_field_placeholder="нажмите кнопку 📲 Отправить свой контакт"
    )
    return keyboard

def get_armor(tel: str):
    buttons = [
        [
            InlineKeyboardButton(text="💲 Мої броні",
                                 callback_data=f"getarmor_{tel}"),
        ],

    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


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
            chat_id=callback.from_user.id, text=f"Замовлення {order_id.zfill(4)} ✅ Прийняте\n\n➕ добавлено в ℹ️ Прийняте замовлення ", message_id=callback.message.message_id)
        # await callback.bot.send_message(chat_id=chat_id_name, text=f"Замовлення {order_id} ➕ добавлено в ℹ️ Прийняте замовлення ")

        logger.debug(order_id)

    logger.info(callback.from_user)
    if callback.data == f'getarmor_{callback.data.split("_")[1]}':

        exists, user_data = db.user_exists(callback.data.split("_")[1])
        if exists:
            if user_data[3] == "client":
                logger.debug(user_data)
                order, order_data = db.get_orders(clients_telephone=user_data[4])
                logger.debug(user_data[4])
                logger.debug(order)
                id = f"{order_data[0]}".zfill(4)
                send_order = f"🛎 <b>Ваше замовлення</b> {id}\n\n🏦{user_data[4]}\n{user_data[4]} \n🫳{user_data[4]} по {user_data[4]} \nCума <b>{user_data[4]}</b>\n\n"
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

@logger.catch
def accept_order(order_id):
    buttons = [
        [
            InlineKeyboardButton(text="✔️ Прийняти замовлення",
                                 callback_data=f"accepted_{order_id}"),
        ],
        [
            InlineKeyboardButton(text="❌ Відмінити замовлення",
                                 callback_data=f"cancel_{order_id}"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


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


@router.message(F.text == "on_order_send_message")
async def echo_handler(message: types.Message):
    logger.info(message.text)
    # await message.bot.send_message(chat_id=chat_id_name, text=f"{message.text}")
    await order_send_message()


@router.message(F.text == "on_post_db")
async def echo_handler(message: types.Message):
    logger.info(message.text)
    await post_to_db()


@router.message()
async def echo_handler(msg: types.Message):

    if msg.contact:
            db.update_phone_user(chat_id=msg.from_user.id, clients_telephone=msg.contact.phone_number)
            await msg.answer(f"Дякуємо за ваш номер \n📲{msg.contact.phone_number}",
                                 reply_markup=ReplyKeyboardRemove())
            await msg.answer(text=f"✨ Ласкаво просимо!\n\n {msg.from_user.first_name} Для перевірки броні\nнатисніть кнопку 👇🏻👇🏻👇🏻",
                                 reply_markup=get_armor(msg.contact.phone_number))



@logger.catch
def kb_status_order(order_id):
    buttons = [
        [
            InlineKeyboardButton(text="✅ Замовлення виконано",
                                 callback_data=f"completed_{order_id}"),
        ],
        [
            InlineKeyboardButton(text="❌ Відмінити замовлення",
                                 callback_data=f"cancel_{order_id}"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@logger.catch
def api_res():
    kb = [[KeyboardButton(text='ℹ️ Прийняте замовлення',
                          callback_data=f"apiaccepted")],]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True, one_time_keyboard=True
    )
    return keyboard


logger.add("../log/DEBUG.log", colorize=True,
           format="{time:YYYY-MM-DD HH:mm:ss} {name} {line} {level} {message} ", level="DEBUG", rotation="500 KB", compression="zip")
