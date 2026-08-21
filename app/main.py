import asyncio
import os
import threading
from aiogram import Bot, Dispatcher
from fastapi import FastAPI
import uvicorn

from app.cache.redis import close_redis
from app.core.logging import setup_logging
from app.core.config import settings

# FastAPI ilovasi
app_web = FastAPI()

@app_web.get("/")
def root():
    return {"status": "Bot ishlayapti!"}

def start_fastapi():
    # Render o'zi beradigan PORT ni oladi (agar topolmasa 10000 ni oladi)
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app_web, host="0.0.0.0", port=port, log_level="warning")

async def asosiy() -> None:
    setup_logging()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await close_redis()

if __name__ == "__main__":
    # Veb serverni alohida oqimda ishga tushiramiz
    server_thread = threading.Thread(target=start_fastapi, daemon=True)
    server_thread.start()

    # Telegram botni ishga tushiramiz
    try:
        asyncio.run(asosiy())
    except KeyboardInterrupt:
        pass
