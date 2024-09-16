from sqlalchemy.ext.asyncio import AsyncSession
from models.match_results import MatchResults
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
from typing import List

class MatchResultsRepository:
    def __init__(self, db: AsyncSession):
        # inject db
        self.db = db

    async def create_match_results(self, match_results: List[MatchResults]) -> bool:
        pass