from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.redis.session import SessionStorage

class CookieSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_token = request.cookies.get("session_token")
        print("session_token", session_token)
        if not session_token:
            response = await call_next(request)
            return response
        session_store = SessionStorage.get_instance()
        user_session = await session_store.get_session(session_token)
        request.state.user_session = user_session
        response = await call_next(request)
        return response