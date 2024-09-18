from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.team import Team
from src.models.game_match import GameMatch
from src.models.match_results import MatchResults
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
from typing import List, Dict
from src.schemas.team import TeamMatchUpDetail, TeamDetails

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
        registration_day_of_year: int
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
    async def get_teams(self) -> List[Team]:
        """
        Gets all teams.

        Returns:
        teams: List[Team]: A list of all teams.

        Raises:
        SQLAlchemyError: If any error occurs during the database query.
        """
        try:
            query = select(Team.team_id,Team.team_name, Team.registration_day_of_year, Team.group_number)
            result = await self.db.execute(query)
            return [Team(team_id=row[0], team_name=row[1], registration_day_of_year=row[2], group_number=row[3]) for row in result.fetchall()]
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
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
            query = select(Team.team_id,Team.team_name, Team.registration_day_of_year, Team.group_number).where(Team.team_name.in_(team_names))
            result = await self.db.execute(query)
            existing_teams = [Team(team_id=row[0], team_name=row[1], registration_day_of_year=row[2], group_number=row[3]) for row in result.fetchall()]

            return existing_teams
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    async def get_teams_by_ids(self, team_ids: List[int]) -> List[Team]:
        """
        Gets teams by their ids.

        Args:
        team_ids: List[int]: A list of team ids to get.

        Returns:
        existing_teams: List[Team]: A list of teams that exist in the database.

        Raises:
        SQLAlchemyError: If any error occurs during the database query.
        """
        try:
            query = select(Team.team_id,Team.team_name, Team.registration_day_of_year, Team.group_number).where(Team.team_id.in_(team_ids))
            result = await self.db.execute(query)
            existing_teams = [Team(team_id=row[0], team_name=row[1], registration_day_of_year=row[2], group_number=row[3]) for row in result.fetchall()]

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
            query = select(Team.team_id,Team.team_name, Team.registration_day_of_year, Team.group_number)
            if group_filter_filter != None:
                query = query.where(Team.group_number == group_filter_filter)
            result = await self.db.execute(query)
            return [Team(team_id=row[0], team_name=row[1], registration_day_of_year=row[2], group_number=row[3]) for row in result.fetchall()]
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def get_team_matchups_for_id(self, team_id: int) -> List[TeamMatchUpDetail]:
        """
        Gets the matchups for a team.

        Args:
        team_id: int: The team id to get matchups for.
        
        Returns:
        matchups: List[TeamMatchUpDetail]: A list of matchups for the team.
        """
        try:
            # get match_ids for team_id
            query = select(MatchResults.match_id).where(MatchResults.team_id == team_id)
            match_ids = [row[0] for row in (await self.db.execute(query)).fetchall()]
            # matchups for team_id
            query = select(Team.team_id, Team.team_name, GameMatch.round_number, GameMatch.match_id, MatchResults.goals_scored).where(MatchResults.match_id.in_(match_ids)).join(GameMatch, GameMatch.match_id == MatchResults.match_id).join(Team, Team.team_id == MatchResults.team_id)
            result = await self.db.execute(query)
            matched_dict: Dict[int, TeamMatchUpDetail] = {} # Dict[match_id, TeamMatchUpDetail]
            for row in result.fetchall():
                match_id = row[3]
                matched_dict.setdefault(match_id, TeamMatchUpDetail(opponent_team_id=0, opponent="", round_number=0, match_id=0, goals_scored=0, goals_conceded=0))
                if row[0] == team_id:
                    matched_dict[match_id].goals_scored = row[4]
                else:
                    matched_dict[match_id].opponent_team_id = row[0]
                    matched_dict[match_id].opponent = row[1]
                    matched_dict[match_id].round_number = row[2]
                    matched_dict[match_id].match_id = row[3]
                    matched_dict[match_id].goals_conceded = row[4]
            return list(matched_dict.values())
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
