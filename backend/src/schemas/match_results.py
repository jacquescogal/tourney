from pydantic import BaseModel, Field, field_validator
from typing import List

class MatchResultBase(BaseModel):
    # goals earned by one of the two teams
    team_name: str = Field(..., example='Team A', description="Name of the team")
    goals_scored: int = Field(..., example=2, description="Number of goals scored by the team for the match")

class CreateMatchResultsRequest(BaseModel):
    # request body for creating a new match result
    match_id: int = Field(..., example=1, description="Unique identifier for the match")
    result: List[MatchResultBase] = Field(..., example=[{"team_name": "Team A", "goals_scored": 2},{"team_name": "Team B", "goals_scored": 2}], description="List of team names and goals scored")

    @field_validator("result")
    def validate_result(cls, v):
        # validates:
        # match results should hold exactly 2 result
        if len(v) != 2:
            raise ValueError("Exactly two teams need to be be defined for a match")
        return v

class BatchCreateMatchResultsRequest(BaseModel):
    results: List[CreateMatchResultsRequest] = Field(..., examples=[{"match_id":1,"result":[{"team_name": "Team A", "goals_scored": 2},{"team_name": "Team B", "goals_scored": 2}]}], description="list of match results to be created as a batch")

    @field_validator("results")
    def validate_results(cls, v):
        # validates:
        # results need to have at least one result in array
        if len(v) == 0:
            raise ValueError("Results array cannot be empty")
        return v