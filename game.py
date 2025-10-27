import time
from player import HumanPlayer, RandomComputerPlayer, SmartComputerPlayer


class TicTacToe:
    """
    Design choices:
      - Flat list board (size n*n) for simple O(1) indexing and slicing.
      - Track current_winner so we don't recompute wins after the fact.
      - Win check inspects only the last move's row/col/diagonals (O(n)), not the whole board.
    """
    def __init__(self, n=3):
        self.n = n
        self.board = [' ' for _ in range(n * n)] # Flat board: cheaper than 2D list for small n
        self.current_winner = None # Set once on winning move

    def print_board(self):
        # Simple text UI kept separate from state/logic
        number_board = [[str(i) for i in range(r*self.n, (r+1)*self.n)] for r in range(self.n)]
        for r in range(self.n):
            row = self.board[r*self.n:(r+1)*self.n]
            num_row = number_board[r]
            print('| ' + ' | '.join(row) + ' |    ' + '| ' + ' | '.join(num_row) + ' |')
            
    def print_board_indices(self):
        # Human indexing helper
        number_board = [[str(i) for i in range(r*self.n, (r+1)*self.n)] for r in range(self.n)]
        for row in number_board:
            print('| ' + ' | '.join(row) + ' |')

    def make_move(self, square, letter):
        if self.board[square] == ' ': # Only allow writing to empty squares
            self.board[square] = letter
            if self.winner(square, letter): # Only check lines affected by this move
                self.current_winner = letter
            return True
        return False

    def winner(self, square, letter):
        # Check only lines that could have changed due to square (row/col/diagonals)
        r = square // self.n
        c = square % self.n

        # Row check
        row = self.board[r*self.n:(r+1)*self.n]
        if all(s == letter for s in row):
            return True

        # Column check
        column = [self.board[c + i*self.n] for i in range(self.n)]
        if all(s == letter for s in column):
            return True

        # Main diagonal check
        if r == c:
            diag1 = [self.board[i*self.n + i] for i in range(self.n)]
            if all(s == letter for s in diag1):
                return True

        # Anti-diagonal check
        if r + c == self.n - 1:
            diag2 = [self.board[i*self.n + (self.n - 1 - i)] for i in range(self.n)]
            if all(s == letter for s in diag2):
                return True

        return False

    def empty_squares(self): # Fast check used by the main loop/AI to terminate search early
        return ' ' in self.board 

    def num_empty_squares(self): # Useful for scoring (when calculating depth sensitive win values in minimax)
        return self.board.count(' ')

    def available_moves(self): # Quickly gets all possible moves
        return [i for i, x in enumerate(self.board) if x == ' '] 


def play(game, x_player, o_player, print_game=True): # Game loop
    if print_game:
        print(f"{game.n}x{game.n} board. Need {game.n} in a row to win.")
        game.print_board_indices()

    letter = 'X' # X always goes first
    while game.empty_squares():
        if letter == 'O': # Get the next player's move
            square = o_player.get_move(game)
        else:
            square = x_player.get_move(game)

        if game.make_move(square, letter):
            if print_game:
                print(letter + f' makes a move to square {square}')
                game.print_board()
                print('')

            if game.current_winner:
                if print_game:
                    print(letter + ' wins!')
                return letter

            letter = 'O' if letter == 'X' else 'X' # Toggles to next player's turn
        
        if print_game: # This allows pacing of board prints/turns, disabled when testing/benchmarking
            time.sleep(0.5)

    if print_game:
        print("It's a tie!")
    return None

def choose_player(letter):
    while True:
        choice = input(f"{letter} player [h = Human, r = Random, s = Smart]: ").strip().lower()
        if choice in ('h', 'r', 's'):
            break
        print("Invalid choice. Enter h, r, or s.")

    if choice == 'r':
        return RandomComputerPlayer(letter)

    if choice == 's':
        while True:
            depth_input = input(" max_depth (Enter = auto): ").strip()
            if depth_input == "":
                max_depth = None
                break
            try:
                max_depth = int(depth_input)
                if max_depth < 0:
                    print("max_depth must be >= 0.")
                    continue
                break
            except ValueError:
                print("Enter a non-negative integer.")

        while True:
            time_input = input(" time_limit_ms (Enter = 200): ").strip()
            if time_input == "":
                time_limit_ms = None
                break
            try:
                time_limit_ms = int(time_input)
                if time_limit_ms <= 0:
                    print("time_limit_ms must be > 0.")
                    continue
                break
            except ValueError:
                print("Enter a positive integer.")

        args = {}
        if max_depth is not None: args['max_depth'] = max_depth
        if time_limit_ms is not None: args['time_limit_ms'] = time_limit_ms

        return SmartComputerPlayer(letter, **args)
        
    return HumanPlayer(letter)

if __name__ == '__main__':
    while True:
        size_input = input("Enter board size (e.g: 3 for 3x3): ")
        try:
            size = int(size_input)
            if size <= 0:
                print("Board size must be a positive integer. Try again.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a positive integer.")

    game = TicTacToe(n=size)

    print("\nChoose player types:")
    x_player = choose_player('X')
    o_player = choose_player('O')

    play(game, x_player, o_player, print_game=True)