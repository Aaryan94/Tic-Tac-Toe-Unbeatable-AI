# Benchmark test for Smart vs Random across various board sizes, in order to evaluate effectiveness of AI at different board sizes

import random

from game import TicTacToe, play
from player import SmartComputerPlayer, RandomComputerPlayer

SIZES = [3, 4, 5, 6, 7, 8, 9, 10]   # Board sizes to test
GAMES = 50        # Games per size per role
DEPTH = None        # None = perfect on 3x3, depth 4 otherwise

def play_one(n, smart_as, depth): # Plays one full game of Smart vs Random
    g = TicTacToe(n=n)
    smart = SmartComputerPlayer(smart_as, max_depth=depth, time_limit_ms=0, print_minimax=False)
    rnd = RandomComputerPlayer('O' if smart_as == 'X' else 'X') # Role flipping allows us to test Smart as both first and second player
    x = smart if smart_as == 'X' else rnd
    o = rnd if smart_as == 'X' else smart
    return play(g, x, o, print_game=False)

def run_series(n, games, smart_as, depth): # Runs multiple Smart vs Random games and computes win/draw/loss rates --> we want accuracy
    wins = draws = losses = 0
    for _ in range(games):
        result = play_one(n, smart_as, depth)
        if result == smart_as:
            wins += 1
        elif result is None:
            draws += 1
        else:
            losses += 1

    winp  = wins / games
    drawp = draws / games
    lossp = losses / games
    return wins, draws, losses, winp, drawp, lossp

def depth_for(n): # Auto depth policy --> perfect search for 3x3 where game tree is solvable in time constraints, shallower for larger boards
    if DEPTH is not None:
        return DEPTH
    return None if n == 3 else 4

def main():
    random.seed(0) # random.seed ensures AI faces the same situations each run so that differences in performance actually come from algorithm changes and not luck

    print("Size | Depth  | Role  | Games  | Wins  | Draws  | Losses  |  Win %  |  Draw % |  Loss %")

    # For each board size we test Smart as both first player (X) and second player (O)
    for n in SIZES:
        d = depth_for(n)
        d_str = str(d if d is not None else "auto")
        for role in ('X', 'O'):
            wins, draws, losses, winp, drawp, lossp = run_series(n, GAMES, role, d)
            print(f"{n:<4} | {d_str:<6} | {role:^5} | {GAMES:>6} | {wins:>5} | {draws:>6} | {losses:>7} | {winp:>7.2%} | {drawp:>7.2%} | {lossp:>7.2%}")

if __name__ == "__main__":
    main()