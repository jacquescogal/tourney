from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import match_core
from src.database.database import Database
from src.routers import team
from src.routers import match_core
from src.routers import user
from src.routers import session
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.redis.session import SessionStorage

app = FastAPI()

database: Database = Database.get_instance()

async def lifespan(_):
    await database.create_tables()
    yield
    await database.engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(team.team_router)
app.include_router(match_core.match_router)
app.include_router(user.user_router)
app.include_router(session.session_router)

class CookieSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_token = request.cookies.get("session_token")
        session_store = SessionStorage.get_instance()
        user_session = await session_store.get_session(session_token)
        request.state.user_session = user_session
        response = await call_next(request)
        return response
    
app.add_middleware(CookieSessionMiddleware)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health():
    return {"status": "ok"}