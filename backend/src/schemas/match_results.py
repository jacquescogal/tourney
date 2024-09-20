from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List

class MatchResultBase(BaseModel):
    # goals earned by one of the two teams
    team_name: str = Field(..., example='Team A', description="Name of the team")
    goals_scored: int = Field(..., example=2, description="Number of goals scored by the team for the match")

class MatchResultSparse(BaseModel):
    match_id: int = Field(..., example=1, description="Unique identifier for the match")
    team_id: int = Field(..., example=1, description="Unique identifier for the team")
    team_name: str = Field(..., example='Team A', description="Name of the team")

class MatchResultDetailed(BaseModel):
    group_number: int = Field(..., example=1, description="Group number of the team")
    match_id: int = Field(..., example=1, description="Unique identifier for the match")
    team_id: int = Field(..., example=1, description="Unique identifier for the team")
    team_name: str = Field(..., example='Team A', description="Name of the team")
    goals_scored: int = Field(..., example=2, description="Number of goals scored by the team for the match")
    registration_day_of_year: int = Field(..., example=1609459200, description="Date when the team joined the tournament in Unix timestamp")

class CreateMatchResults(BaseModel):
    # request body for creating a new match result
    result: List[MatchResultBase] = Field(..., example=[{"team_name": "Team A", "goals_scored": 2},{"team_name": "Team B", "goals_scored": 2}], description="List of team names and goals scored")

    @field_validator("result")
    def validate_result(cls, v):
        # validates:
        # match results should hold exactly 2 result
        if len(v) != 2:
            raise ValueError("Exactly two teams need to be be defined for a match")
        return v

class BatchCreateMatchResultsRequest(BaseModel):
    results: List[CreateMatchResults] = Field(..., example=[{"result":[{"team_name": "Team A", "goals_scored": 2},{"team_name": "Team B", "goals_scored": 2}]}], description="list of match results to be created as a batch")
    round_number: int = Field(..., example=1, description="Round number for the matches")

    @field_validator("results")
    def validate_results(cls, v):
        # validates:
        # results need to have at least one result in array
        if len(v) == 0:
            raise ValueError("Results array cannot be empty")
        return v
    
    @field_validator("round_number")
    def validate_round_number(cls, v):
        # validates:
        # round number should be between 1 and 3(final round) inclusive
        if v < 1 or v > 3:
            raise ValueError("Round number should be between 1 and 3")
        return v
    
class MatchResultsConcat(BaseModel):
    # is match result with both team names and goals scored for a match id
    # team 1 is lexically smaller than team 2
    match_id: int = Field(..., example=1, description="Unique identifier for the match")
    round_number: int = Field(..., example=1, description="Round number for the match")
    team_1_id: int = Field(..., example=1, description="Unique identifier for the first team")
    team_1_name: str = Field(..., example='Team A', description="Name of the first team")
    team_1_goals: int = Field(..., example=2, description="Number of goals scored by the first team")
    team_2_id: int = Field(..., example=2, description="Unique identifier for the second team")
    team_2_name: str = Field(..., example='Team B', description="Name of the second team")
    team_2_goals: int = Field(..., example=2, description="Number of goals scored by the second team")


class MatchResultsConcatStrict(MatchResultsConcat):
    @model_validator(mode="after")
    def validate_match_results_concat(self):
        # validates:
        # goals scored by both teams should be non-negative
        if self.team_1_goals < 0 or self.team_2_goals < 0:
            raise ValueError("Goals scored should be non-negative")
        if self.team_1_name > self.team_2_name:
            # swap if team 1 is lexically greater than team 2
            self.team_1_name, self.team_2_name = self.team_2_name, self.team_1_name
            self.team_1_id, self.team_2_id = self.team_2_id, self.team_1_id
            self.team_1_goals, self.team_2_goals = self.team_2_goals, self.team_1_goals
        return self
    
class GetMatchResultsResponse(BaseModel):
    match_results: List[MatchResultsConcatStrict] = Field(..., example=[{"match_id": 1, "round_number": 1, "team_1_id": 1, "team_1_name": "Team A", "team_1_goals": 2, "team_2_id": 2, "team_2_name": "Team B", "team_2_goals": 2}], description="List of match results")