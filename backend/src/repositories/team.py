from sqlalchemy.ext.asyncio import AsyncSession
from src.models.team import Team
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
from typing import List

class TeamRepository:
    def __init__(self, db: AsyncSession):
        # inject db
        self.db = db

    async def create_teams(self, teams: List[Team]) -> bool:
        """
        Creates new team as batch.
        Is transactional, if one team already exists, rollbacks whole transaction.

        Args:
        team_name: str
        registration_date_unix: int
        group_number: int

        Returns:
        is_successful: bool

        Raises:
        IntegrityError: If one of the team names already exists
        SQLAlchemyError: If any other error
        """
        try:
            for team in teams:
                self.db.add(team)
            try:
                await self.db.flush()
            except IntegrityError as e:
                await self.db.rollback()
                raise HTTPException(status_code=400, detail=f"Team already exists: {e.params[0]}")
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except HTTPException as e:
            await self.db.rollback()
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        return True
