import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


logger = logging.getLogger(name)


# PostgreSQL asinxron ulanish dvigateli
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,

    # Eskirgan yoki uzilgan ulanishlarni tekshirish
    pool_pre_ping=True,

    # Ulanishlar havzasi
    pool_size=5,
    max_overflow=10,

    # Ulanish olish uchun maksimal kutish vaqti
    pool_timeout=30,

    # Ulanishlarni vaqti-vaqti bilan yangilash
    pool_recycle=1800,

    # Ulanishlar havzasini dastur to'xtaganda yopish
    pool_use_lifo=True,
)


# Asinxron sessiyalar fabrikasi
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Ma'lumotlar bazasi sessiyasini taqdim etadi.

    Xatolik yuz bersa, ochiq tranzaksiya bekor qilinadi.
    Sessiya har qanday holatda yopiladi.

    Commit biznes operatsiyasining o'zida,
    tegishli service qatlamida bajariladi.
    """

    async with AsyncSessionFactory() as session:
        try:
            yield session

        except Exception:
            await session.rollback()

            logger.exception(
                "Ma'lumotlar bazasi sessiyasida xatolik."
            )

            raise


async def close_database() -> None:
    """
    Dastur to'xtatilganda ma'lumotlar bazasi
    ulanishlarini xavfsiz yopadi.
    """

    try:
        await engine.dispose()

        logger.info(
            "PostgreSQL ulanishlari muvaffaqiyatli yopildi."
        )

    except Exception:
        logger.exception(
            "PostgreSQL ulanishlarini yopishda xatolik."
        )

        raise
