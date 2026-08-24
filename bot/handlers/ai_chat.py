from aiogram import Router
from aiogram.types import Message

from ai.manager import manager


router = Router()


# Хэндлер ловит ВСЕ входящие сообщения из бизнес-чатов
# @router.business_message()
# async def catch_business_message(message: Message):
#     # Текст полученного сообщения
#     user_text = message.text
#     # Имя отправителя
#     sender_name = message.from_user.first_name

#     print(f"Новое сообщение от {sender_name}: {user_text}")

#     # Пример ответа на конкретное слово
#     if user_text and "привет" in user_text.lower():
#         await message.answer("Здравствуйте!")

#     else:
#         await message.answer(f"Дякуємо {sender_name} за довіру і що обрали саме нас. Будемо вдячні, якщо підпишитесь 👉@private_obmen")

@router.business_message()
async def ai_chat(message: Message):
    answer = await manager.chat(
        chat_id=str(message.from_user.id),
        text=message.text,
    )

    await message.answer(answer, parse_mode="HTML")
