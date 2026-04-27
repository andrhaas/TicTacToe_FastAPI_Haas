

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
  
    player_symbol = player_symbol.upper()
    if player_symbol not in ["X", "O"]:
        raise HTTPException(status_code=400, detail="Symbol muss 'X' oder 'O' sein.")
        
    game = crud.create_game(db, owner_id=current_user.id, player_symbol=player_symbol)
    game.message = "Spiel gestartet! X macht den ersten Zug."
    return game


def set_game_list_message(game: models.Game, current_user_id: int):
    """Setzt eine benutzerfreundliche Nachricht für die Spielübersicht."""
    if game.status.startswith("won_"):
        winner_symbol = game.status.split("_")[1]
        
        # wer hat gwonnen
        if winner_symbol == game.player_symbol:
            winner_id = game.owner_id
            winner_username = game.owner.username if game.owner else "Unbekannt"
        else:
            winner_id = game.player2_id
            winner_username = game.player2.username if game.player2 else "Unbekannt"
            
        # Überprüfe, ob der eingeloggte User gewonnen hat
        if winner_id == current_user_id:
            game.message = "Du hast gewonnen!"
        else:
            game.message = f"{winner_username} hat gewonnen!"
            
    elif game.status == "draw":
        game.message = "Unentschieden!"
    else:
        game.message = "Spiel läuft noch..."


@router.get("/", response_model=list[schemas.GameResponse])
def list_games(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    games = crud.get_all_games(db)
    for game in games:
        set_game_list_message(game, current_user.id)
    return games


@router.get("/user/{username}", response_model=list[schemas.GameResponse])
def get_games_by_username(
    username: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user = crud.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    games = crud.get_user_games(db, user.id)
    for game in games:
        set_game_list_message(game, current_user.id)
    return games


def is_winner(game: models.Game, user_id: int) -> bool:
    if not game.status.startswith("won_"):
        return False
    winner_symbol = game.status.split("_")[1]
    if winner_symbol == game.player_symbol:
        return game.owner_id == user_id
    else:
        return game.player2_id == user_id


@router.get("/me/won", response_model=list[schemas.GameResponse])
def get_won_games(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    games = crud.get_user_games(db, current_user.id)
    won_games = [g for g in games if is_winner(g, current_user.id)]
    for game in won_games:
        set_game_list_message(game, current_user.id)
    return won_games


@router.get("/me/lost", response_model=list[schemas.GameResponse])
def get_lost_games(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    games = crud.get_user_games(db, current_user.id)
    # Verloren hat man, wenn ein Spieler gewonnen hat und man selbst es nicht war
    lost_games = [g for g in games if g.status.startswith("won_") and not is_winner(g, current_user.id)]
    for game in lost_games:
        set_game_list_message(game, current_user.id)
    return lost_games



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
    """
    Aufbau des Spielfelds:
   
    ```
     1 | 2 | 3 
    -----------
     4 | 5 | 6 
    -----------
     7 | 8 | 9 
    ```

    Bitte gib als position eine Zahl zwischen 1 und 9 ein.
    """
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

    # Schummeln verboten halt stop
    owner_symbol = game.player_symbol
    player2_symbol = "O" if owner_symbol == "X" else "X"

    if current_user.id == game.owner_id:
        if symbol != owner_symbol:
            raise HTTPException(status_code=403, detail=f"Cheat-Schutz: Du bist Spieler {owner_symbol}!")
    elif game.player2_id is not None and current_user.id == game.player2_id:
        if symbol != player2_symbol:
            raise HTTPException(status_code=403, detail=f"Cheat-Schutz: Du bist Spieler {player2_symbol}!")
    elif game.player2_id is None:
        # Der Spieler versucht beizutreten
        if symbol != player2_symbol:
            raise HTTPException(status_code=403, detail=f"Cheat-Schutz: Das andere Symbol ({owner_symbol}) gehört bereits dem Raum-Ersteller!")
        # Logge den zweiten Spieler, falls noch nicht gesetzt
        game.player2_id = current_user.id
    else:
        raise HTTPException(status_code=403, detail="Cheat-Schutz: Du bist nicht Teil dieses Spiels!")
    

    try:
        new_board, winner, draw = make_move(game.board, position, symbol)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Züge in datenbank speichern tuff
    crud.create_move(
        db, 
        game_id=game_id, 
        user_id=current_user.id, 
        position=position, 
        symbol=symbol
    )

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


@router.get("/{game_id}/moves", response_model=list[schemas.MoveResponse])
def get_game_moves(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Gibt die Move-Historie eines Spiels zurück."""
    game = crud.get_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden.")
    
    return crud.get_game_moves(db, game_id)


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):

    game = crud.get_game(db, game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden.")

    deleted = crud.delete_game(db, game_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Löschen fehlgeschlagen.")
