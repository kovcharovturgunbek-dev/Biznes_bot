import asyncio
from aiogram import Bot, Dispatcher

from app.cache.redis import close_redis
from app.core.logging import setup_logging
from app.core.config import settings

# Routerlaringizni shu yerga import qilasiz va ulaysiz:
# Masalan: from app.routerlar import main_router


async def asosiy() -> None:
    setup_logging()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Routerlarni ulash:
    # dp.include_router(main_router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await close_redis()
        # Ma'lumotlar bazasini yopish (agar funksiya bo'lsa):
        # await ma'lumotlar_bazasini_yopish()


if __name__ == "__main__":
    asyncio.run(asosiy())
