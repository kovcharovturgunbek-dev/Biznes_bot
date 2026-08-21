import asyncio
from aiogram import Bot, Dispatcher

from ilova.kesh.redis import close_redis
from ilova.yadro.konfiguratsiya import sozlamalar
from ilova.yadro.yog'och_kesish import sozlash_jurnali
from ilova.ma'lumotlar_bazasi.sessiya import ma'lumotlar_bazasini_yopish

# Routerlaringizni shu yerga import qilasiz va ulaysiz:
# Masalan: from ilova.routerlar import main_router


async def asosiy() -> None:
    sozlash_jurnali()

    bot = Bot(token=sozlamalar.bot_token)
    dp = Dispatcher()

    # Routerlarni ulash:
    # dp.include_router(main_router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await close_redis()
        await ma'lumotlar_bazasini_yopish()


if __name__ == "__main__":
    asyncio.run(asosiy())
