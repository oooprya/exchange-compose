import asyncio
from collections import defaultdict

from ai.memory import memory
from ai.assistant import assistant
from ai.prompts import SYSTEM_PROMPT
from config import db

MESSAGE_DELAY = 8.0


class AIManager:

    def __init__(self):
        self._pending_text = defaultdict(list)
        self._pending_tasks = {}

    async def chat(self, chat_id, text):
        memory.add(chat_id, "user", text)

        # 🔍 Проверяем, есть ли клиент в БД
        user_exists, user_data = db.user_exists(str(chat_id))

        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt(user_exists, user_data)
            }
        ]

        messages.extend(memory.get(chat_id))

        answer = await assistant.chat(
            messages,
            chat_id=chat_id
        )

        memory.add(chat_id, "assistant", answer)

        return answer

    async def chat_delayed(self, chat_id, text, delay=MESSAGE_DELAY):
        """Объединяет короткие сообщения до паузы клиента."""
        self._pending_text[chat_id].append(text)

        previous_task = self._pending_tasks.get(chat_id)
        if previous_task:
            previous_task.cancel()

        task = asyncio.create_task(
            self._flush_after_delay(chat_id, delay)
        )
        self._pending_tasks[chat_id] = task

        try:
            return await task
        except asyncio.CancelledError:
            # Это сообщение продолжилось следующим сообщением клиента.
            return None

    async def _flush_after_delay(self, chat_id, delay):
        await asyncio.sleep(delay)

        texts = self._pending_text.pop(chat_id, [])
        self._pending_tasks.pop(chat_id, None)

        if not texts:
            return None

        return await self.chat(
            chat_id,
            "\n".join(texts),
        )

    def _get_system_prompt(self, user_exists: bool, user_data: tuple = None) -> str:
        """Генерируем промпт с информацией о клиенте"""
        prompt = SYSTEM_PROMPT

        if user_exists and user_data:
            # user_data структура: (id, chat_id, chat_id_name, role, clients_telephone)
            name = user_data[2]  # chat_id_name
            phone = user_data[4]  # clients_telephone

            if name and phone:
                prompt += f"""

                ==================================================
                ИНФОРМАЦИЯ О ПОВТОРНОМ КЛИЕНТЕ
                ==================================================

                Этот клиент уже заказывал раньше.

                Его данные:
                - Имя: {name}
                - Телефон: {phone}

                Используй эти данные только как справочную информацию.
                Перед каждой новой бронью обязательно спроси имя и телефон
                человека, на которого оформляется бронь.
                Не подставляй имя или телефон автоматически и не используй
                имя профиля в приветствии без подтверждения клиента.
                """

        return prompt


manager = AIManager()
