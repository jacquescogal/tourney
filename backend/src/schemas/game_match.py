from pydantic import BaseModel, Field, field_validator
from typing import List

class GameMatchBase(BaseModel):
    match_id: int = Field(..., example=1, description='Unique Match ID')
    round_number: int = Field(..., example=1, description='Round Number')

    @field_validator("round_number")
    def validate_round_number(cls, v):
        # validates:
        # round number should be between 1 and 3(final round) inclusive
        if v < 1 or v > 3:
            raise ValueError("Round number should be between 1 and 3")
        return v

class CreateGameMatch(GameMatchBase):
    # request body for creating a new match result
    pass

class BatchCreateGameMatch(BaseModel):
    game_matches: List[CreateGameMatch] = Field(..., examples=[{"match_id":1,"round_number":1}], description="list of game matches to be created as a batch")