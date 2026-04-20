from fastapi import FastAPI
from app.database import create_tables
from app.routers import auth
from app import games

app = FastAPI(
    title="TicTacToe API",
    description="",
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    """Create database tables on startup."""
    create_tables()


app.include_router(auth.router)
app.include_router(games.router)


@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "TicTacToe API is running"}
