import time
import pytest
from game import TicTacToe, play
from player import SmartComputerPlayer

def build_state(n, marks):
    # Builds a board size nxn that contains the marks. Marks are given in form [(index, char), (index2, char2)].
    g = TicTacToe(n=n)
    for idx, ch in marks:
        g.board[idx] = ch
    g.current_winner = None  # Ensures winner will be recomputed by any make_move (winner to be checked on next move)
    return g

def test_ai_plays_centre_on_opening_odd_board():
    # Ensures on an odd empty board that AI picks the centre as the best first move
    g = TicTacToe(n=3)
    ai = SmartComputerPlayer('X', max_depth=None, time_limit_ms=0)
    move = ai.get_move(g)
    assert move == 4  # Check it == centre

def test_ai_prefers_centreish_on_even_board():
    # Checks the opening strategy works when we have an even board as no specific centre (meant to choose 1 of 4 middle squares)
    g = TicTacToe(n=4)
    ai = SmartComputerPlayer('X', max_depth=None, time_limit_ms=0)
    move = ai.get_move(g)
    mids = (g.n//2 - 1, g.n//2)
    centres = {mids[0]*g.n + mids[0], mids[0]*g.n + mids[1],
               mids[1]*g.n + mids[0], mids[1]*g.n + mids[1]}
    assert move in centres

def test_ai_blocks_immediate_threat():
    # If the opponent is about to win the next turn, the AI must block the win
    g = build_state(3, [(1,'O'), (2,'O'), (4,'X')])
    ai = SmartComputerPlayer('X', max_depth=None, time_limit_ms=0)
    move = ai.get_move(g)
    assert move == 0  # block

def test_ai_takes_immediate_win():
    # If the AI has an immediate move it can take to win, it must take it
    g = build_state(3, [(0,'X'), (4,'X'), (1,'O')])
    ai = SmartComputerPlayer('X', max_depth=None, time_limit_ms=0)
    move = ai.get_move(g)
    assert move == 8

def test_time_cap_returns_legal_move():
    # On a larger board with a tiny time cap, ensure we still return a legal move --> checking time working + resilience under low time
    g = build_state(5, [(0,'X'), (6,'O'), (12,'X'), (18,'O')]) # Tested on state that isn't empty as we want it to enter minimax, not just return centre (as it would on first move)
    ai = SmartComputerPlayer('X', max_depth=6, time_limit_ms=5)
    move = ai.get_move(g)
    assert move in g.available_moves()

def test_time_cap_respected_within_slack():
    # Checks AI runs close to the time limit and doesn't blow past it. Doesn't need to be exact just doesn't need to go high past it.
    g = build_state(7, [(0,'X'), (24,'O'), (10,'X'), (38,'O')])
    time_cap_ms = 10
    ai = SmartComputerPlayer('X', max_depth=6, time_limit_ms=time_cap_ms)
    start_time = time.perf_counter()
    move = ai.get_move(g)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    assert move in g.available_moves()
    assert elapsed_ms <= time_cap_ms * 10

def test_self_play_no_immediate_loss_3x3():
    # Checks that two smart players on 3x3 should not lose immediately --> stability check in early game
    g = TicTacToe(n=3)
    x = SmartComputerPlayer('X', max_depth=None, time_limit_ms=0)
    o = SmartComputerPlayer('O', max_depth=None, time_limit_ms=0)

    for _ in range(3):   # Simulate first 3 moves per side (opening phase)
        mvx = x.get_move(g)
        assert mvx in g.available_moves()
        g.make_move(mvx, 'X')
        if g.current_winner: break

        mvo = o.get_move(g)
        assert mvo in g.available_moves()
        g.make_move(mvo, 'O')
        if g.current_winner: break

    assert g.current_winner in (None, 'X', 'O')  # Checks no crash

def test_perfect_self_play_draw_3x3():
    # Checks that two smart players always draw, so AI is optimal on 3x3
    g = TicTacToe(n=3)
    x = SmartComputerPlayer('X', max_depth=None, time_limit_ms=0)
    o = SmartComputerPlayer('O', max_depth=None, time_limit_ms=0)
    result = play(g, x, o, print_game=False)
    assert result is None  # Tie with perfect play

def test_eval_prefers_uncontested_lines_for_self():
    # Checking that heuristics score boards higher when they contain (X's here) marks in lines uncontested by opponent
    ai = SmartComputerPlayer('X', max_depth=None, time_limit_ms=0)

    # Board A --> X has two in a row on top, O is elsewhere
    game_a = build_state(3, [(0,'X'), (1,'X'), (4,'O')])
    score_a = ai._evaluate_position(game_a)

    # Board B --> O has two in a row on top, X is elsewhere
    game_b = build_state(3, [(0,'O'), (1,'O'), (4,'X')])
    score_b = ai._evaluate_position(game_b)

    assert score_a > score_b  # X favoring position should score higher for X

def test_eval_blocks_are_better_than_letting_opp_threaten():
    # Check that blocking a threat improves and does not hurt the heuristic score
    # Score after blocking should be >= Score of leaving threat open
    ai = SmartComputerPlayer('X', max_depth=None, time_limit_ms=0)

    # Threat --> O is at 1 and 2, X is in the centre, Position 0 is the block
    g_threat = build_state(3, [(1,'O'), (2,'O'), (4,'X')])
    score_open = ai._evaluate_position(g_threat)

    # After X blocks at 0, heuristic should be better or equal.
    g_block = build_state(3, [(0,'X'), (1,'O'), (2,'O'), (4,'X')])
    score_block = ai._evaluate_position(g_block)

    assert score_block >= score_open
