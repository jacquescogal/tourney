from src.repositories.team import TeamRepository
from src.schemas.team import RegisterTeamRequest, TeamDetails, TeamMatchUpDetail
from src.models.team import Team
from typing import List
from fastapi import HTTPException
from src.utils.date_util import ddmm_to_day_of_year, day_of_year_to_ddmm
from src.redis.lock import DistributedLock
from src.schemas.team import TeamBase
from src.controllers.connection_controller import ConnectionController
import json
from fastapi.responses import JSONResponse
class TeamController:
    def __init__(self, team_repository: TeamRepository, team_lock: DistributedLock = None):
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
        # the lock will ensure that the limit of 6 teams for each group is not exceeded
        
        try:
            # check if group limit is exceeded before continuing (6 teams per group)
            group_team_dict = {} # group_number: count of teams
            for team in request_teams:
                group_team_dict[team.group_number] = group_team_dict.get(team.group_number, 0) + 1
            all_teams: List[Team] = await self.team_repository.get_teams_by_group()
            for team in all_teams:
                group_team_dict[team.group_number] = group_team_dict.get(team.group_number, 0) + 1
            group_exceeded = []
            for group, count in group_team_dict.items():
                if count > 6:
                    group_exceeded.append(group)
            if len(group_exceeded) > 0:
                await self.team_lock.give()
                raise HTTPException(status_code=400, detail="Group limit exceeded for groups: "+str(group_exceeded))

            # create teams 
            teams: List[Team] = [Team(
                team_name=team.team_name,
                registration_day_of_year=ddmm_to_day_of_year(team.registration_date_ddmm),
                group_number=team.group_number
            ) for team in request_teams]
            if await self.team_repository.create_teams(teams) == True:
                is_committed = await self.team_repository.commit_transaction()
                await self.team_lock.give()
                connectionController = ConnectionController.get_instance()
                teams:List[TeamBase] = await self.get_teams()
                response = json.dumps(sorted([team.dict() for team in teams], key=lambda x: x["group_number"]))
                await connectionController.broadcast(
                    ("teams"),
                    response
                )
                return is_committed
            else:
                await self.team_lock.give()
                return False
        finally:
            await self.team_lock.give()

    async def get_teams(self) -> List[TeamBase]:
        """
        get_teams gets all teams from the repository.
        """
        teams = await self.team_repository.get_teams()
        return [TeamBase(
            team_id=team.team_id,
            team_name=team.team_name,
            registration_day_of_year=team.registration_day_of_year,
            registration_date_ddmm=day_of_year_to_ddmm(team.registration_day_of_year),
            group_number=team.group_number
        ) for team in teams]
    
    async def get_team_details_for_id(self, team_id: int) -> TeamDetails:
        match_ups = await self.team_repository.get_team_matchups_for_id(team_id)
        team:Team = (await self.team_repository.get_teams_by_ids([team_id]))[0]
        return TeamDetails(
            team_id=team.team_id,
            team_name=team.team_name,
            registration_date_ddmm=day_of_year_to_ddmm(team.registration_day_of_year),
            registration_day_of_year=team.registration_day_of_year,
            group_number=team.group_number,
            match_ups=match_ups
        )