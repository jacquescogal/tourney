from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.game_match import GameMatch
from src.models.match_results import MatchResults
from src.models.team import Team
from src.schemas.match_results import MatchResultDetailed, MatchResultSparse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
from typing import List


class MatchRepository:
    def __init__(self, db: AsyncSession):
        # inject db
        self.db = db

    async def create_game_matches(self, match_count: int, round_number: int) -> List[int]: 
        """
        Creates new game matches as batch.

        Args:
        match_count: int
        round_number: int

        Returns:
        inserted_ids: List[int]: A list of match ids that were inserted.
        """
        try:
            matches_to_create = [
                GameMatch(round_number=round_number)
                for _ in range(match_count)
            ]
            self.db.add_all(matches_to_create)
            try:
                await self.db.flush()
                inserted_ids = [match.match_id for match in matches_to_create]
                return inserted_ids
            except IntegrityError as e:
                await self.rollback_transaction()
                raise HTTPException(status_code=400, detail=f"Game Match already exists: {e.params[0]}")
        except SQLAlchemyError as e:
            await self.rollback_transaction()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except HTTPException as e:
            await self.rollback_transaction()
            raise HTTPException(status_code=e.status_code, detail=e.detail)

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
    
    async def get_match_results_by_round(self, round_number: int, group_number_filter: int = None) -> List[MatchResultDetailed]:
        try:
            # join MatchResults with GameMatch to get the round_number
            # if group number is None, then return result, else join with Team and filter by group_number
            query = select(Team.group_number, MatchResults.match_id, Team.team_name, MatchResults.team_id, MatchResults.goals_scored, Team.registration_day_of_year).join(Team, Team.team_id == MatchResults.team_id, isouter=True).join(GameMatch, GameMatch.match_id == MatchResults.match_id, isouter=True).where(GameMatch.round_number == round_number)
            if group_number_filter != None:
                query = query.where(Team.group_number == group_number_filter)
            result = await self.db.execute(query)
            return [MatchResultDetailed(
                group_number=row[0],
                match_id=row[1],
                team_name=row[2],
                team_id=row[3],
                goals_scored=row[4],
                registration_day_of_year=row[5]
            ) for row in result.fetchall()]
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)
        
    async def get_matchups_by_round_and_team_ids(self, round_number: int, team_ids: List[int]) -> List[MatchResultSparse]:
        try:
            query = select(Team.team_name, MatchResults.match_id,  MatchResults.team_id).join(GameMatch, GameMatch.match_id == MatchResults.match_id).where(GameMatch.round_number == round_number).where(MatchResults.team_id.in_(team_ids)).join(Team, Team.team_id == MatchResults.team_id)
            result = await self.db.execute(query)
            return [MatchResultSparse(
                team_name=row[0],
                match_id=row[1],
                team_id=row[2]
            ) for row in result.fetchall()]
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

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