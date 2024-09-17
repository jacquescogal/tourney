from pydantic import BaseModel, Field, field_validator
from typing import List

class TeamRank(BaseModel):
    position: int = Field(..., example=1, description="Position of the team in the ranking")
    is_tied: bool = Field(..., example=False, description="Flag to indicate if the team is tied with another team")
    is_qualified: bool = Field(default=False, example=True, description="Flag to indicate if the team is qualified for the next round")
    team_id: int = Field(..., example=1, description="Unique identifier for the team")
    team_name: str = Field(..., example='Team A', description="Name of the team")
    goals: int = Field(..., example=5, description="Number of goals scored by the team")
    wins: int = Field(..., example=2, description="Number of wins by the team")
    draws: int = Field(..., example=1, description="Number of draws by the team")
    losses: int = Field(..., example=0, description="Number of losses by the team")
    registration_date_ddmm: str = Field(..., example='01/01', description="Date when the team joined the tournament in DD/MM")
    registration_day_of_year: int = Field(..., example=1609459200, description="Date when the team joined the tournament in Unix timestamp")
class GroupRanking(BaseModel):
    group_number: int = Field(..., example=1, description="Group number of the team")
    team_rankings: List[TeamRank] = Field(..., example=[{"position":1,"team_id":1,"team_name":"Team A","wins":2,"draws":1,"losses":0,"registration_date":"01/01"}], description="List of team rankings in the group")

class GetRankingResponse(BaseModel):
    round_number: int = Field(..., example=1, description="Round number for the matches")
    group_rankings: List[GroupRanking] = Field(..., example=[{"group_number":1,"team_rankings":[{"position":1,"team_id":1,"team_name":"Team A","wins":2,"draws":1,"losses":0,"registration_date":"01/01"}]}], description="List of group rankings for the round")

    @field_validator("round_number")
    def validate_round_number(cls, v):
        # validates:
        # round number should be between 1 and 3(final round) inclusive
        if v < 1 or v > 3:
            raise ValueError("Round number should be between 1 and 3")
        return v
