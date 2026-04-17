from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    games = relationship("Game", back_populates="owner")


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    board = Column(String(9), default=".........", nullable=False)
    current_player = Column(String(1), default="X", nullable=False)
    player_symbol = Column(String(1), default="X", nullable=False)

    status = Column(String(10), default="ongoing", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="games")

    @property
    def formatted_board(self) -> list[str]:
        b = self.board.replace('.', ' ')
        return [
            f" {b[0]} | {b[1]} | {b[2]} ",
            "-----------",
            f" {b[3]} | {b[4]} | {b[5]} ",
            "-----------",
            f" {b[6]} | {b[7]} | {b[8]} "
        ]

