import logging
from redis.asyncio import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis ulanishini sozlash (timeout va health-check parametrlar bilan)
redis = Redis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    health_check_interval=30,
    retry_on_timeout=True,
)

async def check_redis_connection() -> bool:
    """
    Redis serveri ishlayotganini tekshirish (Ping).
    Agar Redis o'chgan bo'lsa, xatolikni logga yozib False qaytaradi (fallback uchun).
    """
    try:
        return await redis.ping()
    except Exception as e:
        logger.error(f"Redis ulanishini tekshirishda xatolik yuz berdi: {e}")
        return False


async def close_redis() -> None:
    """
    Dastur to'xtaganda (shutdown) Redis ulanishini xavfsiz yopish.
    """
    try:
        await redis.aclose()
    except Exception as e:
        logger.error(f"Redis ulanishini yopish vaqtida xatolik: {e}")
