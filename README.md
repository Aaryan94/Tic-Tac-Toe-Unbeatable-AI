# Tic-Tac-Toe Unbeatable AI (Minimax + Alpha-Beta Pruning)

A fast and smart Tic-Tac-Toe engine that scales to n x n boards.

Includes:
- Alpha-beta-pruned Minimax AI
- Move ordering optimization (center-first)
- Soft time caps per move for large boards
- O(n) win checking
- Full test suite using pytest
- Benchmarks to analyze AI performance

How to run:
- To run main game: python3 game.py
- To run optimisation comparison benchmark: python3 -m benchmarks.comparison_bench
- To run effectiveness benchmark: python3 -m benchmarks.run_match_bench
- To run tests, install pytest and run: 
    python3 -m pip install --upgrade pip
    pip install pytest
    python3 -m pytest -q

What I built:
- Minimax AI with Alpha-Beta Pruning.
- Heuristics to evaluate positions when full search is too expensive.
    - Rewards lines where the opponent has no presence.
    - Penalises leaving immediate threats.
    - Prefers faster wins / delayed losses.
- Move ordering (centre first) to significantly improve pruning.
- Time limits for scalable play on 4x4, 5x5, etc.
- O(n) win detection by checking only the row/column/diagonals affected by the last move
- Comprehensive tests (pytest): correctness on rows/cols/diagonals, multiple board sizes, no false positives, AI opening choices, blocking/taking wins, heuristic sanity checks and perfect-play draw on 3×3.
- Benchmarks:
    - Search performance comparison between pruning on/off and move-ordering on/off (nodes visited, ms, nodes/sec).
    - Match series (Smart vs Random) across board sizes and roles to measure win/draw/loss rates for different board sizes.
Together these allow:
- Perfect play on 3x3.
- Strong play and quick performance on bigger boards

Project Structure:
- game.py
- player.py
- tests/
    - test_game.py
    - test_search.py
- benchmarks/
    - comparison_bench.py
    - run_match.py
- README.md