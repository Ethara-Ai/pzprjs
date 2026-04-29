import sys
import time
from collections import deque
from datetime import datetime, timezone


_PUZZLES = {
    "easy": {
        "rows": 3,
        "cols": 3,
        "url_body": "3g3l",
    },
    "medium": {
        "rows": 5,
        "cols": 4,
        "url_body": "2g2l3g3n",
    },
    "hard": {
        "rows": 8,
        "cols": 4,
        "url_body": "2g2l3g3n3g3o",
    },
}

_DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]


def _decode_number16(url_body, rows, cols):
    grid = [[-1] * cols for _ in range(rows)]
    pos = 0
    i = 0
    total = rows * cols
    while i < len(url_body) and pos < total:
        ch = url_body[i]
        if ch == '.':
            pos += 1
        elif ch == '-':
            val = int(url_body[i + 1:i + 3], 16)
            r, c = divmod(pos, cols)
            grid[r][c] = val
            pos += 1
            i += 2
        elif ch == '+':
            val = int(url_body[i + 1:i + 4], 16)
            r, c = divmod(pos, cols)
            grid[r][c] = val
            pos += 1
            i += 3
        elif 'g' <= ch <= 'z':
            gap = ord(ch) - ord('g') + 1
            pos += gap
        else:
            val = int(ch, 16)
            r, c = divmod(pos, cols)
            grid[r][c] = val
            pos += 1
        i += 1
    return grid


def _gen_straight_lines(r0, c0, n, rows, cols):
    """Generate all straight-line (horizontal/vertical) island placements
    of length *n* that include the clue cell (r0, c0)."""
    if n == 1:
        return [frozenset([(r0, c0)])]
    lines = []
    # Horizontal lines through (r0, c0)
    for start_c in range(max(0, c0 - n + 1), min(cols - n + 1, c0 + 1)):
        lines.append(frozenset((r0, start_c + j) for j in range(n)))
    # Vertical lines through (r0, c0)
    for start_r in range(max(0, r0 - n + 1), min(rows - n + 1, r0 + 1)):
        lines.append(frozenset((start_r + j, c0) for j in range(n)))
    return lines


def _solve_nurikabe(grid, rows, cols):
    clues = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] > 0:
                clues.append((r, c, grid[r][c]))

    options = []
    for r, c, n in clues:
        lines = _gen_straight_lines(r, c, n, rows, cols)
        options.append(lines)

    if any(len(o) == 0 for o in options):
        return None

    indices = sorted(range(len(clues)), key=lambda i: len(options[i]))
    cell_owner = {}
    chosen = [None] * len(clues)

    def _neighbors(r, c):
        for dr, dc in _DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                yield nr, nc

    def _island_adj_conflict(poly, idx):
        for r, c in poly:
            for nr, nc in _neighbors(r, c):
                if (nr, nc) in cell_owner and cell_owner[(nr, nc)] != idx and (nr, nc) not in poly:
                    return True
        return False

    def _shaded_regions_valid():
        all_island = set(cell_owner.keys())
        visited = set()
        for r in range(rows):
            for c in range(cols):
                if (r, c) not in all_island and (r, c) not in visited:
                    region_size = 0
                    queue = deque([(r, c)])
                    visited.add((r, c))
                    while queue:
                        cr, cc = queue.popleft()
                        region_size += 1
                        if region_size > 3:
                            return False
                        for nr, nc in _neighbors(cr, cc):
                            if (nr, nc) not in all_island and (nr, nc) not in visited:
                                visited.add((nr, nc))
                                queue.append((nr, nc))
        return True

    def _backtrack(order_idx):
        if order_idx == len(clues):
            return _shaded_regions_valid()
        idx = indices[order_idx]
        for poly in options[idx]:
            if any(c in cell_owner for c in poly):
                continue
            if _island_adj_conflict(poly, idx):
                continue
            chosen[idx] = poly
            for c in poly:
                cell_owner[c] = idx
            if _backtrack(order_idx + 1):
                return True
            for c in poly:
                del cell_owner[c]
            chosen[idx] = None
        return False

    if not _backtrack(0):
        return None

    solution = [[1] * cols for _ in range(rows)]
    for cells in chosen:
        for r, c in cells:
            solution[r][c] = 0
    return solution


def _build_moves(rows, cols, grid, solution):
    moves_full = []
    moves_required = []
    moves_hint = []

    for r in range(rows):
        for c in range(cols):
            x = 1 + c * 2
            y = 1 + r * 2
            if solution[r][c] == 1:
                move = f"mouse,left,{x},{y}"
                moves_full.append(move)
                moves_required.append(move)
            else:
                if grid[r][c] <= 0:
                    move = f"mouse,right,{x},{y}"
                    moves_full.append(move)
                    moves_hint.append(move)

    return moves_full, moves_required, moves_hint


def generate_custom_nurikabe(difficulty="easy"):
    p = _PUZZLES[difficulty]
    rows, cols, url_body = p["rows"], p["cols"], p["url_body"]
    grid = _decode_number16(url_body, rows, cols)
    now = datetime.now(timezone.utc).isoformat()

    num_clues = sum(1 for r in range(rows) for c in range(cols) if grid[r][c] > 0)

    solution = _solve_nurikabe(grid, rows, cols)
    if solution is not None:
        moves_full, moves_required, moves_hint = _build_moves(
            rows, cols, grid, solution,
        )
        has_solution = True
    else:
        moves_full, moves_required, moves_hint = [], [], []
        has_solution = False

    return {
        "puzzle_url": f"http://localhost:8000/p.html?nurikabe_custom/{cols}/{rows}/{url_body}",
        "pid": "nurikabe_custom",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"http://localhost:8000/p.html?nurikabe_custom/{cols}/{rows}/{url_body}",
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": has_solution,
            "cspuz_is_unique": True,
            "db_w": cols,
            "db_h": rows,
            "num_island_clues": num_clues,
        },
        "created_at": now,
        "solution": {
            "moves_full": moves_full,
            "moves_required": moves_required,
            "moves_hint": moves_hint,
        },
    }


if __name__ == "__main__":
    import json

    difficulty = sys.argv[1].lower() if len(sys.argv) > 1 else "easy"
    if difficulty not in _PUZZLES:
        print(f"Unknown difficulty: {difficulty}")
        print(f"Available: {', '.join(_PUZZLES)}")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_custom_nurikabe(difficulty)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))

    meta = puzzle_data["metadata"]
    print(f"\nGrid: {puzzle_data['width']}x{puzzle_data['height']}")
    print(f"Island clues: {meta['num_island_clues']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
