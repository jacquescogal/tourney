from src.repositories.match_results import MatchResultsRepository
from src.repositories.game_match import GameMatchRepository
from src.repositories.team import TeamRepository
from src.schemas.match_results import CreateMatchResultsRequest
from src.models.match_results import MatchResults
from src.models.team import Team
from typing import List, Set
from fastapi import HTTPException
from src.models.game_match import GameMatch
class MatchResultsController:
    def __init__(self, match_results_repository: MatchResultsRepository, game_match_repository: GameMatchRepository, team_repository: TeamRepository):
        # inject team_repository
        self.match_results_repository = match_results_repository
        self.game_match_repository = game_match_repository
        self.team_repository = team_repository

    async def create_results(self, request_match_results: List[CreateMatchResultsRequest], round_number: int) -> bool:
        """
        Creates Match and MatchResults records in the database
        """

        match_ids: List[int] =[]
        team_name_set: Set[str] = set()
        self_match_game_ids: List[int] = []
        for match_result in request_match_results:
            match_ids.append(match_result.match_id)
            if (match_result.result[0].team_name == match_result.result[1].team_name):
                self_match_game_ids.append(match_result.match_id)
            team_name_set.add(match_result.result[0].team_name)
            team_name_set.add(match_result.result[1].team_name)
        
        # check if self match games are present
        if len(self_match_game_ids) > 0:
            raise HTTPException(status_code=400, detail="Self match games are not allowed: "+str(self_match_game_ids))

        # check match duplicates
        if len(set(match_ids)) != len(match_ids):
            raise HTTPException(status_code=400, detail="Duplicate match ids found in the request")
        
        # check if teams exist
        existing_teams:List[Team] = await self.team_repository.get_teams_by_team_names(list(team_name_set))
        if len(existing_teams) != len(team_name_set):
            raise HTTPException(status_code=400, detail="Teams do not exist: "+str(team_name_set - set([team.team_name for team in existing_teams])))
        team_name_to_id_map = {}
        for team in existing_teams:
            team_name_to_id_map[team.team_name] = team.team_id

        # check if matches already exist
        existing_matches = await self.game_match_repository.get_game_matches_by_ids(match_ids)
        if len(existing_matches) > 0:
            raise HTTPException(status_code=400, detail="Matches already exist: "+str(existing_matches))
        
        # create matches and match results
        game_matches: List[GameMatch] = [GameMatch(match_id=match_id, round_number=round_number) for match_id in match_ids]
        is_game_matches_created = await self.game_match_repository.create_game_matches(game_matches)
        if is_game_matches_created:
            match_results: List[MatchResults] = [MatchResults(match_id=match_result.match_id, team_id=team_name_to_id_map[match_result.result[0].team_name], goals_scored=match_result.result[0].goals_scored) for match_result in request_match_results]
            match_results.extend([MatchResults(match_id=match_result.match_id, team_id=team_name_to_id_map[match_result.result[1].team_name], goals_scored=match_result.result[1].goals_scored) for match_result in request_match_results])
            try:
                is_match_results_created = await self.match_results_repository.create_match_results(match_results)
                if is_match_results_created:
                    await self.game_match_repository.commit_transaction()
                    await self.match_results_repository.commit_transaction()
                    return True
                else:
                    await self.game_match_repository.rollback_transaction()
            except HTTPException as e:
                await self.game_match_repository.rollback_transaction()
                raise HTTPException(status_code=e.status_code, detail=e.detail)
            except Exception as e:
                await self.game_match_repository.rollback_transaction()
                raise HTTPException(status_code=500, detail=str(e))
        return False

