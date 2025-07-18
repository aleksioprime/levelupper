from datetime import datetime
import redis.asyncio as redis


class RedisSyncStateManager:
    """
    Менеджер хранения времени последней синхронизации в Redis.
    Используется для инкрементальной синхронизации в Airflow DAG.
    """

    def __init__(self, redis_client: redis.Redis, key: str):
        self.redis = redis_client
        self.key = key  # e.g. "sync:courses_full:last_updated_at"

    async def get_last_sync_time(self) -> datetime:
        value = await self.redis.get(self.key)
        if value is None:
            # если ни разу не синхронизировали — берем "с нуля"
            return datetime(2000, 1, 1)
        return datetime.fromisoformat(value.decode("utf-8"))

    async def set_last_sync_time(self, time: datetime):
        await self.redis.set(self.key, time.isoformat())
