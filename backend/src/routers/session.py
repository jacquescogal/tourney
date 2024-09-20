from fastapi import APIRouter, Depends, Response
from src.database.database import Database
from src.schemas.user import UserLoginRequest
from src.redis.session import SessionStorage
from src.controllers.authentication import AuthController
from src.repositories.user import UserRepository
from src.schemas.user import SessionTokenAndUserSession
from fastapi import Request
import logging
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
    session_token_and_user_session: SessionTokenAndUserSession = await auth_controller.create_session(username=user.username, password=user.password, ttl=cookie_ttl)
    response.set_cookie(key="session_token", value=session_token_and_user_session.session_token, max_age=cookie_ttl
    )
    logging.info(f"User {user.username} logged in")
    return session_token_and_user_session.user_session


@session_router.get("/sessions", tags=["session"])
async def get_session_user(request: Request):
    """
    API endpoint to get session.
    """
    return request.state.user_session

@session_router.delete("/sessions", tags=["session"])
async def delete_session(response: Response, request: Request):
    """
    API endpoint to delete session.
    """
    session_token = request.cookies.get("session_token")
    response.delete_cookie(key="session_token")
    logging.info(f"{request.state.user_session.user_role} logged out")
    return await session_storage.delete_session(session_token)