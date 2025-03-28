#!/bin/bash
import asyncio
import requests
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.client.bot import DefaultBotProperties
from functions.all_fun import status_orders
from os import getenv
from aiogram import Bot
from loguru import logger


orders_url = f'{getenv("API")}/api/v1/orders/?status=new'
status_accepted = f'{getenv("API")}/api/v1/orders/?status=accepted'


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
                    chat_id=getenv("PrivatObmenOd"),
                    # chat_id=getenv("ULIA"), PrivatObmenOd Admin Head
                    text=send_order,
                    reply_markup=accept_order(order.get('id'))
                )
                await status_orders(order.get('id'), "ordersent")
                logger.debug(f'{meg.text}')
            except:
                logger.debug(f"замовлення нема")

        # Ждем 1 минуту
        await asyncio.sleep(60)