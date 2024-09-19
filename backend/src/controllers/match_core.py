from src.repositories.match_core import MatchRepository
from src.repositories.team import TeamRepository
from src.schemas.match_results import CreateMatchResults, MatchResultDetailed, MatchResultSparse
from src.models.match_results import MatchResults
from src.models.team import Team
from typing import List, Set, Dict
from fastapi import HTTPException
from src.models.game_match import GameMatch
from src.schemas.rank import TeamRank, GroupRanking, GetRankingResponse
from src.utils.date_util import day_of_year_to_ddmm
import json
from src.redis.lock import DistributedLock
from src.controllers.connection_controller import ConnectionController
class MatchController:
    def __init__(self, match_repository: MatchRepository, team_repository: TeamRepository, match_result_lock: DistributedLock):
        # inject repositories
        self.match_repository = match_repository
        self.team_repository = team_repository

        # lock with unique lock value for instance
        self.match_result_lock = match_result_lock

    async def create_results(self, request_match_results: List[CreateMatchResults], round_number: int) -> bool:
        """
        Creates Match and MatchResults records in the database according to round number and match results provided.

        Args:
        request_match_results: List[CreateMatchResults]: List of match results to be created
        round_number: int: Round number for which the match results are to be created

        Returns:
        is_successful: bool: True if match results are created successfully, False otherwise
        """
        match_up_dict: Dict[int, Set] = {} # team_name -> {opponent_team_name}
        duplicate_match_ups = []
        team_name_set: Set[str] = set()
        self_match_game_ids: List[int] = []
        for match_result in request_match_results:
            if (match_result.result[0].team_name == match_result.result[1].team_name):
                self_match_game_ids.append((match_result.result[0].team_name, match_result.result[1].team_name))
            team_name_set.add(match_result.result[0].team_name)
            team_name_set.add(match_result.result[1].team_name)
            # check match up duplicates within request
            if match_result.result[0].team_name in match_up_dict.setdefault(match_result.result[1].team_name, set()):
                duplicate_match_ups.append((match_result.result[0].team_name, match_result.result[1].team_name))
            if match_result.result[1].team_name in match_up_dict.setdefault(match_result.result[0].team_name, set()):
                duplicate_match_ups.append((match_result.result[1].team_name, match_result.result[0].team_name))
            match_up_dict[match_result.result[0].team_name].add(match_result.result[1].team_name)
            match_up_dict[match_result.result[1].team_name].add(match_result.result[0].team_name)
        if len(duplicate_match_ups) > 0:
            raise HTTPException(status_code=400, detail="Duplicate match ups found: "+str(duplicate_match_ups))
        
        # check if self match games are present
        if len(self_match_game_ids) > 0:
            raise HTTPException(status_code=400, detail="Self match games are not allowed: "+str(self_match_game_ids))
        
        # check if teams exist in database
        existing_teams:List[Team] = await self.team_repository.get_teams_by_team_names(list(team_name_set))
        if len(existing_teams) != len(team_name_set):
            raise HTTPException(status_code=400, detail="Teams do not exist: "+str(team_name_set - set([team.team_name for team in existing_teams])))
        team_name_to_id_map = {}
        team_name_to_group_map = {}
        for team in existing_teams:
            team_name_to_id_map[team.team_name] = team.team_id
            team_name_to_group_map[team.team_name] = team.group_number

        # if the round is 1 or 2 and not 3(assumption: final round), don't allow cross group matches
        if round_number < 3:
            for match_result in request_match_results:
                if team_name_to_group_map[match_result.result[0].team_name] != team_name_to_group_map[match_result.result[1].team_name]:
                    raise HTTPException(status_code=400, detail="Cross group matches are not allowed in round 1 and 2")
        print("before lock")
        # get lock here
        # existing matches will be consistent
        # we also check if matches have already been played between two teams for a round
        # this lock prevents double write        
        if not await self.match_result_lock.get():
            raise HTTPException(status_code=500, detail="Failed to get match result lock")
        try:
            # check if matches between teams already exist for a round
            match_ups: List[MatchResultSparse] = await self.match_repository.get_matchups_by_round_and_team_ids(round_number, list(team_name_to_id_map.values()))
            match_id_opponent_map: Dict[int, int] = {} # match_id -> opponent_team_id, will set on first match_id natched
            for match_up in match_ups:
                if match_id_opponent_map.get(match_up.match_id, None) is None:
                    match_id_opponent_map[match_up.match_id] = match_up.team_name
                else:
                    if match_up.team_name in match_up_dict[match_id_opponent_map[match_up.match_id]]:
                        duplicate_match_ups.append((match_id_opponent_map[match_up.match_id], match_up.team_name))
            if len(duplicate_match_ups) > 0:
                await self.match_result_lock.give()
                raise HTTPException(status_code=400, detail="Duplicate match ups found: "+str(duplicate_match_ups))

            
            # create matches and match results
            game_match_ids = await self.match_repository.create_game_matches(match_count=len(request_match_results), round_number=round_number)
            if len(game_match_ids) > 0:
                if len(game_match_ids) != len(request_match_results):
                    await self.match_repository.rollback_transaction()
                    await self.match_result_lock.give()
                    raise HTTPException(status_code=500, detail="Failed to create game matches")
                
                match_results = []
                cur_game_match_id = 0
                for match_result in request_match_results:
                    match_results.extend([MatchResults(match_id=game_match_ids[cur_game_match_id], team_id=team_name_to_id_map[match_result.result[0].team_name], goals_scored=match_result.result[0].goals_scored), MatchResults(match_id=game_match_ids[cur_game_match_id], team_id=team_name_to_id_map[match_result.result[1].team_name], goals_scored=match_result.result[1].goals_scored)])
                    cur_game_match_id += 1
                try:
                    is_match_results_created = await self.match_repository.create_match_results(match_results)
                    if is_match_results_created:
                        await self.match_repository.commit_transaction()
                        await self.match_repository.commit_transaction()
                        await self.match_result_lock.give()
                        connectionController = ConnectionController.get_instance()
                        await connectionController.broadcast(
                            ("match_rankings",round_number,1),
                            json.dumps((await self.get_match_rankings(qualifying_count=4, round_number=round_number, group_number_filter=1)).dict()),
                        )
                        await connectionController.broadcast(
                            ("match_rankings",round_number,2),
                            json.dumps((await self.get_match_rankings(qualifying_count=4, round_number=round_number, group_number_filter=2)).dict()),
                        )
                        return True
                    else:
                        await self.match_result_lock.give()
                        await self.match_repository.rollback_transaction()
                except HTTPException as e:
                    await self.match_repository.rollback_transaction()
                    raise HTTPException(status_code=e.status_code, detail=e.detail)
                except Exception as e:
                    await self.match_repository.rollback_transaction()
                    raise HTTPException(status_code=500, detail=str(e))
            self.match_result_lock.give()
            return False
        finally:
            await self.match_result_lock.give()
    
    async def get_match_rankings(self, qualifying_count: int, round_number: int, group_number_filter: int = None) -> GetRankingResponse:
        """
        Gets match results for a given round and group number
        """
        match_results: List[MatchResultDetailed] = await self.match_repository.get_match_results_by_round(round_number, group_number_filter)
        # convert match_result.goals scored to points for teams in the match
        match_maker:Dict[int,MatchResultDetailed] = {}
        # team_id -> TeamRank
        team_rank_mapper: Dict[int, TeamRank] = {}
        # team_id -> group_number
        group_mapper: Dict[int, int] = {}
        """
        scoring rules:
        1. Highest total match points (3 points for win, 1 point for draw, 0 points for loss)
        2. Highest total goals scored
        3. Highest alternate total match points (5 points for win, 3 points for draw, 0 points for loss)
        4. Earliest registration date
        """
        # create a match maker to get the match results
        for result in match_results:
            if match_maker.get(result.match_id, None) is None:
                match_maker[result.match_id] = result
            else:
                team_a_detail = match_maker[result.match_id]
                team_b_detail = result
                group_mapper.setdefault(team_a_detail.team_id, team_a_detail.group_number)
                group_mapper.setdefault(team_b_detail.team_id, team_b_detail.group_number)
                team_rank_mapper.setdefault(team_a_detail.team_id, TeamRank(team_id=team_a_detail.team_id, position=1, is_tied=False, team_name=team_a_detail.team_name, goals=0,wins=0, draws=0, losses=0,registration_day_of_year=team_a_detail.registration_day_of_year, registration_date_ddmm=day_of_year_to_ddmm(team_a_detail.registration_day_of_year)))
                team_rank_mapper.setdefault(team_b_detail.team_id, TeamRank(team_id=team_b_detail.team_id, position=1, is_tied=False, team_name=team_b_detail.team_name, goals=0,wins=0, draws=0, losses=0,registration_day_of_year=team_b_detail.registration_day_of_year, registration_date_ddmm=day_of_year_to_ddmm(team_b_detail.registration_day_of_year)))
                team_rank_mapper[team_a_detail.team_id].goals += team_a_detail.goals_scored
                team_rank_mapper[team_b_detail.team_id].goals += team_b_detail.goals_scored
                if team_a_detail.goals_scored > team_b_detail.goals_scored:
                    team_rank_mapper[team_a_detail.team_id].wins += 1
                    team_rank_mapper[team_b_detail.team_id].losses += 1
                elif team_a_detail.goals_scored < team_b_detail.goals_scored:
                    team_rank_mapper[team_a_detail.team_id].losses += 1
                    team_rank_mapper[team_b_detail.team_id].wins += 1
                else:
                    team_rank_mapper[team_a_detail.team_id].draws += 1
                    team_rank_mapper[team_b_detail.team_id].draws += 1
        # split into groups then sort
        group_dict: Dict[int, TeamRank] = {}
        for team in team_rank_mapper.values():
            group_dict.setdefault(group_mapper[team.team_id], []).append(team)

        # get all teams in the group, including those that did not play yet
        all_teams = await self.team_repository.get_teams_by_group(group_number_filter)
        for team in all_teams:
            if team_rank_mapper.get(team.team_id, None) is None:
                group_dict.setdefault(team.group_number, []).append(TeamRank(team_id=team.team_id, position=1, is_tied=False, team_name=team.team_name, goals=0, wins=0, draws=0, losses=0, registration_day_of_year=team.registration_day_of_year, registration_date_ddmm=day_of_year_to_ddmm(team.registration_day_of_year)))
        for group_number in group_dict.keys():
            if len(group_dict[group_number]) == 0:
                continue
            group_dict[group_number] = sorted(group_dict[group_number], key=lambda x: (self._get_score(x), x.goals, self._get_alternate_score(x), -x.registration_day_of_year), reverse=True)
            cur_pos = len(group_dict[group_number])
            tie_count = 0
            group_dict[group_number][len(group_dict[group_number])-1].position = cur_pos
            if cur_pos <= qualifying_count:
                group_dict[group_number][len(group_dict[group_number])-1].is_qualified = True
            for i in range(len(group_dict[group_number])-2, -1, -1):
                if self._get_score(group_dict[group_number][i]) == self._get_score(group_dict[group_number][i+1]) and group_dict[group_number][i].goals == group_dict[group_number][i+1].goals and self._get_alternate_score(group_dict[group_number][i]) == self._get_alternate_score(group_dict[group_number][i+1]) and group_dict[group_number][i].registration_day_of_year == group_dict[group_number][i+1].registration_day_of_year:
                    group_dict[group_number][i+1].is_tied = True
                    group_dict[group_number][i].is_tied = True
                    tie_count += 1
                else:
                    group_dict[group_number][i].is_tied = False
                    cur_pos -= (1 + tie_count)
                    tie_count = 0
                group_dict[group_number][i].position = cur_pos
                if cur_pos <= qualifying_count:
                    group_dict[group_number][i].is_qualified = True
                
        
        # return structured response
        return GetRankingResponse(
            round_number=round_number,
            group_rankings=[GroupRanking(
                group_number=group_number,
                team_rankings=[team for team in group_dict[group_number]]
            ) for group_number in group_dict.keys()]
        )
    
    def _get_score(self, team: TeamRank) -> int:
        return team.wins * 3 + team.draws
    
    def _get_alternate_score(self, team: TeamRank) -> int:
        return team.wins * 5 + team.draws * 3 + team.losses