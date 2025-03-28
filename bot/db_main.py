import psycopg2
import os
from loguru import logger
from typing import Tuple, Optional, Any


class Database:
    def __init__(
        self,
        host: str = os.getenv('DB_HOST', 'localhost'),
        database: str = os.getenv('DB_NAME', 'your_database'),
        user: str = os.getenv('DB_USER', 'your_username'),
        password: str = os.getenv('DB_PASSWORD', 'your_password'),
        port: str = os.getenv('DB_PORT', '5432')
    ):
        """Функция для подключения к базе данных в Docker"""
        self.conn = None
        self.cursor = None

        connection_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port
        }

        logger.info(f"Попытка подключения к базе: {host}:{port}")

        try:
            self.conn = psycopg2.connect(**connection_params)
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            logger.success("Успешное подключение к базе данных")
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            logger.error(f"Параметры подключения: {connection_params}")
            raise ConnectionError(f"Не удалось подключиться к базе данных: {e}")

    def _ensure_connection(self):
        """Проверка и восстановление соединения"""
        try:
            # Проверяем, что соединение существует и работает
            if self.conn is None or self.conn.closed:
                logger.warning("Соединение с базой данных закрыто. Переподключение...")
                self._connect()

            # Дополнительная проверка активности курсора
            if self.cursor is None or self.cursor.closed:
                self.cursor = self.conn.cursor()
        except Exception as e:
            logger.error(f"Ошибка при восстановлении соединения: {e}")
            raise

    def user_exists(self, chat_id: int) -> Tuple[bool, Optional[Any]]:
        """Проверка существования пользователя"""
        try:
            self._ensure_connection()
            self.cursor.execute("SELECT * FROM currency_users WHERE chat_id = %s;", (chat_id,))
            result = self.cursor.fetchone()
            return bool(result), result
        except Exception as e:
            logger.error(f"Ошибка при проверке пользователя: {e}")
            return False, None

    def get_orders(self, clients_telephone: str) -> Tuple[bool, Optional[Any]]:
        try:
            self._ensure_connection()
            self.cursor.execute("SELECT * FROM currency_orders WHERE clients_telephone = %s;", (clients_telephone,))
            result = self.cursor.fetchone()
            return bool(result), result
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            return False, None

    def add_user(self, chat_id: int, chat_id_name: str, role: str, clients_telephone: str) -> bool:
        """Добавление нового пользователя"""
        try:
            self._ensure_connection()
            self.cursor.execute(
                'INSERT INTO currency_users (chat_id, chat_id_name, role, clients_telephone) VALUES (%s, %s, %s, %s)',(chat_id, chat_id_name, role, clients_telephone)
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя: {e}")
            return False

    def update_phone_user(self, chat_id: int, clients_telephone: str) -> bool:
        """Добавление clients_telephone"""
        try:
            self._ensure_connection()
            self.cursor.execute(
                'UPDATE currency_users SET clients_telephone = %s WHERE  chat_id = %s', (clients_telephone, chat_id,)
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            return False

    def close(self):
        """Закрытие соединения с базой данных"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            logger.info("Соединение с базой данных закрыто")
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединения: {e}")

    def __del__(self):
        """Деструктор для автоматического закрытия соединения"""
        self.close()