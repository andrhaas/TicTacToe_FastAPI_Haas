from pydantic import BaseModel, field_validator
from datetime import datetime



class UserRegister(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Username darf ned leer sein")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 4:
            raise ValueError("Password muss länger als 4 zeichn sein")
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"




class GameResponse(BaseModel):
    id: int
    owner_id: int
    player2_id: int | None = None
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
    game_id: int
    user_id: int
    position: int
    symbol: str
    created_at: datetime

    model_config = {"from_attributes": True}
