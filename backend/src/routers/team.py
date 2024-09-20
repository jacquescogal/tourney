from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from src.database.database import Database
from src.repositories.team import TeamRepository
from src.controllers.team import TeamController
from src.schemas.team import BatchRegisterTeamRequest, TeamBase,TeamDetails, TeamUpdateRequest
from src.redis.lock import DistributedLock, TEAM_LOCK_KEY, MATCH_LOCK_KEY
from typing import List
from fastapi import HTTPException, Request
from src.schemas.user import UserRole
from fastapi import WebSocket, WebSocketDisconnect
from src.controllers.connection_controller import ConnectionController
from src.repositories.match_core import MatchRepository
team_router = APIRouter()
database = Database.get_instance()

@team_router.post("/teams", tags=["team"])
async def create_team(request:Request, batchRequest: BatchRegisterTeamRequest, db: AsyncSession = Depends(database.get_session)):
    """
    API endpoint to create teams in batch.
    """
    if request.state.user_session is None or request.state.user_session.user_role != UserRole.admin:
        return HTTPException(status_code=401, detail="Unauthorized")
    team_controller = TeamController(TeamRepository(db), team_lock=DistributedLock(TEAM_LOCK_KEY))
    is_ok = await team_controller.create_teams(
        request_teams=batchRequest.teams
    )
    if is_ok:
        return JSONResponse(content={"detail":"teams created successfully"}, status_code=200)
    else:
        return JSONResponse(content={"detail":"teams creation failed"}, status_code=500)
    
@team_router.get("/teams", tags=["team"])
async def get_teams(db: AsyncSession = Depends(database.get_session)):
    """
    API endpoint to get all teams.
    """
    team_controller = TeamController(TeamRepository(db))
    teams:List[TeamBase] = await team_controller.get_teams()
    return JSONResponse(content=sorted([team.dict() for team in teams], key=lambda x: x["group_number"]), status_code=200)

@team_router.get("/teams/{team_id}", tags=["team"])
async def get_team(team_id: int, db: AsyncSession = Depends(database.get_session)):
    """
    API endpoint to get team details by team ID.
    """
    team_controller = TeamController(TeamRepository(db))
    team:TeamDetails = await team_controller.get_team_details_for_id(team_id)
    if team is None:
        return JSONResponse(content={"detail":"team not found"}, status_code=404)
    return JSONResponse(content=team.dict(), status_code=200)

@team_router.put("/teams/{team_id}", tags=["team"])
async def update_team(request: Request, team_id: int, team: TeamUpdateRequest, db: AsyncSession = Depends(database.get_session)):
    """
    API endpoint to update team by team ID.
    """
    if request.state.user_session is None or request.state.user_session.user_role != UserRole.admin:
        return HTTPException(status_code=401, detail="Unauthorized")
    team_controller = TeamController(TeamRepository(db), team_lock=DistributedLock(TEAM_LOCK_KEY))
    is_ok = await team_controller.update_team_details_for_id(team_id, team.team_name, registration_date_ddmm=team.registration_date_ddmm)
    if is_ok:
        return JSONResponse(content={"detail":"team updated successfully"}, status_code=200)
    else:
        return JSONResponse(content={"detail":"team update failed"}, status_code=500)

@team_router.delete("/teams/{team_id}", tags=["team"])
async def delete_team(request: Request, team_id: int, db: AsyncSession = Depends(database.get_session)):
    """
    API endpoint to delete team by team ID.
    """
    if request.state.user_session is None or request.state.user_session.user_role != UserRole.admin:
        return HTTPException(status_code=401, detail="Unauthorized")
    team_controller = TeamController(TeamRepository(db), MatchRepository(db), DistributedLock(TEAM_LOCK_KEY), DistributedLock(MATCH_LOCK_KEY))
    is_ok = await team_controller.delete_team(team_id)
    if is_ok:
        return JSONResponse(content={"detail":"team deleted successfully"}, status_code=200)
    else:
        return JSONResponse(content={"detail":"team deletion failed"}, status_code=500)

@team_router.websocket("/ws/teams")
async def websocket_endpoint(websocket: WebSocket):
    connectionController = ConnectionController.get_instance()
    await connectionController.connect(("teams"),websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connectionController.disconnect(("teams"),websocket)
