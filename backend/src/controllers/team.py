from src.repositories.team import TeamRepository
from src.schemas.team import RegisterTeamRequest
from src.models.team import Team
from typing import List
class TeamController:
    def __init__(self, team_repository: TeamRepository):
        # inject team_repository
        self.team_repository = team_repository
    
    async def create_teams(self, request_teams: List[RegisterTeamRequest]) -> bool:
        """
        create_teams creates teams in batch. It processes the request_teams into ORM teams model and calls the repository to create teams in batch.
        """
        teams: List[Team] = [Team(
            team_name=team.team_name,
            registration_date_unix=0,
            group_number=team.group_number
        ) for team in request_teams]
        return await self.team_repository.create_teams(teams)