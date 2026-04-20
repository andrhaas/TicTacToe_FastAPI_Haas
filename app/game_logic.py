

import random

# Alle Gewinn-Kombinationen 
WIN_COMBINATIONS = [
    [0, 1, 2],  # Zeile 1
    [3, 4, 5],  # Zeile 2
    [6, 7, 8],  # Zeile 3
    [0, 3, 6],  # Spalte 1
    [1, 4, 7],  # Spalte 2
    [2, 5, 8],  # Spalte 3
    [0, 4, 8],  # Diagonale
    [2, 4, 6],  # Diagonale
]


def board_from_string(board_str: str) -> list[str]:
    """Konvertiert den gespeicherten Board-String (z.B. 'X.O.X....') in eine Liste."""
    return list(board_str)


def board_to_string(board: list[str]) -> str:
    """Konvertiert die Board-Liste zurück in einen String."""
    return "".join(board)


def empty_board() -> str:
    """Gibt ein leeres 3x3-Board als String zurück."""
    return "." * 9


def check_winner(board: list[str]) -> str | None:
    """
    Prüft ob 'X' oder 'O' gewonnen hat.
    Gibt 'X', 'O' oder None zurück.
    """
    for combo in WIN_COMBINATIONS:
        a, b, c = combo
        if board[a] != "." and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_draw(board: list[str]) -> bool:
    """Gibt True zurück wenn das Board voll ist und kein Gewinner existiert."""
    return "." not in board and check_winner(board) is None


def make_move(board_str: str, position: int, symbol: str) -> tuple[str, str | None, bool]:
    """
    Führt einen Zug aus.

    Args:
        board_str: Aktueller Board-String
        position:  Position 1–9
        symbol:    'X' oder 'O'

    Returns:
        (neuer_board_string, gewinner_oder_None, unentschieden)

    Raises:
        ValueError: Bei ungültigem Zug
    """
    if position < 1 or position > 9:
        raise ValueError("Position muss zwischen 1 und 9 liegen.")

    board = board_from_string(board_str)
    index = position - 1

    if board[index] != ".":
        raise ValueError(f"Position {position} ist bereits belegt.")

    board[index] = symbol
    new_board_str = board_to_string(board)

    winner = check_winner(board)
    draw = is_draw(board)

    return new_board_str, winner, draw


def get_current_player(board_str: str) -> str:
    """
    Bestimmt wer als nächstes dran ist.
    X beginnt immer. Bei gleich vielen X und O ist X dran.
    """
    x_count = board_str.count("X")
    o_count = board_str.count("O")
    return "X" if x_count <= o_count else "O"


