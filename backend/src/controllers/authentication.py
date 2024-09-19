from src.repositories.user import UserRepository
from fastapi import HTTPException
from src.models.user import User
from src.redis.lock import DistributedLock
from src.redis.session import SessionStorage
from src.utils.crypto import encrypt_password, check_password
from src.schemas.user import UserSessionStoreValue, UserRole, SessionTokenAndUserSession
class AuthController:
    def __init__(self, user_repository: UserRepository, session_store: SessionStorage, user_lock: DistributedLock = None):
        # inject repositories
        self.user_repository = user_repository

        # store sessions in cache
        self.session_store = session_store

        # lock to prevent inconsistency with async writes
        self.user_lock = user_lock

    async def create_session(self, username: str, password: str, ttl: int = 60 * 60 * 24) -> SessionTokenAndUserSession:
        """
        create_session authenticates the user and returns a session token if successful.
        """
        user:User = await self.user_repository.get_user_by_username(username)
        if user is None:
            raise HTTPException(status_code=400, detail="Wrong username or password")
        if check_password(password, user.hashed_password) is False:
            raise HTTPException(status_code=400, detail="Wrong username or password")
        user_session_store_value: UserSessionStoreValue = UserSessionStoreValue(user_id=user.user_id, user_role=user.user_role, team_id=user.team_id)
        session_token = await self.session_store.create_session(user_session_store_value)
        return SessionTokenAndUserSession(
            session_token=session_token,
            user_session=user_session_store_value
        )
    
    async def create_user(self, username: str, password: str, role: UserRole, team_id: int = None) -> bool:
        """
        create_user creates a new user.
        """
        hashed_password = encrypt_password(password)
        user = User(user_name=username, hashed_password=hashed_password, user_role=role, team_id=team_id)

        if not await self.user_lock.get():
            raise HTTPException(status_code=500, detail="Failed to get user lock")
        try:
            await self.user_repository.create_user(user)
            await self.user_repository.commit_transaction()
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        finally:
            await self.user_lock.give()
        return True