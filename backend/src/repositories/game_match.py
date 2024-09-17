from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.game_match import GameMatch
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
from typing import List

class GameMatchRepository:
    def __init__(self, db: AsyncSession):
        # inject db
        self.db = db

    async def create_game_matches(self, game_matches: List[GameMatch]) -> bool:
        """
        Creates new game matches as batch.
        """
        try:
            for game_match in game_matches:
                self.db.add(game_match)
            try:
                await self.db.flush()
            except IntegrityError as e:
                await self.rollback_transaction()
                raise HTTPException(status_code=400, detail=f"Game Match already exists: {e.params[0]}")
        except SQLAlchemyError as e:
            await self.rollback_transaction()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except HTTPException as e:
            await self.rollback_transaction()
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        return True

    async def get_game_matches_by_ids(self, match_ids: List[int]) -> GameMatch:
        """
        Gets game matches by their ids.
        """
        try:
            query = select(GameMatch.match_id).where(GameMatch.match_id.in_(match_ids))
            result = await self.db.execute(query)
            existing_teams = [row[0] for row in result.fetchall()]

            return existing_teams
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    async def rollback_transaction(self) -> bool:
        await self.db.rollback()
        return True

    async def commit_transaction(self) -> bool:
        try:
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        return True
