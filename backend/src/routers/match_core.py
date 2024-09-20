from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from src.database.database import Database
from src.controllers.match_core import MatchController
from src.repositories.match_core import MatchRepository
from src.repositories.team import TeamRepository
from src.schemas.match_results import BatchCreateMatchResultsRequest, MatchResultsConcatStrict, GetMatchResultsResponse
from fastapi import HTTPException
from src.redis.lock import DistributedLock, MATCH_LOCK_KEY
from config import Settings
from fastapi import Request
from src.schemas.user import UserRole
from fastapi import WebSocket, WebSocketDisconnect
from src.controllers.connection_controller import ConnectionController
from typing import List
import json
match_router = APIRouter()
database = Database.get_instance()

@match_router.post("/match_results", tags=["match"])
async def create_match_results(request: Request, batchRequest: BatchCreateMatchResultsRequest, db: AsyncSession = Depends(database.get_session)):
    """
    API endpoint to create teams in batch.
    """
    if request.state.user_session is None or request.state.user_session.user_role != UserRole.admin:
        return HTTPException(status_code=401, detail="Unauthorized")
    match_results_controller = MatchController(
        match_repository=MatchRepository(db),
        team_repository=TeamRepository(db),
        match_result_lock=DistributedLock(MATCH_LOCK_KEY)
    )
    is_ok = await match_results_controller.create_results(
        request_match_results=batchRequest.results,
        round_number=batchRequest.round_number
    )
    if is_ok:
        return JSONResponse(content={"detail":"matches and results created successfully"}, status_code=200)
    else:
        return JSONResponse(content={"detail":"matches and results creation failed"}, status_code=500)

@match_router.get("/match_rankings", tags=["match"])
async def get_match_rankings(request: Request, round_number: int = None, group_number:int = None, db: AsyncSession = Depends(database.get_session)):
    """
    API endpoint to get all match results.
    """
    if round_number is None:
        return HTTPException(status_code=400, detail="Round number is required")
    elif round_number < 1 or round_number > 3:
        return HTTPException(status_code=400, detail="Round number should be between 1 and 3 inclusive")
    match_results_controller = MatchController(
        match_repository=MatchRepository(db),
        team_repository=TeamRepository(db),
        match_result_lock=DistributedLock(MATCH_LOCK_KEY)
    )
    match_results = await match_results_controller.get_match_rankings(qualifying_count = Settings.get_instance().round_qualify_count.get(round,4) ,round_number=round_number, group_number_filter=group_number)
    return JSONResponse(content=match_results.dict(), status_code=200)

@match_router.get("/match_results", tags=["match"])
async def get_match_results(request: Request, round_number: int, db: AsyncSession = Depends(database.get_session)):
    """
    API endpoint to get match results by round number and group number.
    """
    match_results_controller = MatchController(
        match_repository=MatchRepository(db)
    )
    match_results: List[MatchResultsConcatStrict] = await match_results_controller.get_concat_match_results(round_number=round_number)
    return JSONResponse(content=GetMatchResultsResponse(match_results=match_results).dict(), status_code=200)

@match_router.websocket("/ws/match_rankings/{round}/{group}")
async def websocket_endpoint(websocket: WebSocket, round: int, group: int):
    connectionController = ConnectionController.get_instance()
    await connectionController.connect(("match_rankings",round,group),websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connectionController.disconnect(("match_rankings",round,group),websocket)

@match_router.websocket("/ws/match_results/{round}")
async def websocket_endpoint(websocket: WebSocket, round: int):
    connectionController = ConnectionController.get_instance()
    await connectionController.connect(("match_results",round),websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connectionController.disconnect(("match_results",round),websocket)