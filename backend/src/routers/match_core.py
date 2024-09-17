from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from src.database.database import Database
from src.controllers.match_core import MatchController
from src.repositories.match_core import MatchRepository
from src.repositories.team import TeamRepository
from src.schemas.match_results import BatchCreateMatchResultsRequest
from fastapi import HTTPException
from src.redis.lock import DistributedLock, MATCH_LOCK_KEY

match_router = APIRouter()
database = Database.get_instance()

@match_router.post("/match_results", tags=["match"])
async def create_match_results(request: BatchCreateMatchResultsRequest, db: AsyncSession = Depends(database.get_session)):
    """
    API endpoint to create teams in batch.
    """
    match_results_controller = MatchController(
        match_repository=MatchRepository(db),
        team_repository=TeamRepository(db),
        match_result_lock=DistributedLock(MATCH_LOCK_KEY)
    )
    is_ok = await match_results_controller.create_results(
        request_match_results=request.results,
        round_number=request.round_number
    )
    if is_ok:
        return JSONResponse(content={"detail":"matches and results created successfully"}, status_code=200)
    else:
        return JSONResponse(content={"detail":"matches and results creation failed"}, status_code=500)

@match_router.get("/match_rankings", tags=["match"])
async def get_match_rankings(round: int = None, group:int = None, db: AsyncSession = Depends(database.get_session)):
    """
    API endpoint to get all match results.
    """
    if round is None:
        return HTTPException(status_code=400, detail="Round number is required")
    elif round < 1 or round > 3:
        return HTTPException(status_code=400, detail="Round number should be between 1 and 3 inclusive")
    match_results_controller = MatchController(
        match_repository=MatchRepository(db),
        team_repository=TeamRepository(db),
        match_result_lock=DistributedLock(MATCH_LOCK_KEY)
    )
    match_results = await match_results_controller.get_match_rankings(round_number=round, group_number_filter=group)
    return JSONResponse(content={"results":match_results.dict()}, status_code=200)