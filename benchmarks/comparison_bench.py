# Benchmark test to compare speeds/stats of:
#   - Normal Minimax, with no alpha beta pruning or move ordering
#   - Minimax + alpha beta pruning without move ordering
#   - Minimax + alpha beta pruning + move ordering
# Done to compare efficiencies and show impact of optimisations on nodes searched and speed of algorithms

import time
from statistics import mean
import random

from game import TicTacToe
from player import SmartComputerPlayer

# Implemented some functions so that we can toggle on/off specific optimisations without modifying Smart AI code
def _no_order_moves(self, game): # Disables the AI's move ordering feature so AI explores moves in plain index order
    return list(game.available_moves()) # Returns unsorted moves

def _minimax_no_alpha_beta(self, state, player, alpha, beta, depth=None, stop_at=None):
    # Same minimax function but without using alpha-beta pruning
    self.call_count += 1
    max_player = self.letter
    other_player = 'O' if player == 'X' else 'X'

    if stop_at is not None and time.perf_counter() >= stop_at:
        return {'position': None, 'score': self._evaluate_position(state)}

    if state.current_winner == other_player:
        rem = state.num_empty_squares() + 1
        return {'position': None, 'score': (1 if other_player == max_player else -1) * rem}
    if not state.empty_squares():
        return {'position': None, 'score': 0}

    if depth == 0:
        return {'position': None, 'score': self._evaluate_position(state)}

    moves = self._ordered_moves(state)

    if player == max_player: # Same logic as normal minimax but without any alpha beta pruning implemented
        best = {'position': None, 'score': float('-inf')}
        for move in moves:
            prev_winner = state.current_winner
            state.make_move(move, player)
            res = _minimax_no_alpha_beta(
                self, state, other_player, alpha, beta,
                None if depth is None else depth - 1, stop_at
            )
            
            state.board[move] = ' '
            state.current_winner = prev_winner

            res['position'] = move
            if res['score'] > best['score']:
                best = res
        return best
    else:
        best = {'position': None, 'score': float('inf')}
        for move in moves:
            prev_winner = state.current_winner
            state.make_move(move, player)
            res = _minimax_no_alpha_beta(
                self, state, other_player, alpha, beta,
                None if depth is None else depth - 1, stop_at
            )
            
            state.board[move] = ' '
            state.current_winner = prev_winner

            res['position'] = move
            if res['score'] < best['score']:
                best = res
        return best

def to_index(n, r, c): # This converts a row/column into the flat board index --> it is a helper function
    return r * n + c

def generate_test_positions(n): # Helper
    # This creates a list of example mid game starting boards so that we can test the algorithms in difference scenarios for fairness + to make differences in pruning and ordering more obvious
    start_position = [] # Our list of different board states
    if n % 2 == 1: # Odd board has one true centre
        m = n // 2
        centre = to_index(n, m, m)
        start_position += [
            [(centre, 'O')], # O in centre
            [(centre, 'X')], # X in centre
            [(centre, 'O'), (to_index(n, 0, 0), 'X')], # Adding corner variations
            [(centre, 'X'), (to_index(n, 0, n-1), 'O')],
            [(to_index(n, 0, 0), 'X'), (to_index(n, n-1, n-1), 'O')],
            [(to_index(n, 0, 0), 'X'), (to_index(n, m, m-1), 'O')],
        ]
    else: # Even board has 4 middle squares
        a, b = n//2 - 1, n//2
        centres = [to_index(n, a, a), to_index(n, a, b), to_index(n, b, a), to_index(n, b, b)]
        start_position += [
            [(centres[0], 'O')],
            [(centres[1], 'X')],
            [(centres[0], 'X'), (centres[3], 'O')],
            [(to_index(n, 0, 0), 'X'), (centres[2], 'O')],
            [(to_index(n, 0, 0), 'X'), (to_index(n, n-1, n-1), 'O')],
            [(to_index(n, 0, 0), 'O'), (to_index(n, 0, n-2), 'X')],
        ]
    return start_position

def benchmark_one_move(n, depth, time_ms, mode="PRUNE_ON", start_pos=None): 
    # Performs only one minimax decision (a move), and returns node count and time elapsed for this run
    # We can turn pruning on/off and ordering on/off here
    
    g = TicTacToe(n=n)

    if start_pos: # Applying a preset board state to simulate a realistic test
        for sq, ch in start_pos:
            g.make_move(sq, ch)

    ai = SmartComputerPlayer('X', max_depth=depth, time_limit_ms=time_ms) # Player to benchmark

    # Toggling pruning and ordering
    restore = {}
    if mode == "PRUNE_OFF":
        restore['minimax'] = ai.minimax # Save real minimax into dictionary
        ai.minimax = _minimax_no_alpha_beta.__get__(ai, type(ai)) # Replaces ai.minimax function with the no pruning version
    elif mode == "ORDER_OFF":
        restore['_ordered_moves'] = ai._ordered_moves
        ai._ordered_moves = _no_order_moves.__get__(ai, type(ai))

    ai.get_move(g)  # SmartComputer picks a move, benchmark happens here

    for name, fn in restore.items(): # Restoring original methods
        setattr(ai, name, fn)

    nodes = ai.call_count
    elapsed_ms = ai.move_times[-1] * 1000.0
    return nodes, elapsed_ms

def run_bench(): # Loops through sizes and modes and prints benchmark results
    random.seed(0) # random.seed ensures AI faces the same situations each run so that differences in performance actually come from algorithm changes and not luck
    configs = [
        # (board size, search depth, time limit, repetitions per position)
        (3, None, 1000, 5),
        (4, 4, 1000, 5),
        (5, 4, 1000, 5),
        (6, 4, 1000, 5),
        (7, 4, 1000, 5),
        (8, 4, 1000, 5),
        (9, 4, 1000, 5),
        (10, 4, 1000, 5),
    ]

    modes = ["PRUNE_ON", "ORDER_OFF", "PRUNE_OFF"]
  
    print("Board | Depth | Time(ms) | Mode       | avg_nodes |  avg_ms | nodes/sec")

    for n, depth, time_ms, repeats in configs:
        positions = generate_test_positions(n)

        for mode in modes:
            all_nodes, all_ms = [], []

            for start_position in positions:
                for _ in range(repeats):
                    nodes, ms = benchmark_one_move(n, depth, time_ms, mode=mode, start_pos=start_position)
                    all_nodes.append(nodes)
                    all_ms.append(ms)

            avg_nodes = int(mean(all_nodes)) if all_nodes else 0 # Aggregating perfomance
            avg_ms = mean(all_ms) if all_ms else 0.0
            nps = (avg_nodes / (avg_ms / 1000.0)) if avg_ms > 0 else 0.0

            print(f"{n}x{n}   | {depth if depth is not None else 'auto':>5} | {time_ms:>8} | {mode:10} "
                  f"| {avg_nodes:>9} | {avg_ms:7.2f} | {nps:9.0f}")
        print()

if __name__ == "__main__":
    run_bench()
