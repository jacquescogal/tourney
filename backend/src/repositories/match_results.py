from sqlalchemy.ext.asyncio import AsyncSession
from src.models.match_results import MatchResults
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
from typing import List

class MatchResultsRepository:
    def __init__(self, db: AsyncSession):
        # inject db
        self.db = db

    async def create_match_results(self, match_results: List[MatchResults]) -> bool:
        try:
            for match_result in match_results:
                self.db.add(match_result)
            try:
                await self.db.flush()
            except IntegrityError as e:
                await self.rollback_transaction()
                raise HTTPException(status_code=400, detail=f"Match Result already exists: {e.params[0]}")
        except SQLAlchemyError as e:
            await self.rollback_transaction()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except HTTPException as e:
            await self.rollback_transaction()
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        return True
    
    async def rollback_transaction(self) -> bool:
        await self.db.rollback()
        return True

    async def commit_transaction(self) -> bool:
        try:
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except HTTPException as e:
            await self.db.rollback()
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        return True
