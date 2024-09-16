from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from src.database.database import Database
from src.controllers.match_results import MatchResultsController
from src.repositories.match_results import MatchResultsRepository
from src.repositories.game_match import GameMatchRepository
from src.repositories.team import TeamRepository
from src.schemas.match_results import BatchCreateMatchResultsRequest

match_results_router = APIRouter()
database = Database.get_instance()

@match_results_router.post("/match_results", tags=["match_result"])
async def create_match_results(request: BatchCreateMatchResultsRequest, db: AsyncSession = Depends(database.get_session)):
    """
    API endpoint to create teams in batch.
    """
    match_results_controller = MatchResultsController(
        match_results_repository=MatchResultsRepository(db),
        game_match_repository=GameMatchRepository(db),
        team_repository=TeamRepository(db)
    )
    is_ok = await match_results_controller.create_results(
        request_match_results=request.results,
        round_number=request.round_number
    )
    if is_ok:
        return JSONResponse(content={"detail":"matches and results created successfully"}, status_code=200)
    else:
        return JSONResponse(content={"detail":"matches and results creation failed"}, status_code=500)

