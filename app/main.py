import asyncio
import os
import threading

import uvicorn
from aiogram import Bot, Dispatcher
from fastapi import FastAPI

from app.cache.redis import close_redis
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import close_database
from app.handlers import router as main_router


app_web = FastAPI()


@app_web.get("/")
async def root():
    return {"status": "Bot ishlayapti!"}


def start_fastapi() -> None:
    port = int(os.environ.get("PORT", 10000))

    uvicorn.run(
        app_web,
        host="0.0.0.0",
        port=port,
        log_level="warning",
    )


async def asosiy() -> None:
    setup_logging()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    dp.include_router(main_router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await close_redis()
        await close_database()


if name == "main":
    server_thread = threading.Thread(
        target=start_fastapi,
        daemon=True,
    )
    server_thread.start()

    try:
        asyncio.run(asosiy())
    except KeyboardInterrupt:
        pass
