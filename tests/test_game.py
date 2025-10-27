import pytest
from game import TicTacToe

def test_available_moves_and_empty_count():
    # Checks correct tracking of how many empty spaces we have and which squares are available to play
    g = TicTacToe(n=3)
    assert len(g.available_moves()) == 9
    assert g.num_empty_squares() == 9
    assert g.empty_squares() is True

    g.make_move(0, 'X')
    assert len(g.available_moves()) == 8
    assert g.num_empty_squares() == 8

def test_winner_rows_cols_diags():
    # Checks winning is detected correctly for 3x3 (by row, col, main diag, anti diag)
    
    # Row win
    g = TicTacToe(n=3)
    g.make_move(0, 'X'); g.make_move(1, 'X'); g.make_move(2, 'X')
    assert g.current_winner == 'X'

    # Column win
    g = TicTacToe(n=3)
    g.make_move(0, 'O'); g.make_move(3, 'O'); g.make_move(6, 'O')
    assert g.current_winner == 'O'

    # Main diagonal win
    g = TicTacToe(n=3)
    g.make_move(0, 'X'); g.make_move(4, 'X'); g.make_move(8, 'X')
    assert g.current_winner == 'X'

    # Anti-diagonal win
    g = TicTacToe(n=3)
    g.make_move(2, 'O'); g.make_move(4, 'O'); g.make_move(6, 'O')
    assert g.current_winner == 'O'

def test_no_false_positive_winner():
    # Checks correct enforcement of win condition
    g = TicTacToe(n=3)
    g.make_move(0, 'X'); g.make_move(1, 'X')
    assert g.current_winner is None

# We want to feed multiple board sizes and winning line locations into test functions so we do this to avoid unnecessary code duplication:
@pytest.mark.parametrize("n, line", [
    (4, [0,1,2,3]),            # Row
    (4, [0,4,8,12]),           # Column
    (4, [0,5,10,15]),          # Main diagonal
    (4, [3,6,9,12]),           # Anti diagonal
    (5, [5,6,7,8,9]),          # Row
    (5, [2,7,12,17,22]),       # Column
    (5, [0,6,12,18,24]),       # Main diagonal
    (5, [4,8,12,16,20]),       # Anti diagonal
])
def test_winner_various_sizes(n, line):
    # Checks win detection + game logic works for board size n
    g = TicTacToe(n=n)
    for idx in line:
        assert g.make_move(idx, 'X')
    assert g.current_winner == 'X'

def test_no_false_winner_on_mixed_line_larger():
    # Ensures no false wins on bigger boards by building a line with mixed X and O pieces
    g = TicTacToe(n=5)
    for idx, ch in zip([0,1,2,3], ['X','O','X','O']):
        g.make_move(idx, ch)
    assert g.current_winner is None

def test_moves_count_matches_empty_squares():
    # Checks that every move removes exactly one empty square and removes exactly one available move --> numbers must match
    g = TicTacToe(n=5)
    for index in [0, 6, 12, 18, 24]:
        g.make_move(index, 'X')
        assert len(g.available_moves()) == g.num_empty_squares()
