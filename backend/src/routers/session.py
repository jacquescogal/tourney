from fastapi import APIRouter, Depends, Response, HTTPException
from src.database.database import Database
from src.schemas.user import UserLoginRequest
from src.redis.session import SessionStorage
from src.controllers.authentication import AuthController
from src.repositories.user import UserRepository
from src.redis.lock import DistributedLock, USER_LOCK_KEY
session_router = APIRouter()
database = Database.get_instance()
session_storage = SessionStorage.get_instance()

@session_router.post("/sessions", tags=["session"])
async def create_session(user: UserLoginRequest, response: Response, db = Depends(database.get_session)):
    """
    API endpoint to create session.
    """
    auth_controller = AuthController(UserRepository(db), session_storage)
    cookie_ttl = 60 * 60 * 24
    session_token = await auth_controller.create_session(username=user.username, password=user.password, ttl=cookie_ttl)
    response.set_cookie(key="session_token", value=session_token, max_age=cookie_ttl,httponly=True,
    secure=False,  # False for local dev over HTTP
    path="/"       # Make sure it's available for the entire app
)
    return {"detail":"session created successfully", "session_token":session_token}



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