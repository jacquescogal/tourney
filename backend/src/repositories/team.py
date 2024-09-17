from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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
                await self.rollback_transaction()
                raise HTTPException(status_code=400, detail=f"Team already exists: {e.params[0]}")
        except SQLAlchemyError as e:
            await self.rollback_transaction()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except HTTPException as e:
            await self.rollback_transaction()
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        return True
    
    async def get_teams_by_team_names(self, team_names: List[str]) -> List[Team]:
        """
        Checks the existence of teams by their names.

        Args:
        team_names: List[str]: A list of team names to check.

        Returns:
        existing_teams: List[str]: A list of team names that already exist in the database.

        Raises:
        SQLAlchemyError: If any error occurs during the database query.
        """
        try:
            query = select(Team.team_id,Team.team_name, Team.registration_date_unix, Team.group_number).where(Team.team_name.in_(team_names))
            result = await self.db.execute(query)
            existing_teams = [Team(team_id=row[0], team_name=row[1], registration_date_unix=row[2], group_number=row[3]) for row in result.fetchall()]

            return existing_teams
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    async def get_teams_by_group(self, group_filter_filter:int = None) -> List[Team]:
        """
        Gets teams by their group number.

        Args:
        group_filter: int: The group number to filter by.

        Returns:
        teams: List[Team]: A list of teams that belong to the group number.

        Raises:
        SQLAlchemyError: If any error occurs during the database query.
        """
        try:
            query = select(Team.team_id,Team.team_name, Team.registration_date_unix, Team.group_number)
            if group_filter_filter != None:
                query = query.where(Team.group_number == group_filter_filter)
            result = await self.db.execute(query)
            return [Team(team_id=row[0], team_name=row[1], registration_date_unix=row[2], group_number=row[3]) for row in result.fetchall()]
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
