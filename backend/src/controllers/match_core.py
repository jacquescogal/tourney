from src.repositories.match_core import MatchRepository
from src.repositories.team import TeamRepository
from src.schemas.match_results import CreateMatchResultsRequest, MatchResultDetailed
from src.models.match_results import MatchResults
from src.models.team import Team
from typing import List, Set, Dict
from fastapi import HTTPException
from src.models.game_match import GameMatch
from src.schemas.rank import TeamRank, GroupRanking, GetRankingResponse
from src.utils.date_util import unix_to_ddmm
import json
from src.redis.lock import DistributedLock
class MatchController:
    def __init__(self, match_repository: MatchRepository, team_repository: TeamRepository, match_result_lock: DistributedLock):
        # inject team_repository
        self.match_repository = match_repository
        self.team_repository = team_repository
        self.match_result_lock = match_result_lock

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
        team_name_to_group_map = {}
        for team in existing_teams:
            team_name_to_id_map[team.team_name] = team.team_id
            team_name_to_group_map[team.team_name] = team.group_number

        # if the round is 1 or 2 and not 3(final round), don't allow cross group matches
        if round_number < 3:
            for match_result in request_match_results:
                if team_name_to_group_map[match_result.result[0].team_name] != team_name_to_group_map[match_result.result[1].team_name]:
                    raise HTTPException(status_code=400, detail="Cross group matches are not allowed in round 1 and 2")

        # get lock here
        # existing matches will be consistent
        # we also check if matches have already been played between two teams for a round
        # this lock prevents double write        
        if not await self.match_result_lock.get():
            raise HTTPException(status_code=500, detail="Failed to get match result lock")
        
        # check if matches already exists
        existing_matches = await self.match_repository.get_game_matches_by_ids(match_ids)
        if len(existing_matches) > 0:
            raise HTTPException(status_code=400, detail="Matches already exist: "+str(existing_matches))
        
        # check if matches between teams already exist for a round
        
        # create matches and match results
        game_matches: List[GameMatch] = [GameMatch(match_id=match_id, round_number=round_number) for match_id in match_ids]
        is_game_matches_created = await self.match_repository.create_game_matches(game_matches)
        if is_game_matches_created:
            match_results: List[MatchResults] = [MatchResults(match_id=match_result.match_id, team_id=team_name_to_id_map[match_result.result[0].team_name], goals_scored=match_result.result[0].goals_scored) for match_result in request_match_results]
            match_results.extend([MatchResults(match_id=match_result.match_id, team_id=team_name_to_id_map[match_result.result[1].team_name], goals_scored=match_result.result[1].goals_scored) for match_result in request_match_results])
            try:
                is_match_results_created = await self.match_repository.create_match_results(match_results)
                if is_match_results_created:
                    await self.match_repository.commit_transaction()
                    await self.match_repository.commit_transaction()
                    return True
                else:
                    await self.match_repository.rollback_transaction()
            except HTTPException as e:
                await self.match_repository.rollback_transaction()
                raise HTTPException(status_code=e.status_code, detail=e.detail)
            except Exception as e:
                await self.match_repository.rollback_transaction()
                raise HTTPException(status_code=500, detail=str(e))
        return False
    
    async def get_match_rankings(self, round_number: int, group_number_filter: int = None) -> GetRankingResponse:
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
                team_rank_mapper.setdefault(team_a_detail.team_id, TeamRank(team_id=team_a_detail.team_id, position=1, is_tied=False, team_name=team_a_detail.team_name, goals=team_a_detail.goals_scored,wins=0, draws=0, losses=0,join_date_unix=team_a_detail.join_date_unix, join_date_ddmm=unix_to_ddmm(team_a_detail.join_date_unix)))
                team_rank_mapper.setdefault(team_b_detail.team_id, TeamRank(team_id=team_b_detail.team_id, position=1, is_tied=False, team_name=team_b_detail.team_name, goals=team_b_detail.goals_scored,wins=0, draws=0, losses=0,join_date_unix=team_b_detail.join_date_unix, join_date_ddmm=unix_to_ddmm(team_b_detail.join_date_unix)))
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
                group_dict.setdefault(team.group_number, []).append(TeamRank(team_id=team.team_id, position=1, is_tied=False, team_name=team.team_name, goals=0, wins=0, draws=0, losses=0, join_date_unix=team.registration_date_unix, join_date_ddmm=unix_to_ddmm(team.registration_date_unix)))
        for group_number in group_dict.keys():
            group_dict[group_number] = sorted(group_dict[group_number], key=lambda x: (self._get_score(x), x.goals, self._get_alternate_score(x), -x.join_date_unix), reverse=True)
            cur_pos = 1
            for i in range(1, len(group_dict[group_number])):
                if self._get_score(group_dict[group_number][i]) == self._get_score(group_dict[group_number][i-1]) and group_dict[group_number][i].goals == group_dict[group_number][i-1].goals and self._get_alternate_score(group_dict[group_number][i]) == self._get_alternate_score(group_dict[group_number][i-1]) and group_dict[group_number][i].join_date_unix == group_dict[group_number][i-1].join_date_unix:
                    group_dict[group_number][i-1].is_tied = True
                    group_dict[group_number][i].is_tied = True
                else:
                    group_dict[group_number][i].is_tied = False
                    cur_pos += 1
                group_dict[group_number][i].position = cur_pos
        
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