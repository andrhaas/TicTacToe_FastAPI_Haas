

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.game_logic import make_move, get_current_player
from app.routers.auth import get_current_user
from app import models

router = APIRouter(prefix="/games", tags=["Games"])


@router.post("/", response_model=schemas.GameResponse, status_code=status.HTTP_201_CREATED)
def create_game(
    player_symbol: str = "X",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Erstellt ein neues TicTacToe-Spiel für den eingeloggten Benutzer. Wähle 'X' oder 'O'."""
    player_symbol = player_symbol.upper()
    if player_symbol not in ["X", "O"]:
        raise HTTPException(status_code=400, detail="Symbol muss 'X' oder 'O' sein.")
        
    game = crud.create_game(db, owner_id=current_user.id, player_symbol=player_symbol)
    game.message = "Spiel gestartet! X macht den ersten Zug."
    return game


@router.get("/", response_model=list[schemas.GameResponse])
def list_games(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Gibt alle Spiele zurück (inkl. Board-Status und Spielverlauf)."""
    return crud.get_all_games(db)


@router.get("/{game_id}", response_model=schemas.GameResponse)
def get_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Gibt Details eines bestimmten Spiels zurück."""
    game = crud.get_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden.")
    return game


@router.put("/{game_id}/move/{position}", response_model=schemas.GameResponse)
def make_move_endpoint(
    game_id: int,
    position: int,
    symbol: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
   
    game = crud.get_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden.")

    if game.status != "ongoing":
        raise HTTPException(
            status_code=400,
            detail=f"Dieses Spiel ist bereits beendet (Status: {game.status}).",
        )

    if position < 1 or position > 9:
        raise HTTPException(status_code=400, detail="Position muss zwischen 1 und 9 liegen.")

    symbol = symbol.upper()
    if symbol not in ["X", "O"]:
        raise HTTPException(status_code=400, detail="Symbol muss X oder O sein.")
        
    expected_player = get_current_player(game.board)
    if symbol != expected_player:
         raise HTTPException(status_code=400, detail=f"Du bist nicht dran. Aktueller Spieler ist {expected_player}.")

    try:
        new_board, winner, draw = make_move(game.board, position, symbol)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


    if winner:
        game = crud.update_game(db, game, new_board, symbol, f"won_{winner}")
        game.message = f"Glückwunsch! {winner} hat gewonnen"
        return game
    elif draw:
        game = crud.update_game(db, game, new_board, symbol, "draw")
        game.message = "Unentschieden! Keine Züge mehr möglich"
        return game
        
    next_player = "O" if symbol == "X" else "X"
    game = crud.update_game(db, game, new_board, next_player, "ongoing")
    game.message = f"Guter Zug von {symbol}. Spieler {next_player} ist jetzt am Zug."

    return game


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Löscht ein abgeschlossenes Spiel."""
    game = crud.get_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden.")

    deleted = crud.delete_game(db, game_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Löschen fehlgeschlagen.")
