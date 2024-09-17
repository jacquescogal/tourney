from src.repositories.team import TeamRepository
from src.schemas.team import RegisterTeamRequest
from src.models.team import Team
from typing import List
from fastapi import HTTPException
from src.utils.date_util import ddmm_to_day_of_year
from src.redis.lock import DistributedLock

class TeamController:
    def __init__(self, team_repository: TeamRepository, team_lock: DistributedLock):
        # inject team_repository
        self.team_repository = team_repository
        self.team_lock = team_lock
    
    async def create_teams(self, request_teams: List[RegisterTeamRequest]) -> bool:
        """
        create_teams creates teams in batch. It processes the request_teams into ORM teams model and calls the repository to create teams in batch.
        """
        

        team_names: List[str] =[team.team_name for team in request_teams]

        # check if there are duplicate teams in the request_teams list
        if len(set(team_names)) != len(team_names):
            raise HTTPException(status_code=400, detail="Duplicate team names found in the request")

        # check if teams already exist and return error if they do
        existing_teams:List[Team] = await self.team_repository.get_teams_by_team_names(team_names)
        if len(existing_teams) > 0:
            raise HTTPException(status_code=400, detail="Teams already exist: "+str([team.team_name for team in existing_teams]))
        
        # acquire lock
        if not await self.team_lock.get():
            raise HTTPException(status_code=500, detail="Failed to get team lock")
        # the lock will ensure that the limit of 12 teams is not exceeded
        
        try:
            # get all teams
            all_teams: List[Team] = await self.team_repository.get_teams_by_group()
            if len(all_teams) + len(request_teams) > 12:
                await self.team_lock.give()
                raise HTTPException(status_code=400, detail="Transaction will exceed Team limit of 12")

            # create teams 
            teams: List[Team] = [Team(
                team_name=team.team_name,
                registration_day_of_year=ddmm_to_day_of_year(team.registration_date),
                group_number=team.group_number
            ) for team in request_teams]
            if await self.team_repository.create_teams(teams) == True:
                is_committed = await self.team_repository.commit_transaction()
                await self.team_lock.give()
                return is_committed
            else:
                await self.team_lock.give()
                return False
        finally:
            await self.team_lock.give()