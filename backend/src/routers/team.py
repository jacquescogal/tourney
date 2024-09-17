from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from src.database.database import Database
from src.repositories.team import TeamRepository
from src.controllers.team import TeamController
from src.schemas.team import BatchRegisterTeamRequest
from src.redis.lock import DistributedLock, TEAM_LOCK_KEY

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

