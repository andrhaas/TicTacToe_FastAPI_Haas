"""
crud.py
Alle Datenbankoperationen für User und Game.
"""

from sqlalchemy.orm import Session
from app import models, schemas
from app.security import hash_password
from app.game_logic import empty_board




def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user_data: schemas.UserRegister) -> models.User:
    hashed = hash_password(user_data.password)
    user = models.User(username=user_data.username, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user




def create_game(db: Session, owner_id: int, player_symbol: str) -> models.Game:
    game = models.Game(
        board=empty_board(),
        current_player="X",
        player_symbol=player_symbol,
        status="ongoing",
        owner_id=owner_id,
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


def get_game(db: Session, game_id: int) -> models.Game | None:
    return db.query(models.Game).filter(models.Game.id == game_id).first()


def get_all_games(db: Session) -> list[models.Game]:
    return db.query(models.Game).all()


def update_game(db: Session, game: models.Game, board: str, current_player: str, status: str) -> models.Game:
    game.board = board
    game.current_player = current_player
    game.status = status
    db.commit()
    db.refresh(game)
    return game


def delete_game(db: Session, game_id: int) -> bool:
    game = get_game(db, game_id)
    if not game:
        return False
    db.delete(game)
    db.commit()
    return True
