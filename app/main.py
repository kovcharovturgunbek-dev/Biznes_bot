import asyncio
import threading
from aiogram import Bot, Dispatcher
from fastapi import FastAPI
import uvicorn

from app.cache.redis import close_redis
from app.core.logging import setup_logging
from app.core.config import settings

# Render port talabini qondirish uchun kichik FastAPI server
app_web = FastAPI()

@app_web.get("/")
def root():
    return {"status": "Bot ishlayapti!"}

def run_web():
    uvicorn.run(app_web, host="0.0.0.0", port=10000)

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
    # Veb serverni alohida oqimda ishga tushiramiz (Render portni ko'rishi uchun)
    threading.Thread(target=run_web, daemon=True).start()
    
    # Telegram botni ishga tushiramiz
    asyncio.run(asosiy())
