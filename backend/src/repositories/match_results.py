from sqlalchemy.ext.asyncio import AsyncSession
from src.models.match_results import MatchResults
from src.models.game_match import GameMatch
from src.models.team import Team
from src.schemas.match_results import MatchResultDetailed
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
from typing import List
from sqlalchemy.future import select

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
    
    async def get_match_results_by_round(self, round_number: int, group_number_filter: int = None) -> List[MatchResultDetailed]:
        try:
            # join MatchResults with GameMatch to get the round_number
            # if group number is None, then return result, else join with Team and filter by group_number
            query = select(Team.group_number, MatchResults.match_id, Team.team_name, MatchResults.team_id, MatchResults.goals_scored, Team.registration_date_unix).join(Team, Team.team_id == MatchResults.team_id, isouter=True).join(GameMatch, GameMatch.match_id == MatchResults.match_id, isouter=True).where(GameMatch.round_number == round_number)
            if group_number_filter != None:
                query = query.where(Team.group_number == group_number_filter)
            result = await self.db.execute(query)
            return [MatchResultDetailed(
                group_number=row[0],
                match_id=row[1],
                team_name=row[2],
                team_id=row[3],
                goals_scored=row[4],
                join_date_unix=row[5]
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
