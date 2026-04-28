"""
Hitori puzzle — rule-based validation (no hardcoded solution).

Rules:
  1. Shade cells so no number appears more than once in any row/column
     (among unshaded cells).
  2. Shaded cells cannot be adjacent horizontally or vertically.
  3. All unshaded cells must form a single connected group.

Extra rules (medium/hard):
  4. Diagonal ban — shaded cells cannot touch diagonally (king-move).
  5. Checkerboard parity — shading only on cells where (row + col) is even.
  6. Max 2 shaded per row/column.

Interface: init_game, make_move, undo_move, check_solution, get_hint
"""

# ── Grids per difficulty ──

_GRIDS = {
    "easy": {
        "rows": 5,
        "cols": 5,
        "grid": [
            [1, 2, 3, 2, 5],
            [3, 1, 2, 5, 4],
            [2, 3, 5, 4, 1],
            [5, 4, 1, 3, 2],
            [4, 5, 4, 1, 3],
        ],
        "extra_rules": [],  # Only core rules 1-3
    },
    "medium": {
        "rows": 6,
        "cols": 6,
        "grid": [
            [2, 4, 5, 2, 1, 3],
            [4, 5, 2, 1, 3, 6],
            [5, 2, 3, 3, 2, 4],
            [2, 1, 3, 6, 4, 5],
            [1, 3, 6, 4, 5, 2],
            [3, 6, 4, 4, 2, 1],
        ],
        "extra_rules": ["diagonal_ban", "checkerboard_parity", "max_2_per_line"],
    },
    "hard": {
        "rows": 8,
        "cols": 8,
        "grid": [
            [1, 5, 8, 3, 2, 6, 4, 7],
            [5, 4, 3, 2, 6, 4, 7, 5],
            [8, 3, 2, 6, 7, 7, 1, 5],
            [3, 2, 6, 4, 7, 1, 5, 8],
            [2, 6, 4, 7, 1, 5, 7, 3],
            [6, 4, 7, 1, 5, 8, 3, 2],
            [7, 7, 3, 5, 8, 3, 2, 6],
            [7, 1, 5, 8, 3, 2, 6, 4],
        ],
        "extra_rules": ["diagonal_ban", "checkerboard_parity", "max_2_per_line"],
    },
}

# ── Active puzzle state (set by init_game) ──
_ROWS = 6
_COLS = 6
_GRID = _GRIDS["medium"]["grid"]
_active_extra_rules = _GRIDS["medium"]["extra_rules"]
_history = []


# ── Rule checks (all operate on the board: 0=unshaded, 1=shaded) ──

def _check_no_duplicate_unshaded(board):
    """No duplicate numbers among unshaded cells in any row/column."""
    errors = []
    for r in range(_ROWS):
        seen = {}
        for c in range(_COLS):
            if board[r][c] == 0:
                num = _GRID[r][c]
                if num in seen:
                    errors.append({"row": r, "col": c, "message": f"Duplicate {num} in row {r+1}"})
                    errors.append({"row": r, "col": seen[num], "message": f"Duplicate {num} in row {r+1}"})
                else:
                    seen[num] = c
    for c in range(_COLS):
        seen = {}
        for r in range(_ROWS):
            if board[r][c] == 0:
                num = _GRID[r][c]
                if num in seen:
                    errors.append({"row": r, "col": c, "message": f"Duplicate {num} in col {c+1}"})
                    errors.append({"row": seen[num], "col": c, "message": f"Duplicate {num} in col {c+1}"})
                else:
                    seen[num] = r
    return errors


def _check_no_adjacent_shaded(board):
    """Shaded cells cannot be horizontally or vertically adjacent."""
    errors = []
    for r in range(_ROWS):
        for c in range(_COLS):
            if board[r][c] == 1:
                if c + 1 < _COLS and board[r][c + 1] == 1:
                    errors.append({"row": r, "col": c, "message": "Adjacent shaded cells"})
                    errors.append({"row": r, "col": c + 1, "message": "Adjacent shaded cells"})
                if r + 1 < _ROWS and board[r + 1][c] == 1:
                    errors.append({"row": r, "col": c, "message": "Adjacent shaded cells"})
                    errors.append({"row": r + 1, "col": c, "message": "Adjacent shaded cells"})
    return errors


def _check_unshaded_connected(board):
    """All unshaded cells must form a single connected group."""
    start = None
    unshaded_count = 0
    for r in range(_ROWS):
        for c in range(_COLS):
            if board[r][c] == 0:
                unshaded_count += 1
                if start is None:
                    start = (r, c)

    if start is None or unshaded_count == 0:
        return [{"row": 0, "col": 0, "message": "No unshaded cells"}]

    visited = set()
    queue = [start]
    visited.add(start)
    while queue:
        r, c = queue.pop(0)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < _ROWS and 0 <= nc < _COLS and (nr, nc) not in visited and board[nr][nc] == 0:
                visited.add((nr, nc))
                queue.append((nr, nc))

    if len(visited) < unshaded_count:
        errors = []
        for r in range(_ROWS):
            for c in range(_COLS):
                if board[r][c] == 0 and (r, c) not in visited:
                    errors.append({"row": r, "col": c, "message": "Disconnected unshaded cell"})
        return errors
    return []


def _check_diagonal_ban(board):
    """Shaded cells cannot touch diagonally (king-move exclusion)."""
    errors = []
    for r in range(_ROWS):
        for c in range(_COLS):
            if board[r][c] == 1:
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < _ROWS and 0 <= nc < _COLS and board[nr][nc] == 1:
                        errors.append({"row": r, "col": c, "message": "Diagonally adjacent shaded cells"})
                        break
    return errors


def _check_checkerboard_parity(board):
    """Shading only allowed on cells where (row + col) is even."""
    errors = []
    for r in range(_ROWS):
        for c in range(_COLS):
            if board[r][c] == 1 and (r + c) % 2 != 0:
                errors.append({"row": r, "col": c, "message": "Shading not allowed here (parity)"})
    return errors


def _check_max_2_per_line(board):
    """Max 2 shaded cells per row and per column."""
    errors = []
    for r in range(_ROWS):
        shaded_cols = [c for c in range(_COLS) if board[r][c] == 1]
        if len(shaded_cols) > 2:
            for c in shaded_cols:
                errors.append({"row": r, "col": c, "message": f"More than 2 shaded in row {r+1}"})
    for c in range(_COLS):
        shaded_rows = [r for r in range(_ROWS) if board[r][c] == 1]
        if len(shaded_rows) > 2:
            for r in shaded_rows:
                errors.append({"row": r, "col": c, "message": f"More than 2 shaded in col {c+1}"})
    return errors


def _get_all_errors(board):
    """Run all rule checks, return deduplicated errors."""
    all_errs = []
    all_errs.extend(_check_no_duplicate_unshaded(board))
    all_errs.extend(_check_no_adjacent_shaded(board))
    all_errs.extend(_check_unshaded_connected(board))
    if "diagonal_ban" in _active_extra_rules:
        all_errs.extend(_check_diagonal_ban(board))
    if "checkerboard_parity" in _active_extra_rules:
        all_errs.extend(_check_checkerboard_parity(board))
    if "max_2_per_line" in _active_extra_rules:
        all_errs.extend(_check_max_2_per_line(board))
    seen = set()
    unique = []
    for e in all_errs:
        key = (e["row"], e["col"])
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique


def _has_any_shading(board):
    """Check if player has placed at least one shading."""
    return any(board[r][c] == 1 for r in range(_ROWS) for c in range(_COLS))


def _board_is_solved(board):
    """A board is solved when all rules pass and at least one cell is shaded."""
    if not _has_any_shading(board):
        return False
    return len(_get_all_errors(board)) == 0


# ── Game interface ──

def init_game(metadata):
    """Initialize board for the selected difficulty."""
    global _ROWS, _COLS, _GRID, _active_extra_rules

    difficulty = (metadata.get("difficulty", "medium") if hasattr(metadata, 'get')
                  else metadata.get("difficulty", "medium")).lower()
    if difficulty not in _GRIDS:
        difficulty = "medium"

    config = _GRIDS[difficulty]
    _ROWS = config["rows"]
    _COLS = config["cols"]
    _GRID = config["grid"]
    _active_extra_rules = config["extra_rules"]

    board = [[0] * _COLS for _ in range(_ROWS)]
    labels = [row[:] for row in _GRID]
    given_mask = [[False] * _COLS for _ in range(_ROWS)]
    _history.clear()
    return {
        "board": board,
        "labels": labels,
        "given_mask": given_mask,
        "status": "ready",
    }


def make_move(state, row, col, value):
    """Toggle shading on a cell. value: 1=shaded, 0=unshaded."""
    board = state["board"]
    old_value = board[row][col]
    _history.append({"row": row, "col": col, "old_value": old_value})
    board[row][col] = value

    conflicts = []

    if value == 1:
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < _ROWS and 0 <= nc < _COLS and board[nr][nc] == 1:
                conflicts.append({"row": nr, "col": nc})

        if "diagonal_ban" in _active_extra_rules:
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < _ROWS and 0 <= nc < _COLS and board[nr][nc] == 1:
                    conflicts.append({"row": nr, "col": nc})

        if "checkerboard_parity" in _active_extra_rules and (row + col) % 2 != 0:
            conflicts.append({"row": row, "col": col})

        if "max_2_per_line" in _active_extra_rules:
            row_shaded = sum(1 for c in range(_COLS) if board[row][c] == 1)
            if row_shaded > 2:
                conflicts.append({"row": row, "col": col})

            col_shaded = sum(1 for r in range(_ROWS) if board[r][col] == 1)
            if col_shaded > 2:
                conflicts.append({"row": row, "col": col})

    if conflicts:
        conflicts.append({"row": row, "col": col})

    seen = set()
    unique_conflicts = []
    for c in conflicts:
        key = (c["row"], c["col"])
        if key not in seen:
            seen.add(key)
            unique_conflicts.append(c)

    msg = ""
    if unique_conflicts:
        msg = "Rule violation detected!"

    complete = _board_is_solved(board)
    if complete:
        msg = "Congratulations! Puzzle solved!"

    return {
        "state": state,
        "valid": len(unique_conflicts) == 0,
        "conflicts": unique_conflicts,
        "message": msg,
        "complete": complete,
    }


def undo_move(state):
    """Undo the last move."""
    if not _history:
        return state
    move = _history.pop()
    state["board"][move["row"]][move["col"]] = move["old_value"]
    return state


def check_solution(state):
    """Full rule check — returns all errors."""
    board = state["board"]

    if not _has_any_shading(board):
        return {
            "solved": False,
            "errors": [],
            "message": "No cells shaded yet. Shade cells to eliminate duplicates.",
        }

    errors = _get_all_errors(board)
    solved = len(errors) == 0

    if solved:
        return {
            "solved": True,
            "errors": [],
            "message": "Puzzle solved! All rules satisfied.",
        }

    return {
        "solved": False,
        "errors": errors,
        "message": f"{len(errors)} rule violation(s) found.",
    }


def get_hint(state, row, col):
    """Basic hint: identify a cell that must be shaded or unshaded by logic."""
    board = state["board"]

    for r in range(_ROWS):
        for c in range(_COLS):
            if board[r][c] == 0:
                num = _GRID[r][c]
                row_dups = [c2 for c2 in range(_COLS)
                            if c2 != c and board[r][c2] == 0 and _GRID[r][c2] == num]
                col_dups = [r2 for r2 in range(_ROWS)
                            if r2 != r and board[r2][c] == 0 and _GRID[r2][c] == num]

                if row_dups or col_dups:
                    if "checkerboard_parity" not in _active_extra_rules or (r + c) % 2 == 0:
                        return {
                            "value": 1,
                            "message": f"Cell ({r+1},{c+1}) has duplicate {num} — consider shading it.",
                        }

    return {"value": None, "message": "No obvious hint available. Try looking for duplicates in rows and columns."}
