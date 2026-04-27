# Protokoll: Weiterentwicklung der TicTacToe FastAPI (Cross-Account Play & History)

**Datum:** 27.04.2026
**Zweck:** Dokumentation der heutigen Änderungen

---

## 1. Vorheriger Commit 
*(Link zum Projektstand am Beginn der Einheit einfügen)*

## 2. Ziele für die heutige Unterrichtseinheit
Mein Ziel für diese Einheit war es, das TicTacToe-Backend so zu erweitern, dass das Spielen zwischen zwei verschiedenen Accounts reibungslos und fair funktioniert. Bei ersten manuellen Tests (z.B. mit Edge als User A und Chrome als User B) ist mir aufgefallen, dass Züge zwar verarbeitet wurden, aber die Historie nicht passend synchronisiert war. Außerdem fehlten einige Funktionen zur besseren Spielverwaltung.

Konkrete Teilziele der heutigen Einheit:
1. **Zweispieler-Zuordnung:** Spiele sollen nicht nur dem Ersteller gehören, sondern auch dem beitretenden Spieler zugewiesen werden.
2. **Verbesserte Spielstatistiken:** Die API soll personalisierte Listen ausgeben, welche Spiele gewonnen und welche verloren wurden.
3. **Move-Historie:** Es soll nachträglich einsehbar sein, wer welchen Zug wann in welcher Reihenfolge gemacht hat.
4. **Sicherheit und Cheat-Protection:** Kein Spieler darf in einem Multiplayer-Match die Rolle oder Züge des anderen Spielers klauen.

## 3. Umsetzung und Gedanken hinter den Veränderungen

### 3.1. Zweispieler-Logging (`player2_id`)
**Problem:** Wenn ich in einem Browser das Spiel erstellte und im anderen Browser "O" spielte, erschien das Spiel beim zweiten Account nicht in der Liste *"Meine gespielten Spiele"*.
**Lösung:** Ich habe die Datenbank Tabelle `games` in `models.py` um eine optionale Spalte `player2_id` (ForeignKey auf `users.id`) erweitert. Wenn jetzt jemand (der nicht der Ersteller ist) in einem noch offenen Spiel einen Zug macht, wird seine User-ID automatisch als `player2_id` eingetragen. Das `GameResponse` Schema wurde entsprechend angepasst, um beide User-IDs in der API zurückzugeben.

### 3.2. Filtern nach Sieg, Niederlage & dynamische Nachrichten
**Idee:** Ich wollte Endpunkte für das Profil des Users haben, das Siege und Niederlagen trennt, und wollte, dass direkt in der API steht: *"Du hast gewonnen"* statt nur *"Spieler XY hat gewonnen"*.
**Lösung:** 
- Ich habe die neuen Routen `GET /games/me/won` und `GET /games/me/lost` erstellt.
- In `crud.py` wurde die Methode `get_user_games` eingeführt, die SQLAlchemy's `or_` Operator nutzt, um Spiele aus der DB zu fischen, in denen ich entweder Ersteller **oder** Zweitspieler bin.
- Eine Hilfsfunktion validiert jetzt beim Durchsuchen der Listen, wer gewonnen hat, gleicht dies mit der `current_user.id` ab und setzt die `game.message` entsprechend.

### 3.3. Implementierung der Move-Historie
**Problem:** Bei jedem `/move/` Aufruf wurde das Feld in der DB einfach als 9-Zeichen-String (z.B. "X.O......") überschrieben. Nach Spielende wusste niemand mehr, wie das Match verlaufen war.
**Lösung:**
Ich habe in der Datenbank die neue Tabelle `moves` (`id`, `game_id`, `user_id`, `position`, `symbol`, `created_at`) erstellt. Der Endpunkt zum Züge machen legt jetzt jedes Mal auch ein `Move`-Objekt an. Mit dem neuen Endpunkt `GET /games/{game_id}/moves` lässt sich das Match nun wie in einer Replay-Funktion auflisten.

### 3.4. Die Cheat-Protection
**Problem:** Mir ist aufgefallen, dass User B (Spieler "O") einfach im Endpunkt `?symbol=X` übergeben konnte. Wenn es der Turn für X war, hat das Backend den Zug für User B ausgeführt, weil er sich fälschlicherweise als "X" ausgab.
**Lösung:** 
Im `make_move_endpoint` steht jetzt harte Validierungs-Logik:
- Gehörst du als aktueller Webserver-User zu Symbol "X" oder "O"?
- Liefert dein Request das falsche Symbol ab? -> `HTTP 403: Du bist Spieler O!`.
- Versucht eine dritte Person (User C) einzusteigen, wenn der Raum schon einen `player2` hat? -> `HTTP 403: Du bist nicht Teil dieses Spiels!`.

## 4. Aktueller Commit
*(Link zum neuen Commit am Ende der Einheit einfügen)*

## 5. Diff
*(Diff oder Vergleich der Dateien vor/nach einfügen)*