from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
from enum import Enum

# refer to model.user Enum('player', 'manager', 'admin')
class UserRole(str, Enum):
    player = 'player'
    manager = 'manager'
    admin = 'admin'

class UserBase(BaseModel):
    # base user model
    username: str = Field(..., example='user1', description='Username of the user')
    password: str = Field(..., example='password', description='Password of the user')
    
    @field_validator('username')
    def make_lower(cls, v:str):
        # converts the username to lowercase
        return v.lower()
    
    @field_validator('username')
    def validate_username(cls, v):
        # validates:
        # username length is between 1 and 50 characters
        # username can only contain alphanumeric characters, underscores, hyphens and spaces
        if len(v) == 0:
            raise ValueError('Username cannot be empty')
        elif len(v) > 50:
            raise ValueError('Username is too long (max 50 characters)')
        elif not v.replace(' ', '').replace('-', '').replace('_', '').isalnum():
            raise ValueError('Username can only contain alphanumeric characters, underscores, hyphens and spaces')
        return v
    
    @field_validator('password')
    def validate_password(cls, v):
        # validates:
        # password length is between 1 and 50 characters
        if len(v) == 0:
            raise ValueError('Password cannot be empty')
        elif len(v) > 72:
            raise ValueError('Password is too long (max 50 characters)')
        return v

class UserLoginRequest(UserBase):
    pass

class UserCreateRequest(UserBase):
    user_role: UserRole = Field(..., example='player', description='Role of the user')
    team_id: Optional[int] = Field(None, example=1, description='Team ID')
    
    @field_validator('user_role')
    def validate_user_role(cls, v):
        # validates:
        # user_role should be one of the three roles
        if v not in {UserRole.player, UserRole.manager, UserRole.admin}:
            raise ValueError('User role should be one of player, manager, admin')
        return v

class UserSessionStoreValue(BaseModel):
    user_id: int = Field(..., example=1, description='User ID')
    user_role: UserRole = Field(..., example='player', description='Role of the user')
    team_id: Optional[int] = Field(None, example=1, description='Team ID')

    @model_validator(mode="after")
    def validate_team_id(self):
        # validates:
        # team_id should be none null if user_role is player or manager
        if self.user_role in {UserRole.player, UserRole.manager} and self.team_id is None:
            raise ValueError('Team ID cannot be null for player or manager')
        return self
    

class SessionTokenAndUserSession(BaseModel):
    session_token: str = Field(..., example='session_token', description='Session token')
    user_session: UserSessionStoreValue = Field(..., description='User session')