from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from src.database.database import Database
from src.controllers.match_core import MatchController
from src.repositories.match_core import MatchRepository
from src.repositories.team import TeamRepository
from src.schemas.match_results import BatchCreateMatchResultsRequest, MatchResultsConcatStrict, GetMatchResultsResponse, UpdateMatchResultRequest, DeleteMatchResultRequest
from fastapi import HTTPException
from src.redis.lock import DistributedLock, MATCH_LOCK_KEY
from config import Settings
from fastapi import Request
from src.schemas.user import UserRole
from fastapi import WebSocket, WebSocketDisconnect
from src.controllers.connection_controller import ConnectionController
from typing import List
import logging
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
    try:
        is_ok = await match_results_controller.create_results(
            request_match_results=batchRequest.results,
            round_number=batchRequest.round_number
        )
        if is_ok:
            logging.info(f"{request.state.user_session.user_role} action: Match results created successfully")
            return JSONResponse(content={"detail":"matches and results created successfully"}, status_code=200)
        else:
            logging.error(f"{request.state.user_session.user_role} action: Match results creation failed")
            return JSONResponse(content={"detail":"matches and results creation failed"}, status_code=500)
    except Exception as e:
        logging.error(f"{request.state.user_session.user_role} action: Error creating match results: {e}")
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
    match_results = await match_results_controller.get_match_rankings(qualifying_count = 4 ,round_number=round_number, group_number_filter=group_number)
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

@match_router.put("/match_results", tags=["match"])
async def update_match_result(request: Request, updateRequest: UpdateMatchResultRequest, db: AsyncSession = Depends(database.get_session)):
    if request.state.user_session is None or request.state.user_session.user_role != UserRole.admin:
        return HTTPException(status_code=401, detail="Unauthorized")
    match_results_controller = MatchController(
        match_repository=MatchRepository(db),
        team_repository=TeamRepository(db),
        match_result_lock=DistributedLock(MATCH_LOCK_KEY)
    )
    try:
        is_ok = await match_results_controller.update_match_results_for_match_id(
            round_number=updateRequest.round_number,
            match_id=updateRequest.match_id,
            team_id=updateRequest.team_id,
            team_goals=updateRequest.team_goals
        )
        if is_ok:
            logging.info(f"{request.state.user_session.user_role} action: Match result updated successfully")
            return JSONResponse(content={"detail":"match result updated successfully"}, status_code=200)
        else:
            logging.error(f"{request.state.user_session.user_role} action: Match result update failed")
            return JSONResponse(content={"detail":"match result update failed"}, status_code=500)
    except Exception as e:
        logging.error(f"{request.state.user_session.user_role} action: Error updating match result: {e}")
        return JSONResponse(content={"detail":"match result update failed"}, status_code=500)
    
    

@match_router.delete("/match_results", tags=["match"])
async def delete_match_result(request: Request, deleteRequest: DeleteMatchResultRequest, db: AsyncSession = Depends(database.get_session)):
    if request.state.user_session is None or request.state.user_session.user_role != UserRole.admin:
        return HTTPException(status_code=401, detail="Unauthorized")
    match_results_controller = MatchController(
        match_repository=MatchRepository(db),
        team_repository=TeamRepository(db),
        match_result_lock=DistributedLock(MATCH_LOCK_KEY)
    )
    try:
        is_ok = await match_results_controller.delete_match(
            round_number=deleteRequest.round_number,
            match_id=deleteRequest.match_id
        )
        if is_ok:
            logging.info(f"{request.state.user_session.user_role} action: Match result deleted successfully")
            return JSONResponse(content={"detail":"match result deleted successfully"}, status_code=200)
        else:
            logging.error(f"{request.state.user_session.user_role} action: Match result deletion failed")
            return JSONResponse(content={"detail":"match result deletion failed"}, status_code=500)
    except Exception as e:
        logging.error(f"{request.state.user_session.user_role} action: Error deleting match result: {e}")
        return JSONResponse(content={"detail":"match result deletion failed"}, status_code=500)


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