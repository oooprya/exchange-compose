import asyncio
import logging
from config import TELEGRAM_TOKEN
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import router


async def main():
    # await on_startup()
    try:
        bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(
            parse_mode=ParseMode.HTML))
        dp = Dispatcher(storage=MemoryStorage())
        dp.include_router(router)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types())
    finally:
        pass
        # await on_shutdown()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
