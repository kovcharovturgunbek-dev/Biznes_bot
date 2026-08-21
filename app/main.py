import asyncio

from aiogram import Bot, Dispatcher

from app.cache.redis import close_redis
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import close_database


async def main() -> None:
    setup_logging()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await close_redis()
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())
