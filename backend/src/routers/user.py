from fastapi import APIRouter, Depends, Response, HTTPException
from src.database.database import Database
from src.schemas.user import UserCreateRequest
from src.redis.session import SessionStorage
from src.controllers.authentication import AuthController
from src.repositories.user import UserRepository
from src.redis.lock import DistributedLock, USER_LOCK_KEY
from src.schemas.user import UserRole
from fastapi import Request
user_router = APIRouter()
database = Database.get_instance()
session_storage = SessionStorage.get_instance()

@user_router.post("/users", tags=["user"])
async def create_user(request:Request, user: UserCreateRequest, db = Depends(database.get_session)):
    """
    API endpoint to create users.
    """
    if request.state.user_session is None or request.state.user_session.user_role != UserRole.admin:
        return HTTPException(status_code=401, detail="Unauthorized")
    auth_controller = AuthController(UserRepository(db), session_storage, user_lock=DistributedLock(USER_LOCK_KEY))
    await auth_controller.create_user(
        username=user.username,
        password=user.password,
        role=user.user_role,
        team_id=user.team_id
    )
    return {"detail":"user created successfully"}
