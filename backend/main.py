from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import match_core
from src.database.database import Database
from src.routers import team
from src.routers import match_core
from src.routers import user
from src.routers import session
from src.middleware.middleware import CookieSessionMiddleware
import logging

# Configure logging
logging.basicConfig(
    filename='log.txt',  # Log to log.txt file
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
    level=logging.INFO  # Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
)

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
app.add_middleware(CookieSessionMiddleware)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
    "http://localhost:5173",  # Frontend origin
],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health():
    return {"status": "ok"}