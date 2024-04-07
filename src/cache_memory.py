from redis.asyncio import ConnectionPool, Redis

from src.config import settings


class CacheMemory:
    def __init__(self, host: str, port: int):
        self.pool = ConnectionPool(
            host=host,
            port=port,
            **{"decode_responses": True},
        )

    def pool_dependency(self) -> Redis:
        return Redis(connection_pool=self.pool)


cache_memory = CacheMemory(
    host=settings.redis.host,
    port=settings.redis.port,
)
