from src.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from src.models.team import Team
from src.models.game_match import GameMatch
from src.models.match_results import MatchResults
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
from typing import List, Dict
from src.schemas.team import TeamMatchUpDetail, TeamDetails

class UserRepository:
    def __init__(self, db: AsyncSession):
        # inject db
        self.db = db

    async def create_user(self, user: User) -> bool:
        """
        Creates a new user.

        Args:
        user: User

        Returns:
        is_successful: bool

        Raises:
        IntegrityError: If one of the user names already exists
        SQLAlchemyError: If any other error
        """
        try:
            self.db.add(user)
            try:
                await self.db.flush()
            except IntegrityError as e:
                await self.rollback_transaction()
                raise HTTPException(status_code=400, detail=f"User already exists: {e.params[0]}")
        except SQLAlchemyError as e:
            await self.rollback_transaction()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except HTTPException as e:
            await self.rollback_transaction()
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        return True
    
    async def get_user_by_username(self, username: str) -> User:
        """
        Gets user by username.

        Args:
        username: str

        Returns:
        user: User or None if not found

        Raises:
        SQLAlchemyError: If any error occurs during the database query.
        """
        try:
            query = select(User).where(User.user_name == username)
            result = await self.db.execute(query)
            user = result.scalars().first()
            return user
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
    async def delete_all_users_except_admin(self) -> bool:
        """
        Deletes all users.

        Returns:
        is_successful: bool
        """
        try:
            query = delete(User).where(User.user_name != "admin")
            await self.db.execute(query)
            return True
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
