from pydantic import BaseModel, field_validator
from datetime import datetime


#Auth Schemas

class UserRegister(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Username must not be empty")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 4:
            raise ValueError("Password must be at least 4 characters")
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Game Schemas

class GameResponse(BaseModel):
    id: int
    owner_id: int
    player_symbol: str
    board: str
    formatted_board: list[str]
    current_player: str
    status: str
    created_at: datetime
    updated_at: datetime
    message: str | None = None

    model_config = {"from_attributes": True}


class MoveResponse(BaseModel):
    id: int
    board: str
    current_player: str
    status: str
    message: str
