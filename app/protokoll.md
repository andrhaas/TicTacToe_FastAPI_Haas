# Protokoll: Weiterentwicklung der TicTacToe FastAPI (Cross-Account Play & History)

**Datum:** 27.04.2026


---

## 1. Vorheriger Commit 
https://github.com/andrhaas/TicTacToe_FastAPI_Haas/commit/69e77070cfaa0193ba25b276a16aed023cddd4e0

## 2. Ziele für die heutige Unterrichtseinheit
Mein Ziel für diese Einheit war es, das TicTacToe-Backend so zu erweitern, dass das Spielen zwischen zwei verschiedenen Accounts gut funktioniert. Bei ersten manuellen Tests (z.B. mit Edge als User A und Chrome als User B) ist mir aufgefallen, dass Züge zwar verarbeitet wurden, aber die Historie nicht passend synchronisiert war. Außerdem fehlten einige Funktionen zur besseren Spielverwaltung.

Konkrete Teilziele der heutigen Einheit:
1. **Zweispieler-Zuordnung:** Spiele sollen nicht nur dem Ersteller gehören, sondern auch dem beitretenden Spieler zugewiesen werden.
2. **Verbesserte Spielstatistiken:** Die API soll personalisierte Listen ausgeben, welche Spiele gewonnen und welche verloren wurden.
3. **Move-Historie:** Es soll nachträglich einsehbar sein, wer welchen Zug wann in welcher Reihenfolge gemacht hat.
4. **Sicherheit und Nicht schummeln:** Kein Spieler darf in einem Multiplayer-Match die Rolle oder Züge des anderen Spielers klauen.

## 3. Umsetzung und Gedanken hinter den Veränderungen

### 3.1. Zweispieler-Logging (`player2_id`)
**Problem:** Wenn ich in einem Browser das Spiel erstellte und im anderen Browser "O" spielte, erschien das Spiel beim zweiten Account nicht in der Liste *"Meine gespielten Spiele"*.
**Lösung:**
- Datenbankmodell für Spieler 2 (`player2_id`) erweitert
- Automatisches Eintragen der ID beim ersten Zug des Gegners
- Schema angepasst für die API-Rückgabe

### 3.2. Filtern nach Sieg, Niederlage & dynamische Nachrichten
**Idee:** Ich wollte Endpunkte für das Profil des Users haben, das Siege und Niederlagen trennt, und wollte, dass direkt in der API steht: *"Du hast gewonnen"* statt nur *"Spieler XY hat gewonnen"*.
**Lösung:** 
- Neue Endpunkte `/games/me/won` und `/games/me/lost` erstellt
- Datenbank-Abfrage angepasst, um auch als Zweitspieler teilgenommene Spiele zu finden
- Logik hinzugefügt, die dem Nutzer personalisierte Statusmeldungen ("Du hast gewonnen") zurückgibt

### 3.3. Implementierung der Move-Historie
**Problem:** Bei jedem `/move/` Aufruf wurde das Feld in der DB einfach als 9-Zeichen-String (z.B. "X.O......") überschrieben. Nach Spielende wusste niemand mehr, wie das Match verlaufen war.
**Lösung:**
- Neue Datenbanktabelle `moves` für jeden einzelnen Zug angelegt
- Züge werden beim Aufruf von `/move/` jetzt zusätzlich als einzelner Eintrag mitgeloggt
- Neuer Endpunkt `/games/{game_id}/moves` liefert chronologische Move-Historie zurück

### 3.4. Die Cheat-Protection
**Problem:** Mir ist aufgefallen, dass User B (Spieler "O") einfach im Endpunkt X übergeben konnte. Wenn es der Turn für X war, hat das Backend den Zug für User B ausgeführt, weil er sich fälschlicherweise als "X" ausgab.
**Lösung:** 
- Verifizierung im Code, ob aufrufender User wirklich Eigentümer des gespielten Symbols ist
- Funktioniert auch wenn sich ein Spieler versucht einzuschleichen

## 4. Aktueller Commit
https://github.com/andrhaas/TicTacToe_FastAPI_Haas/commit/1c8b9247b3d4c25a91706d60afd99606bd1f364b

## 5. Diff
diff --git a/app/crud.py b/app/crud.py
index d1bff56..2d0f25b 100644
--- a/app/crud.py
+++ b/app/crud.py
@@ -48,6 +48,13 @@ def get_all_games(db: Session) -> list[models.Game]:
     return db.query(models.Game).all()
 
 
+def get_user_games(db: Session, user_id: int) -> list[models.Game]:
+    from sqlalchemy import or_
+    return db.query(models.Game).filter(
+        or_(models.Game.owner_id == user_id, models.Game.player2_id == user_id)
+    ).all()
+
+
 def update_game(db: Session, game: models.Game, board: str, current_player: str, status: str) -> models.Game:
     game.board = board
     game.current_player = current_player
@@ -64,3 +71,20 @@ def delete_game(db: Session, game_id: int) -> bool:
     db.delete(game)
     db.commit()
     return True
+
+
+def create_move(db: Session, game_id: int, user_id: int, position: int, symbol: str) -> models.Move:
+    move = models.Move(
+        game_id=game_id,
+        user_id=user_id,
+        position=position,
+        symbol=symbol
+    )
+    db.add(move)
+    db.commit()
+    db.refresh(move)
+    return move
+
+def get_game_moves(db: Session, game_id: int) -> list[models.Move]:
+    return db.query(models.Move).filter(models.Move.game_id == game_id).order_by(models.Move.created_at).all()
+
diff --git a/app/games.py b/app/games.py
index 6a50b24..290f1f1 100644
--- a/app/games.py
+++ b/app/games.py
@@ -28,23 +28,92 @@ def create_game(
     return game
 
 
+def set_game_list_message(game: models.Game, current_user_id: int):
+    """Setzt eine benutzerfreundliche Nachricht f├╝r die Spiel├╝bersicht."""
+    if game.status.startswith("won_"):
+        winner_symbol = game.status.split("_")[1]
+        
+        # wer hat gwonnen
+        if winner_symbol == game.player_symbol:
+            winner_id = game.owner_id
+            winner_username = game.owner.username if game.owner else "Unbekannt"
+        else:
+            winner_id = game.player2_id
+            winner_username = game.player2.username if game.player2 else "Unbekannt"
+            
+        # ├£berpr├╝fe, ob der eingeloggte User gewonnen hat
+        if winner_id == current_user_id:
+            game.message = "Du hast gewonnen!"
+        else:
+            game.message = f"{winner_username} hat gewonnen!"
+            
+    elif game.status == "draw":
+        game.message = "Unentschieden!"
+    else:
+        game.message = "Spiel l├ñuft noch..."
+
+
 @router.get("/", response_model=list[schemas.GameResponse])
 def list_games(
     db: Session = Depends(get_db),
     current_user: models.User = Depends(get_current_user),
 ):
-    return crud.get_all_games(db)
+    games = crud.get_all_games(db)
+    for game in games:
+        set_game_list_message(game, current_user.id)
+    return games
 
 
 @router.get("/user/{username}", response_model=list[schemas.GameResponse])
 def get_games_by_username(
     username: str,
-    db: Session = Depends(get_db)
+    db: Session = Depends(get_db),
+    current_user: models.User = Depends(get_current_user)
 ):
     user = crud.get_user_by_username(db, username)
     if not user:
         raise HTTPException(status_code=404, detail="User not found")
-    return user.games
+    
+    games = crud.get_user_games(db, user.id)
+    for game in games:
+        set_game_list_message(game, current_user.id)
+    return games
+
+
+def is_winner(game: models.Game, user_id: int) -> bool:
+    if not game.status.startswith("won_"):
+        return False
+    winner_symbol = game.status.split("_")[1]
+    if winner_symbol == game.player_symbol:
+        return game.owner_id == user_id
+    else:
+        return game.player2_id == user_id
+
+
+@router.get("/me/won", response_model=list[schemas.GameResponse])
+def get_won_games(
+    db: Session = Depends(get_db),
+    current_user: models.User = Depends(get_current_user)
+):
+    games = crud.get_user_games(db, current_user.id)
+    won_games = [g for g in games if is_winner(g, current_user.id)]
+    for game in won_games:
+        set_game_list_message(game, current_user.id)
+    return won_games
+
+
+@router.get("/me/lost", response_model=list[schemas.GameResponse])
+def get_lost_games(
+    db: Session = Depends(get_db),
+    current_user: models.User = Depends(get_current_user)
+):
+    games = crud.get_user_games(db, current_user.id)
+    # Verloren hat man, wenn ein Spieler gewonnen hat und man selbst es nicht war
+    lost_games = [g for g in games if g.status.startswith("won_") and not is_winner(g, current_user.id)]
+    for game in lost_games:
+        set_game_list_message(game, current_user.id)
+    return lost_games
+
 
 
 @router.get("/{game_id}", response_model=schemas.GameResponse)
@@ -105,11 +174,39 @@ def make_move_endpoint(
     if symbol != expected_player:
          raise HTTPException(status_code=400, detail=f"Du bist nicht dran. Aktueller Spieler ist {expected_player}.")
 
+    # Schummeln verboten halt stop
+    owner_symbol = game.player_symbol
+    player2_symbol = "O" if owner_symbol == "X" else "X"
+
+    if current_user.id == game.owner_id:
+        if symbol != owner_symbol:
+            raise HTTPException(status_code=403, detail=f"Cheat-Schutz: Du bist Spieler {owner_symbol}!")
+    elif game.player2_id is not None and current_user.id == game.player2_id:
+        if symbol != player2_symbol:
+            raise HTTPException(status_code=403, detail=f"Cheat-Schutz: Du bist Spieler {player2_symbol}!")
+    elif game.player2_id is None:
+        # Der Spieler versucht beizutreten
+        if symbol != player2_symbol:
+            raise HTTPException(status_code=403, detail=f"Cheat-Schutz: Das andere Symbol ({owner_symbol}) geh├Ârt bereits dem Raum-Ersteller!")
+        # Logge den zweiten Spieler, falls noch nicht gesetzt
+        game.player2_id = current_user.id
+    else:
+        raise HTTPException(status_code=403, detail="Cheat-Schutz: Du bist nicht Teil dieses Spiels!")
+    
+
     try:
         new_board, winner, draw = make_move(game.board, position, symbol)
     except ValueError as e:
         raise HTTPException(status_code=400, detail=str(e))
 
+    # Z├╝ge in datenbank speichern tuff
+    crud.create_move(
+        db, 
+        game_id=game_id, 
+        user_id=current_user.id, 
+        position=position, 
+        symbol=symbol
+    )
 
     if winner:
         game = crud.update_game(db, game, new_board, symbol, f"won_{winner}")
@@ -127,6 +224,20 @@ def make_move_endpoint(
     return game
 
 
+@router.get("/{game_id}/moves", response_model=list[schemas.MoveResponse])
+def get_game_moves(
+    game_id: int,
+    db: Session = Depends(get_db),
+    current_user: models.User = Depends(get_current_user),
+):
+    """Gibt die Move-Historie eines Spiels zur├╝ck."""
+    game = crud.get_game(db, game_id)
+    if not game:
+        raise HTTPException(status_code=404, detail="Spiel nicht gefunden.")
+    
+    return crud.get_game_moves(db, game_id)
+
+
 @router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
 def delete_game(
     game_id: int,
diff --git a/app/models.py b/app/models.py
index 5605991..c80c81e 100644
--- a/app/models.py
+++ b/app/models.py
@@ -12,7 +12,8 @@ class User(Base):
     hashed_password = Column(String, nullable=False)
     created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
 
-    games = relationship("Game", back_populates="owner")
+    games = relationship("Game", back_populates="owner", foreign_keys="[Game.owner_id]")
+    games_as_player2 = relationship("Game", back_populates="player2", foreign_keys="[Game.player2_id]")
 
 
 class Game(Base):
@@ -20,6 +21,7 @@ class Game(Base):
 
     id = Column(Integer, primary_key=True, index=True)
     owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
+    player2_id = Column(Integer, ForeignKey("users.id"), nullable=True)
 
     board = Column(String(9), default=".........", nullable=False)
     current_player = Column(String(1), default="X", nullable=False)
@@ -30,7 +32,9 @@ class Game(Base):
     updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))
 
-    owner = relationship("User", back_populates="games")
+    owner = relationship("User", back_populates="games", foreign_keys=[owner_id])
+    player2 = relationship("User", back_populates="games_as_player2", foreign_keys=[player2_id])
+    moves = relationship("Move", back_populates="game", cascade="all, delete-orphan")
 
     @property
     def formatted_board(self) -> list[str]:
@@ -43,3 +47,16 @@ class Game(Base):
             f" {b[6]} | {b[7]} | {b[8]} "
         ]
 
+class Move(Base):
+    __tablename__ = "moves"
+
+    id = Column(Integer, primary_key=True, index=True)
+    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
+    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
+    position = Column(Integer, nullable=False)
+    symbol = Column(String(1), nullable=False)
+    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
+
+    game = relationship("Game", back_populates="moves")
+    user = relationship("User")
+
diff --git a/app/protokoll.md b/app/protokoll.md
new file mode 100644
index 0000000..25595d0
--- /dev/null
+++ b/app/protokoll.md
@@ -0,0 +1,50 @@
+# Protokoll: Weiterentwicklung der TicTacToe FastAPI (Cross-Account Play & History)
+
+**Datum:** 27.04.2026
+**Zweck:** Dokumentation der heutigen ├änderungen
+
+---
+
+## 1. Vorheriger Commit 
+*(Link zum Projektstand am Beginn der Einheit einf├╝gen)*
+
+## 2. Ziele f├╝r die heutige Unterrichtseinheit
+Mein Ziel f├╝r diese Einheit war es, das TicTacToe-Backend so zu erweitern, dass das Spielen zwischen zwei verschiedenen Accounts reibungslos und fair funktioniert. Bei ersten manuellen Tests (z.B. mit Edge als User A und Chrome als User B) ist mir aufgefallen, dass Z├╝ge zwar verarbeitet wurden, aber die Historie nicht passend synchronisiert war. Au├ƒerdem fehlten einige Funktionen zur besseren Spielverwaltung.
+
+Konkrete Teilziele der heutigen Einheit:
+1. **Zweispieler-Zuordnung:** Spiele sollen nicht nur dem Ersteller geh├Âren, sondern auch dem beitretenden Spieler zugewiesen werden.
+2. **Verbesserte Spielstatistiken:** Die API soll personalisierte Listen ausgeben, welche Spiele gewonnen und welche verloren wurden.
+3. **Move-Historie:** Es soll nachtr├ñglich einsehbar sein, wer welchen Zug wann in welcher Reihenfolge gemacht hat.
+4. **Sicherheit und Cheat-Protection:** Kein Spieler darf in einem Multiplayer-Match die Rolle oder Z├╝ge des anderen Spielers klauen.
+
+## 3. Umsetzung und Gedanken hinter den Ver├ñnderungen
+
+### 3.1. Zweispieler-Logging (`player2_id`)
+**Problem:** Wenn ich in einem Browser das Spiel erstellte und im anderen Browser "O" spielte, erschien das Spiel beim zweiten Account nicht in der Liste *"Meine gespielten Spiele"*.
+**L├Âsung:** Ich habe die Datenbank Tabelle `games` in `models.py` um eine optionale Spalte `player2_id` (ForeignKey auf `users.id`) erweitert. Wenn jetzt jemand (der nicht der Ersteller ist) in einem noch offenen Spiel einen Zug macht, wird seine User-ID automatisch als `player2_id` eingetragen. Das `GameResponse` Schema wurde entsprechend angepasst, um beide User-IDs in der API zur├╝ckzugeben.
+
+### 3.2. Filtern nach Sieg, Niederlage & dynamische Nachrichten
+**Idee:** Ich wollte Endpunkte f├╝r das Profil des Users haben, das Siege und Niederlagen trennt, und wollte, dass direkt in der API steht: *"Du hast gewonnen"* statt nur *"Spieler XY hat gewonnen"*.
+**L├Âsung:** 
+- Ich habe die neuen Routen `GET /games/me/won` und `GET /games/me/lost` erstellt.
+- In `crud.py` wurde die Methode `get_user_games` eingef├╝hrt, die SQLAlchemy's `or_` Operator nutzt, um Spiele aus der DB zu fischen, in denen ich entweder Ersteller **oder** Zweitspieler bin.
+- Eine Hilfsfunktion validiert jetzt beim Durchsuchen der Listen, wer gewonnen hat, gleicht dies mit der `current_user.id` ab und setzt die `game.message` entsprechend.
+
+### 3.3. Implementierung der Move-Historie
+**Problem:** Bei jedem `/move/` Aufruf wurde das Feld in der DB einfach als 9-Zeichen-String (z.B. "X.O......") ├╝berschrieben. Nach Spielende wusste niemand mehr, wie das Match verlaufen war.
+**L├Âsung:**
+Ich habe in der Datenbank die neue Tabelle `moves` (`id`, `game_id`, `user_id`, `position`, `symbol`, `created_at`) erstellt. Der Endpunkt zum Z├╝ge machen legt jetzt jedes Mal auch ein `Move`-Objekt an. Mit dem neuen Endpunkt `GET /games/{game_id}/moves` l├ñsst sich das Match nun wie in einer Replay-Funktion auflisten.
+
+### 3.4. Die Cheat-Protection
+**Problem:** Mir ist aufgefallen, dass User B (Spieler "O") einfach im Endpunkt `?symbol=X` ├╝bergeben konnte. Wenn es der Turn f├╝r X war, hat das Backend den Zug f├╝r User B ausgef├╝hrt, weil er sich f├ñlschlicherweise als "X" ausgab.
+**L├Âsung:** 
+Im `make_move_endpoint` steht jetzt harte Validierungs-Logik:
+- Geh├Ârst du als aktueller Webserver-User zu Symbol "X" oder "O"?
+- Liefert dein Request das falsche Symbol ab? -> `HTTP 403: Du bist Spieler O!`.
+- Versucht eine dritte Person (User C) einzusteigen, wenn der Raum schon einen `player2` hat? -> `HTTP 403: Du bist nicht Teil dieses Spiels!`.
+
+## 4. Aktueller Commit
+*(Link zum neuen Commit am Ende der Einheit einf├╝gen)*
+
+## 5. Diff
+*(Diff oder Vergleich der Dateien vor/nach einf├╝gen)*
\ No newline at end of file
diff --git a/app/schemas.py b/app/schemas.py
index b1fbc09..d5b5b32 100644
--- a/app/schemas.py
+++ b/app/schemas.py
@@ -40,6 +40,7 @@ class Token(BaseModel):
 class GameResponse(BaseModel):
     id: int
     owner_id: int
+    player2_id: int | None = None
     player_symbol: str
     board: str
     formatted_board: list[str]
@@ -54,7 +55,10 @@ class GameResponse(BaseModel):
 
 class MoveResponse(BaseModel):
     id: int
-    board: str
-    current_player: str
-    status: str
-    message: str
+    game_id: int
+    user_id: int
+    position: int
+    symbol: str
+    created_at: datetime
+
+    model_config = {"from_attributes": True}
diff --git a/tictactoe.db b/tictactoe.db
index 0806db4..8ab65bf 100644
Binary files a/tictactoe.db and b/tictactoe.db differ
