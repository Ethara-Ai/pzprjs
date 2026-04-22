import random
import copy
from datetime import datetime, timezone


def _solve(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                for n in range(1, 10):
                    if _valid(board, r, c, n):
                        board[r][c] = n
                        if _solve(board):
                            return True
                        board[r][c] = 0
                return False
    return True


def _valid(board, row, col, num):
    if num in board[row]:
        return False
    if num in [board[r][col] for r in range(9)]:
        return False
    br, bc = 3 * (row // 3), 3 * (col // 3)
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == num:
                return False
    return True


def _generate_filled():
    board = [[0] * 9 for _ in range(9)]
    nums = list(range(1, 10))
    random.shuffle(nums)
    board[0] = nums
    _solve(board)
    return board


def _make_puzzle(solution, clue_count=22):
    puzzle = copy.deepcopy(solution)
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    removed = 0
    target = 81 - clue_count
    for r, c in cells:
        if removed >= target:
            break
        backup = puzzle[r][c]
        puzzle[r][c] = 0
        test = copy.deepcopy(puzzle)
        if _count_solutions(test, limit=2) == 1:
            removed += 1
        else:
            puzzle[r][c] = backup
    return puzzle


def _count_solutions(board, limit=2):
    count = [0]

    def backtrack():
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    for n in range(1, 10):
                        if _valid(board, r, c, n):
                            board[r][c] = n
                            backtrack()
                            board[r][c] = 0
                            if count[0] >= limit:
                                return
                    return
        count[0] += 1

    backtrack()
    return count[0]


def _encode_pzv(puzzle):
    flat = []
    for r in range(9):
        for c in range(9):
            flat.append(puzzle[r][c])

    encoded = ""
    gap = 0
    for v in flat:
        if v == 0:
            gap += 1
            if gap == 20:
                encoded += "z"
                gap = 0
        else:
            if gap > 0:
                encoded += _gap_char(gap)
                gap = 0
            encoded += format(v, 'x')
    if gap > 0:
        encoded += _gap_char(gap)
    return encoded


def _gap_char(count):
    # encodeNumber16: (15 + count) in base-36 → 'g'=1 empty, 'h'=2, ..., 'z'=20
    code = 15 + count
    return chr(ord('a') + code - 10) if code >= 10 else str(code)


def _build_moves(puzzle, solution):
    moves = []
    for r in range(9):
        for c in range(9):
            if puzzle[r][c] == 0:
                x = 1 + c * 2
                y = 1 + r * 2
                moves.append(f"mouse,left,{x},{y};key,{solution[r][c]}")
    return moves


def generate_custom_sudoku(clue_count=22):
    solution = _generate_filled()
    puzzle = _make_puzzle(solution, clue_count)

    pzv_encoded = _encode_pzv(puzzle)
    puzzle_url = f"http://pzv.jp/p.html?sudoku/9/9/{pzv_encoded}"
    puzzlink_url = f"http://puzz.link/p?sudoku/9/9/{pzv_encoded}"

    empty_cells = sum(1 for r in range(9) for c in range(9) if puzzle[r][c] == 0)
    moves = _build_moves(puzzle, solution)

    return {
        "puzzle_url": puzzle_url,
        "pid": "sudoku",
        "sort_key": None,
        "width": 9,
        "height": 9,
        "area": 81,
        "number_required_moves": empty_cells,
        "number_total_solution_moves": empty_cells,
        "puzzlink_url": puzzlink_url,
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
            "published_at": datetime.now(timezone.utc).isoformat()
        },
        "metadata": {
            "has_structured_solution": True,
            "cspuz_is_unique": True,
            "db_w": 9,
            "db_h": 9
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "solution": {
            "moves_full": moves,
            "moves_required": moves,
            "moves_hint": []
        }
    }


if __name__ == "__main__":
    import json
    puzzle_data = generate_custom_sudoku(clue_count=22)
    print(json.dumps(puzzle_data, indent=2, default=str))
    print(f"\nPlay it: {puzzle_data['puzzlink_url']}")
