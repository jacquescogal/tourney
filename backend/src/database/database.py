from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import Settings
from sqlalchemy.ext.declarative import declarative_base
from src.models import Base
from src.models.user import User
from src.models.team import Team
from src.models.game_match import GameMatch
from src.models.match_points import MatchPoints

class Database:
    instance = None

    def __init__(self, settings: Settings):
        settings = settings.get_instance()

        # connection pool
        self.engine = create_async_engine(
            settings.database_url,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            echo=False
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self):
        async with self.SessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = Database(Settings.get_instance())
        return cls.instance
    
