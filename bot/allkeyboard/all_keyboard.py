from loguru import logger
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove


@logger.catch
def get_contact():
    kb = [
        [
            KeyboardButton(text='📲 Надіслати свій контакт',
                           request_contact=True)
        ],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True, one_time_keyboard=True,
        input_field_placeholder="натисніть кнопку 📲 Надіслати свій контакт"
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
        [
            InlineKeyboardButton(text="🚶🏽 Не пришел",
                                 callback_data=f"noshow_{order_id}"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@logger.catch
def order_accepted():
    kb = [
        [KeyboardButton(text='ℹ️ Прийняте замовлення',
                        callback_data=f"apiaccepted")],
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True, one_time_keyboard=True
    )
    return keyboard



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