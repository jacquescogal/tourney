from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from src.database.database import Database
from src.repositories.team import TeamRepository
from src.controllers.team import TeamController
from src.schemas.team import BatchRegisterTeamRequest, TeamBase
from src.redis.lock import DistributedLock, TEAM_LOCK_KEY
from typing import List

team_router = APIRouter()
database = Database.get_instance()

@team_router.post("/teams", tags=["team"])
async def create_team(request: BatchRegisterTeamRequest, db: AsyncSession = Depends(database.get_session)):
    """
    API endpoint to create teams in batch.
    """
    team_controller = TeamController(TeamRepository(db), DistributedLock(TEAM_LOCK_KEY))
    is_ok = await team_controller.create_teams(
        request_teams=request.teams
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
    team = await team_controller.get_team_details_for_id(team_id)
    if team is None:
        return JSONResponse(content={"detail":"team not found"}, status_code=404)
    return JSONResponse(content=team.dict(), status_code=200)