import math
import random
import time

class Player:
    def __init__(self, letter):
        self.letter = letter

    def get_move(self, game):
        pass


class HumanPlayer(Player):
    def __init__(self, letter):
        super().__init__(letter)

    def get_move(self, game):
        valid_square = False
        val = None
        while not valid_square:
            square = input(f"{self.letter}'s turn. Input move (0-{game.n*game.n - 1}): ")
            try:
                val = int(square)
                if val not in game.available_moves():
                    raise ValueError
                valid_square = True
            except ValueError:
                print('Invalid square. Try again.')
        return val


class RandomComputerPlayer(Player):
    def __init__(self, letter):
        super().__init__(letter)

    def get_move(self, game):
        square = random.choice(game.available_moves())
        return square


class SmartComputerPlayer(Player):
    """
    Minimax AI with alpha-beta pruning.
    Design choices:
      - Depth: perfect on 3x3, shallow on larger boards for tractable runtime
      - Soft time cap per move, stops search gracefully and returns best so far
      - Centre first move ordering to improve pruning efficiency
      - Lightweight heuristic on uncontested lines (fast, consistent)
      - Win/loss terminal scores scaled by remaining empties to prefer quicker wins / slower losses
    """
    def __init__(self, letter, max_depth=None, time_limit_ms=200):
        super().__init__(letter)
        self.call_count = 0 # Nodes visited in the current move
        self.call_counts = []  # History for benchmarkers
        self.move_times = [] # Per move elapsed time
        self.max_depth = max_depth
        self.time_limit_ms = time_limit_ms

    def get_move(self, game):
        self.call_count = 0

        moves = game.available_moves()
        start_time = time.perf_counter()
        stop_at = start_time + (self.time_limit_ms / 1000.0) if self.time_limit_ms else None

        if len(moves) == game.n * game.n:  # Opening bias - prefer around centre to reduce symmetry/branching early
            n = game.n
            if n % 2 == 1:
                centre = (n * n) // 2
                square = centre if centre in moves else random.choice(moves)
            else:
                a, b = n // 2 - 1, n // 2
                centres = [a*n + a, a*n + b, b*n + a, b*n + b]  # e.g. for 4x4 --> [5,6,9,10]
                candidates = [c for c in centres if c in moves]
                square = random.choice(candidates) if candidates else self._ordered_moves(game)[0]
            elapsed = 0.0
        else:
            # Auto depth policy - perfect on 3x3, otherwise shallow for speed
            depth = self.max_depth
            if depth is None:
                depth = None if game.n == 3 else 3  

            best = self.minimax(game, self.letter, -math.inf, math.inf, depth=depth, stop_at=stop_at)
            square = best['position']
            elapsed = time.perf_counter() - start_time

        self.call_counts.append(self.call_count)
        self.move_times.append(elapsed)
        #print(f"Minimax called {self.call_count} times for this move, time: {elapsed*1000:.2f} ms") --> uncomment to see metrics per move
        return square

    def _ordered_moves(self, game):
        # Centre first ordering (approximated by Manhattan distance to centre) to enhance pruning
        # Used because central moves tend to create/contest more lines. Exploring them first often tightens alpha/beta bounds earlier.
        n = game.n
        moves = set(game.available_moves())
        centre_r = (n - 1) / 2.0
        centre_c = (n - 1) / 2.0
        scored_moves = []
        for idx in moves:
            r, c = divmod(idx, n)
            manhattan_dist = abs(r - centre_r) + abs(c - centre_c)  # Manhattan distance to centre
            scored_moves.append((manhattan_dist, idx))
        scored_moves.sort()
        return [idx for _, idx in scored_moves]

    def _evaluate_position(self, state):
        """
        Heuristics:
        Idea - only reward lines (row/col/diag) that are uncontested by the opponent
          +count(my marks) if line has only me/empties
          -count(opp marks) if line has only opp/empties
        """
        me = self.letter
        opp = 'O' if me == 'X' else 'X'
        n = state.n
        b = state.board
        score = 0

        # Check rows
        for r in range(n):
            row = b[r*n:(r+1)*n]
            if opp not in row:
                score += row.count(me)
            if me not in row:
                score -= row.count(opp)

        # Check columns
        for c in range(n):
            col = [b[r*n + c] for r in range(n)]
            if opp not in col:
                score += col.count(me)
            if me not in col:
                score -= col.count(opp)

        # Check main diagonal
        d1 = [b[i*n + i] for i in range(n)]
        if opp not in d1:
            score += d1.count(me)
        if me not in d1:
            score -= d1.count(opp)

        # Check anti diagonal
        d2 = [b[i*n + (n-1-i)] for i in range(n)]
        if opp not in d2:
            score += d2.count(me)
        if me not in d2:
            score -= d2.count(opp)

        return score



    def minimax(self, state, player, alpha, beta, depth=None, stop_at=None):
        """
        Alpha-beta minimax with:
           - Terminal scoring scaled by remaining empties (prefer faster wins / delay losses)
           - Soft time cutoff (returns heuristic at current frontier)
           - Move ordering via _ordered_moves.
        """
        self.call_count += 1

        max_player = self.letter
        other_player = 'O' if player == 'X' else 'X'

        # Soft time cutoff - returns best estimate of the position so far using heuristics (keeps play responsive + avoids hanging)
        if stop_at is not None and time.perf_counter() >= stop_at:
            return {'position': None, 'score': self._evaluate_position(state)}

        # Terminal checks (win/draw)
        if state.current_winner == other_player:
            rem = state.num_empty_squares() + 1
            return {'position': None, 'score': (1 if other_player == max_player else -1) * rem} # Depth sensitive rewards - faster wins get higher scores
        if not state.empty_squares():
            return {'position': None, 'score': 0}

        # Heuristic cutoff at the depth limit
        if depth == 0:
            return {'position': None, 'score': self._evaluate_position(state)}

        moves = self._ordered_moves(state)

        if player == max_player: # If player is the maximising player
            best = {'position': None, 'score': -math.inf}
            for move in moves: # Make move --> recurse --> undo move, cheaper than copying state each node
                prev_winner = state.current_winner
                state.make_move(move, player)

                result = self.minimax(
                    state, other_player, alpha, beta,
                    None if depth is None else depth - 1, stop_at
                )

                
                state.board[move] = ' ' # Undoing mutation
                state.current_winner = prev_winner

                result['position'] = move
                if result['score'] > best['score']:
                    best = result
                # Alpha-beta pruning
                alpha = max(alpha, best['score'])
                if beta <= alpha:
                    break

                if stop_at is not None and time.perf_counter() >= stop_at: # Honour time budget even between siblings
                    break
            return best
        else: # Same but for minimising player
            best = {'position': None, 'score': math.inf}
            for move in moves:
                prev_winner = state.current_winner
                state.make_move(move, player)

                result = self.minimax(
                    state, other_player, alpha, beta,
                    None if depth is None else depth - 1, stop_at
                )

                state.board[move] = ' '
                state.current_winner = prev_winner

                result['position'] = move
                if result['score'] < best['score']:
                    best = result
                beta = min(beta, best['score'])
                if beta <= alpha:
                    break
                if stop_at is not None and time.perf_counter() >= stop_at:
                    break
            return best
