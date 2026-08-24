from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

from os import getenv


from allkeyboard.all_keyboard import accept_order
from aiogram import Bot
from loguru import logger

@logger.catch
async def notify_cashiers_new_order(order_data: dict):
    """
    Отправляет уведомление кассирам о новом заказе сразу после его создания.
    
    order_data должен содержать:
    - order_id
    - address
    - currency_name
    - amount
    - rate
    - phone
    """
    bot = Bot(token=getenv("TOKEN"), default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))

    try:
        data_chat_id = getenv("OPTOVAYAKASSA")
        
        order_id = f"{order_data.get('order_id', '0')}".zfill(4)
        address = order_data.get('address', 'Unknown')
        currency_name = order_data.get('currency_name', 'Unknown')
        amount = order_data.get('amount', 0)
        rate = order_data.get('rate', 0)
        phone = order_data.get('phone', 'Unknown')
        
        rate_str = str(rate).rstrip('0').rstrip('.')

        logger.info(order_data)
        
        send_order = f"🛎 <b>Нове замовлення</b> {order_id}\n\n🏦{address}\n{currency_name} \n🫳{amount} по {rate_str} \nCума <b>{amount}</b>\n\n📲+{phone}"
        
        async with bot.session:
            await bot.send_message(
                chat_id=data_chat_id,
                text=send_order,
                reply_markup=accept_order(order_id)
            )
            logger.success(f"Уведомление о заказе {order_id} отправлено кассирам")
            
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления кассирам: {e}")