from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database.database import Database
from src.routers import team, match_results

database: Database = Database.get_instance()

async def lifespan(_):
    await database.create_tables()
    yield
    await database.engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(team.team_router)
app.include_router(match_results.match_results_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health():
    return {"status": "ok"}