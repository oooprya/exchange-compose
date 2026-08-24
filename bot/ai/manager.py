from ai.memory import memory
from ai.assistant import assistant
from ai.prompts import SYSTEM_PROMPT
from config import db


class AIManager:

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

                При оформлении брони ИСПОЛЬЗУЙ эти данные автоматически.
                НЕ спрашивай имя и телефон - они уже известны.

                Упомяни его по имени для персонализации: "Добрый день, {name}!"
                """

        return prompt


manager = AIManager()
