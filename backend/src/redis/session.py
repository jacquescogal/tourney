from redis import asyncio as aioredis
from src.schemas.user import UserSessionStoreValue
import uuid
import asyncio
import time
from config import Settings
from src.schemas.user import UserRole

SESSION_PREFIX = "session:"
ADMIN_SESSION_PREFIX = "admin_session:"

class SessionStorage:
    instance = None
    def __init__(self):
        self.redis_url = Settings.get_instance().redis_url

    @staticmethod
    def get_instance():
        if SessionStorage.instance is None:
            SessionStorage.instance = SessionStorage()
        return SessionStorage.instance
    
    async def create_session(self, user_session: UserSessionStoreValue, ttl: int = 60 * 60 * 24) -> str:
        session_id = SESSION_PREFIX + str(uuid.uuid4()) if user_session.user_role != UserRole.admin else ADMIN_SESSION_PREFIX + str(uuid.uuid4())
        async with aioredis.from_url(self.redis_url) as redis:
            await redis.set( session_id, user_session.model_dump_json(), ex=ttl)
        return session_id
    
    async def get_session(self, session_id: str) -> UserSessionStoreValue:
        async with aioredis.from_url(self.redis_url) as redis:
            session_data = await redis.get(session_id)
            if session_data:
                return UserSessionStoreValue.model_validate_json(session_data.decode())
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        async with aioredis.from_url(self.redis_url) as redis:
            return await redis.delete(session_id)
        
    async def delete_all_sessions_except_admin(self) -> bool:
        async with aioredis.from_url(self.redis_url) as redis:
            keys = await redis.keys(SESSION_PREFIX + "*")
            if keys:
                await redis.delete(*keys)
            return True
    