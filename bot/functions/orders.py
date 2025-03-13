#!/bin/bash
import asyncio
import requests
from dotenv import load_dotenv
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import time
from aiogram.client.bot import DefaultBotProperties
from os import getenv
from datetime import timedelta
from aiogram import Bot
from loguru import logger


orders_url = f'https://private-api-amk6.onrender.com/api/v1/orders/?status=new'
status_accepted = f'https://private-api-amk6.onrender.com/api/v1/orders/?status=accepted'


load_dotenv('bot/.env')

logger.add("cron.log", colorize=True,
           format="{time:YYYY-MM-DD HH:mm:ss} {name} {line} {level} {message} ", level="DEBUG", rotation="500 KB", compression="zip")


@logger.catch
def accept_order(order_id):
    buttons = [
        [
            InlineKeyboardButton(text="✔️ Прийняти замовлення",
                                 callback_data=f"accepted_{order_id}"),
        ],
        [
            InlineKeyboardButton(text="Відмінити замовлення",
                                 callback_data=f"cancel_{order_id}"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard





@logger.catch
async def status_orders(data_id, data_status):
    headers = {"Authorization": "ApiKey oooprya:qwe123"}
    order_patch = {"status": f"{data_status}"}
    x = requests.patch(f"https://private-api-amk6.onrender.com/api/v1/orders/{data_id}/",
                       json=order_patch, headers=headers)
    logger.debug(x.status_code)
    return order_patch

@logger.catch
async def order_send_message():
    """ Получаем новый заказ из сайта по API и отправляю Менеджеру """
    bot = Bot(token=getenv("TOKEN"), default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))

    while True:
        res = requests.get(orders_url)
        data = res.json()
        async with bot.session:  # or `bot.context()`
            try:
                order = data.get('objects')[0]
                logger.debug(f"{order}")
                id = f"{order.get('id')}".zfill(4)
                send_order = f"🛎 <b>Нове замовлення</b> {id}\n\n🏦{order.get('address_exchanger')}\n{order.get('currency_name')} \n🫳{order.get('buy_or_sell')} по {order.get('exchange_rate')} \nCума <b>{order.get('order_sum')}</b>\n\n📲{order.get('clients_telephone')}"
                # logger.debug(await bot.get_me())

                meg = await bot.send_message(
                    chat_id=getenv("Admin"),
                    # chat_id=getenv("ULIA"), PrivatObmenOd Admin Head
                    text=send_order,
                    reply_markup=accept_order(order.get('id'))
                )
                await status_orders(order.get('id'), "ordersent")
                logger.debug(meg.text)
            except:
                logger.debug(f"замовлення нема")

                # await bot.send_message(
                #     chat_id=getenv("PrivatObmenOd"),
                #     text=send_order,
                #     reply_markup=accept_order(order.get('id'))
                # )
        # Ждем 1 минуту
        time.sleep(60)




if __name__ == '__main__':
    asyncio.run(order_send_message())
