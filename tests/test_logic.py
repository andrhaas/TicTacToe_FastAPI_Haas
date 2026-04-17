import pytest
from app.game_logic import empty_board, board_from_string, board_to_string, check_winner, is_draw, get_current_player, make_move

def test_empty_board_length():
    assert len(empty_board()) == 9
    
def test_empty_board_content():
    assert empty_board() == '.........'
    
def test_board_from_string():
    assert board_from_string('X........')[0] == 'X'
    
def test_board_to_string():
    assert board_to_string(['X', '.', '.', '.', '.', '.', '.', '.', '.']) == 'X........'
    
def test_check_winner_row():
    assert check_winner(list('XXX......')) == 'X'
    
def test_check_winner_column():
    assert check_winner(list('O..O..O..')) == 'O'
    
def test_check_winner_none():
    assert check_winner(list('X.O......')) is None
    
def test_is_draw_false():
    assert is_draw(list('X........')) is False
    
def test_is_draw_true():
    assert is_draw(list('XOXOOXXXO')) is True
    
def test_get_current_player_start():
    assert get_current_player('.........') == 'X'


