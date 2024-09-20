from pydantic import BaseModel, field_validator, Field
from datetime import datetime

class TeamBase(BaseModel):
    team_id: int = Field(..., example=1, description='Team ID')
    team_name: str = Field(..., example='Team 1', description='Team Name')
    registration_day_of_year: int = Field(..., example=1630483200, description='Registration Date in Unix Timestamp')
    registration_date_ddmm: str = Field(..., example='01/12', description='Registration Date in DD/MM format')
    group_number: int = Field(..., example=1, description='Group Number')

class RegisterTeamRequest(BaseModel):
    """
    Schema for registering a new team
    """
    team_name: str = Field(..., example='Team 1', description='Team Name')
    registration_date_ddmm: str = Field(..., example='01/12', description='Registration Date in DD/MM format')
    group_number: int = Field(..., example=1, description='Group Number')

    # validate team name
    @field_validator('team_name')
    def validate_team_name(cls, v):
        # validates:
        # team name length is between 1 and 50 characters
        # team name can only contain alphanumeric characters, underscores, hyphens and spaces
        if len(v) == 0:
            raise ValueError('Team name cannot be empty')
        elif len(v) > 50:
            raise ValueError('Team name is too long (max 50 characters)')
        elif not v.replace(' ', '').replace('-', '').replace('_', '').isalnum():
            raise ValueError('Team name can only contain alphanumeric characters, underscores, hyphens and spaces')
        return v

    # validate registration date
    @field_validator('registration_date_ddmm')
    def validate_registration_date(cls, v):
        # validates the registration date format adheres to DD/MM
        if len(v) != 5:
            raise ValueError('Invalid registration date format')
        if not v[0:2].isnumeric() or not v[3:5].isnumeric() or v[2] != '/':
            raise ValueError('Invalid registration date format')
        try:
            # strptime() will raise ValueError if the date is invalid
            # the first argument must be a full date, so we append a year
            datetime.strptime(f"{v}/1972", '%d/%m/%Y')
        except ValueError:
            raise ValueError('Invalid registration date format')
        return v
    
    # validate group number
    @field_validator('group_number')
    def validate_group_number(cls, v):
        # validates:
        # group number is either 1 or 2
        if v not in {1, 2}:
            raise ValueError('Invalid group number')
        return v

class BatchRegisterTeamRequest(BaseModel):
    """
    Schema for registering multiple teams at once
    """
    teams: list[RegisterTeamRequest] = Field(..., example=[{'team_name': 'Team 1', 'registration_date_ddmm': '01/12', 'group_number': 1}], description='List of Teams to Register')

class TeamMatchUpDetail(BaseModel):
    opponent_team_id: int = Field(..., example=2, description='Opponent Team ID')
    opponent: str = Field(..., example='Team 2', description='Opponent Team Name')
    round_number: int = Field(..., example=1, description='Round Number')
    match_id: int = Field(..., example=1, description='Match ID')
    goals_scored: int = Field(0, example=2, description='Goals Scored in the Match')
    goals_conceded: int = Field(..., example=1, description='Goals Conceded in the Match')

class TeamDetails(TeamBase):
    team_name: str = Field(..., example='Team 1', description='Team Name')
    registration_date_ddmm: str = Field(..., example='01/12', description='Registration Date in DD/MM format')
    group_number: int = Field(..., example=1, description='Group Number')
    match_ups: list[TeamMatchUpDetail] = Field(..., example=[{'opponent': 'Team 2', 'round_number': 1, 'match_id': 1, 'goals_scored': 2, 'goals_conceded': 1}], description='List of Match Ups')

class TeamUpdateRequest(BaseModel):
    team_name: str = Field(..., example='Team 1', description='Team Name')
    registration_date_ddmm: str = Field(..., example='01/12', description='Registration Date in DD/MM format')