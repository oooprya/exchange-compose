from aiogram import types, F, Router
import logging
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from functions import orders, post_db
import requests
import time
import json
from os import getenv
from dotenv import load_dotenv
from loguru import logger

orders_url = f'{getenv("API")}/api/v1/orders/?status=new'
get_status = f'{getenv("API")}/api/v1/orders/?status=accepted'

headers = {"Authorization": f"ApiKey {getenv('API_KEY')}"}

router = Router()

load_dotenv('.env')

# getenv("ULIA") Head Admin PrivatObmenOd
chat_id_name = getenv("Admin")


@router.message(Command("start"))
async def start_handler(msg: Message):
    # res = requests.get(orders_url)
    # data = res.json()
    # orders = data.get('objects')

    time_local = time.localtime()
    time_user = time.strftime('%Y %d %m %H:%M:%S', time_local)
    with open(f'users.json') as users_f:
        users_json = json.load(users_f)
    users_f.close()

    user_id = msg.from_user.id
    there_id = False

    for useri in range(len(users_json)):
        if user_id == users_json[useri]['id']:
            print(f'{user_id} = {users_json[useri]["id"]}')
            there_id = True
    print(there_id)

    # если в users.json нет такого user.id добавляем его в users.json
    if there_id == False:
        time_local = time.localtime()
        time_user = time.strftime('%Y %d %m %H:%M:%S', time_local)
        time_string = time.strftime('%d_%m_%H_', time_local)
        tM = time.strftime('%M', time_local)

        if int(tM[-1]) > 0:
            res_tM = tM[-2] + tM[-1].replace(tM[-1], '0')

        user = dict(id=msg.from_user.id, first_name=msg.from_user.first_name,
                    last_name=msg.from_user.last_name, username=msg.from_user.username, time=time_user)
        users_json.append(user)
        print(f'{user} : {time_string}{tM}')
        with open(f'users.json', 'w') as f:
            json.dump(users_json, f, indent=4)


    # if orders:
    #     for order in orders:
    #         get_id = order.get('id')
    #         send_order = f"🛎 <b>Нове замовлення</b> 10000{order.get('id')}\n\n🏦{order.get('address_exchanger')}\n{order.get('currency_name')} \n🫳{order.get('buy_or_sell')} по {order.get('exchange_rate')} \nCума <b>{order.get('order_sum')}</b>\n\n📲{order.get('сlients_telephone')}"
    #         logging.info(f"{order.get('id')}")
    #         await msg.answer(text=send_order,  reply_markup=accept_order(get_id))

    # if user_id == getenv("Admin"):
    await msg.answer(text=f"Доброго дня, {msg.from_user.first_name}! \n\n{all_orders}", reply_markup=api_res())

    logging.info(f'{msg.from_user.id}')


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

    if callback.data == f"cancel_{order_id}":
        await status_orders(order_id, status)
        await callback.bot.edit_message_text(chat_id=callback.from_user.id, text=f"Відмінити замовлення №{order_id.zfill(4)}", message_id=callback.message.message_id)

        logger.debug(order_id)

    if callback.data == f"completed_{order_id}":
        await status_orders(order_id, status)
        await callback.bot.edit_message_text(chat_id=callback.from_user.id, text=f"✅ Виконано замовлення №{order_id.zfill(4)}", message_id=callback.message.message_id)
        logger.debug(f'{order_id} {callback.from_user}')

all_orders =f"<a href='{getenv("API")}/admin/currency/orders/'>Все заказы</a>"

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
    await orders.order_send_message()


@router.message(F.text == "on_post_db")
async def echo_handler(message: types.Message):
    logger.info(message.text)
    await post_db.post_db()



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
