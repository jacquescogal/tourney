from fastapi import APIRouter, Depends, Response, HTTPException
from src.database.database import Database
from src.schemas.user import UserCreateRequest
from src.redis.session import SessionStorage
from src.controllers.authentication import AuthController
from src.repositories.user import UserRepository
from src.redis.lock import DistributedLock, USER_LOCK_KEY
user_router = APIRouter()
database = Database.get_instance()
session_storage = SessionStorage.get_instance()

@user_router.post("/users", tags=["user"])
async def create_user(user: UserCreateRequest, db = Depends(database.get_session)):
    """
    API endpoint to create session.
    """
    auth_controller = AuthController(UserRepository(db), session_storage, user_lock=DistributedLock(USER_LOCK_KEY))
    await auth_controller.create_user(
        username=user.username,
        password=user.password,
        role=user.user_role,
        team_id=user.team_id
    )
    return {"detail":"user created successfully"}


# TODO: middleware to check session token

# @session_router.delete("/sessions", tags=["session"])
# async def delete_session(response: Response):
#     """
#     API endpoint to delete session.
#     """
#     response.delete_cookie(key="session_token")
    
#     auth_controller = AuthController(UserRepository(db), session_storage)
#     session_token = request.cookies.get("session_token")

#     return {"detail":"session deleted successfully"}