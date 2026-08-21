import asyncio
import logging
from aiogram import Bot, Dispatcher
from fastapi import FastAPI
import uvicorn
import threading

from app.cache.redis import close_redis
from app.core.logging import setup_logging
from app.core.config import settings

# FastAPI ilovasini yaratamiz
app_web = FastAPI()

@app_web.get("/")
def root():
    return {"status": "Bot ishlayapti!"}

def start_fastapi():
    # Render talab qiladigan portni ochish
    uvicorn.run(app_web, host="0.0.0.0", port=10000, log_level="warning")

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


if __name__ == "__main__":
    # 1. Oldin veb-serverni alohida oqimda (thread) ishga tushiramiz (portni darhol band qiladi)
    server_thread = threading.Thread(target=start_fastapi, daemon=True)
    server_thread.start()

    # 2. Keyin telegram botni ishga tushiramiz
    try:
        asyncio.run(asosiy())
    except KeyboardInterrupt:
        pass
