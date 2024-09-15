from pydantic import BaseModel, validator, Field
from typing import Optional

class Response(BaseModel):
    code: int = Field(..., example=200, description='HTTP Status Code')
    message: str = Field(..., example='Success', description='Response Message')