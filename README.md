# TicTacToe Backend API

## Projektbeschreibung
Dieses Projekt beinhaltet das alleinige REST-API-Backend für eine Tic-Tac-Toe Web-Anwendung (z. B. ein React-basiertes Frontend). Es basiert auf FastAPI und ist für die Authentifizierung (JWT), Spielverwaltung und die gesamte serverseitige TicTacToe-Spiellogik verantwortlich. Die Daten werden relational mit SQLAlchemy in einer Datenbank gespeichert, und das Backend liefert diese synchron als Schnittstelle aus.

## Technologie-Stack
- **FastAPI**: Modernes und schnelles Web-Framework für Python.
- **Uvicorn**: ASGI Server zum Ausführen der FastAPI-Applikation.
- **SQLAlchemy**: ORM (Object Relational Mapper) für die Datenbankinteraktion.
- **SQLite**: Standard-Datenbank (konfigurierbar auf andere SQL-Datenbanken).
- **python-jose & passlib**: Für JWT-Authentifizierung und Passwort-Hashing.
- **pytest**: Für das Test-Framework (Unit-Testing der Spiellogik etc.).

---

## Startanleitung

Voraussetzung: Python 3.8 oder neuer ist installiert.

1. **Abhängigkeiten installieren:**
   Führe im Hauptverzeichnis (dort, wo die `requirements.txt` liegt) folgenden Befehl aus:
   ```bash
   pip install -r requirements.txt
   ```
2. **Server (Backend) starten:**
   Starte den Uvicorn Development-Server:
   ```bash
   uvicorn app.main:app --reload
   ```
   Die API ist nun unter `http://127.0.0.1:8000` erreichbar.
   *Tipp: Die automatisch generierte, interaktive Swagger-Dokumentation zum Testen der Endpunkte findest du unter: `http://127.0.0.1:8000/docs`*

---

## Konfigurationshinweise

### Environment-Variablen (.env)
Das Backend kann über eine optional anzulegende `.env`-Datei im Root-Verzeichnis (`app/config.py` lädt diese) konfiguriert werden. Falls keine angegeben sind, greifen sichere lokale Fallback-Werte.



### Ports & CORS (Schnittstelle zum Frontend)
- **Port:** Standardmäßig lauscht das FastAPI-Backend über Uvicorn auf **Port 8000** (`http://127.0.0.1:8000`).
- **CORS (Cross-Origin Resource Sharing):** Das Backend erlaubt standardmäßig HTTP-Anfragen von der Frontend-URL:
  - `http://localhost:5173` (Standard Vite / React 19 Umgebung)


Falls dein Frontend unter einer anderen Port-Adresse laufen sollte, musst du diesen Port in der Datei `app/main.py` im Attribut `allow_origins` der CORS-Middleware ergänzen.
