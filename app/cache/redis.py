import logging
from typing import Optional

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings


logger = logging.getLogger(name)

# Redis mijozini yaratish.
# Ulanish birinchi Redis so'rovi yuborilganda amalga oshadi.
redis: Redis = Redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    health_check_interval=30,
    retry_on_timeout=True,
    socket_keepalive=True,
    max_connections=20,
)

# Redis hozir ishlayaptimi?
_redis_available: bool = False


async def check_redis_connection() -> bool:
    """
    Redis serveri bilan aloqani tekshiradi.

    Redis ishlayotgan bo'lsa True,
    ulanishda xatolik bo'lsa False qaytaradi.

    Redis ishlamasligi asosiy ma'lumotlar bazasi
    va savdo jarayonlarini to'xtatmasligi kerak.
    """
    global _redis_available

    try:
        response = await redis.ping()

        _redis_available = bool(response)

        if _redis_available:
            logger.info("Redis bilan ulanish muvaffaqiyatli.")

        return _redis_available

    except (RedisError, OSError, TimeoutError) as exc:
        _redis_available = False

        logger.warning(
            "Redis bilan aloqa mavjud emas. "
            "Tizim Redis talab qilmaydigan jarayonlarni davom ettiradi. "
            "Xatolik: %s",
            exc,
        )

        return False

    except Exception:
        _redis_available = False

        logger.exception(
            "Redis ulanishini tekshirishda kutilmagan xatolik."
        )

        return False


def is_redis_available() -> bool:
    """
    Redisning oxirgi tekshiruvdagi holatini qaytaradi.
    """
    return _redis_available


async def get_redis() -> Optional[Redis]:
    """
    Redis ishlayotgan bo'lsa mijozni qaytaradi.
    Redis mavjud bo'lmasa None qaytaradi.

    Redis majburiy bo'lmagan funksiyalar uchun ishlatiladi.
    """
    if not _redis_available:
        return None

    return redis


async def close_redis() -> None:
    """
    Dastur to'xtatilganda Redis ulanishini xavfsiz yopadi.
    """
    global _redis_available

    try:
        await redis.aclose()
        logger.info("Redis ulanishi muvaffaqiyatli yopildi.")

    except (RedisError, OSError, TimeoutError) as exc:
        logger.warning(
            "Redis ulanishini yopishda xatolik: %s",
            exc,
        )

    except Exception:
        logger.exception(
            "Redisni yopishda kutilmagan xatolik."
        )

    finally:
        _redis_available = False
