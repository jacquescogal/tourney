from redis import asyncio as aioredis
import uuid
import asyncio
import time
from config import Settings

# Constant lock keys
TEAM_LOCK_KEY = "team_lock"
MATCH_LOCK_KEY = "match_lock"


class DistributedLock:
    def __init__(self, lock_key: str, ttl: int = 5):
        self.redis_url = Settings.get_instance().redis_url
        self.lock_key = lock_key
        self.ttl = ttl
        self.lock_value = str(uuid.uuid4()) 
        # unique value for the lock, so no deletion by other clients
        # eg. one client finished task and wants to give back though their lock_key had expired

    async def get(self, timeout_seconds: int = 1, interval: float = 0.5) -> bool:
        start_time = time.time()
        async with aioredis.from_url(self.redis_url) as redis:
            # if lock is not set, set it and return True
            # if lock is already set, return False, retry after some time
            while time.time() - start_time < timeout_seconds:
                result = await redis.set(self.lock_key, self.lock_value, ex=self.ttl, nx=True)
                if result:
                    return True
                await asyncio.sleep(interval)
            return False
                

    async def give(self) -> bool:
        async with aioredis.from_url(self.redis_url) as redis:
            # give back lock if it belongs to the client
            lock_value = await redis.get(self.lock_key)
            if lock_value and lock_value.decode() == self.lock_value:
                await redis.delete(self.lock_key)
                return True
            return False