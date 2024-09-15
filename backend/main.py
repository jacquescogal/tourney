from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database.database import Database

database: Database = Database.get_instance()

async def lifespan(_):
    await database.create_tables()
    yield
    await database.engine.dispose()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health():
    database = await Database.get_instance()
    return {"status": "ok"}