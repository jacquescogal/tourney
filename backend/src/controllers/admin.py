from src.repositories.match_core import MatchRepository
from src.repositories.team import TeamRepository
from src.repositories.user import UserRepository
from src.schemas.match_results import CreateMatchResults, MatchResultDetailed, MatchResultSparse
from src.models.match_results import MatchResults
from src.models.team import Team
from typing import List, Set, Dict
from fastapi import HTTPException
from src.models.game_match import GameMatch
from src.schemas.rank import TeamRank, GroupRanking, GetRankingResponse
from src.utils.date_util import day_of_year_to_ddmm
from src.redis.session import SessionStorage
from src.redis.lock import DistributedLock
class DBAdminController:
    """
    DB Admin Controller class to handle admin operations on the database.
    """
    def __init__(self, match_repository: MatchRepository, team_repository: TeamRepository, user_repository: UserRepository, session_storage: SessionStorage, match_result_lock: DistributedLock, team_lock: DistributedLock):
        # dependency injection
        self.match_repository = match_repository
        self.team_repository = team_repository
        self.user_repository = user_repository

        # session storage to sign out all users except admin
        self.session_storage = session_storage

        # locks to prevent inconsistency with async writes
        self.match_result_lock = match_result_lock
        self.team_lock = team_lock
    
    async def delete_all_data(self) -> bool:
        """
        delete_all_data deletes all data from the database.
        """
        # acquire lock
        if not await self.match_result_lock.get() or not await self.team_lock.get():
            raise HTTPException(status_code=500, detail="Failed to get lock")
        
        # delete all data
        try:
            await self.match_repository.delete_all_match_results()
            await self.team_repository.delete_all_teams()
            await self.user_repository.delete_all_users_except_admin()
            await self.match_repository.commit_transaction()
            await self.team_repository.commit_transaction()
            await self.user_repository.commit_transaction()
        except Exception as e:
            await self.match_repository.rollback_transaction()
            await self.team_repository.rollback_transaction()
            await self.user_repository.rollback_transaction()
            await self.match_result_lock.give()
            await self.team_lock.give()
            return False
        # release lock
        await self.match_result_lock.give()
        await self.team_lock.give()
        return True