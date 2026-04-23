"""Hitori puzzle -- custom puzzles in ppbench format.

Rules (from hitori.js variant):
  1. At least one shaded cell
  2. No two shaded cells orthogonally adjacent
  3. No two shaded cells diagonally adjacent (king-move exclusion)
  4. Checkerboard parity: shading only where 0-indexed (row+col) is even
  5. Max 2 shaded cells per row and per column
  6. Unshaded cells must be orthogonally connected
  7. No duplicate numbers among unshaded cells in any row or column

Usage:
    python3 hitori_game.py              # generate easy (default)
    python3 hitori_game.py medium       # generate medium
    python3 hitori_game.py hard         # generate hard
"""

import sys
import time
from datetime import datetime, timezone


_PUZZLES = {
    "easy": {
        "rows": 5,
        "cols": 5,
        "url_body": "1234224513351244123533451",
        "grid": [
            [1, 2, 3, 4, 2],
            [2, 4, 5, 1, 3],
            [3, 5, 1, 2, 4],
            [4, 1, 2, 3, 5],
            [3, 3, 4, 5, 1],
        ],
        "solution": [
            [0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
        ],
    },
    "medium": {
        "rows": 6,
        "cols": 6,
        "url_body": "121456234561145642456123561254612345",
        "grid": [
            [1, 2, 1, 4, 5, 6],
            [2, 3, 4, 5, 6, 1],
            [1, 4, 5, 6, 4, 2],
            [4, 5, 6, 1, 2, 3],
            [5, 6, 1, 2, 5, 4],
            [6, 1, 2, 3, 4, 5],
        ],
        "solution": [
            [0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0],
        ],
    },
    "hard": {
        "rows": 7,
        "cols": 7,
        "url_body": "2234667234567134467124567123667123367123457123556",
        "grid": [
            [2, 2, 3, 4, 6, 6, 7],
            [2, 3, 4, 5, 6, 7, 1],
            [3, 4, 4, 6, 7, 1, 2],
            [4, 5, 6, 7, 1, 2, 3],
            [6, 6, 7, 1, 2, 3, 3],
            [6, 7, 1, 2, 3, 4, 5],
            [7, 1, 2, 3, 5, 5, 6],
        ],
        "solution": [
            [1, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
        ],
    },
}


def _decode_hitori(url_body, rows, cols):
    """Decode hitori pzv URL body into a 2D grid of integers.

    Each character is a base-36 digit representing the cell number.
    Two-digit numbers are prefixed with '-'.
    """
    grid = [[0] * cols for _ in range(rows)]
    c = 0
    i = 0
    while i < len(url_body) and c < rows * cols:
        ch = url_body[i]
        if ch == "-":
            grid[c // cols][c % cols] = int(url_body[i + 1 : i + 3], 36)
            i += 3
        elif ch in (".", "%", "@"):
            grid[c // cols][c % cols] = -2
            i += 1
        else:
            grid[c // cols][c % cols] = int(ch, 36)
            i += 1
        c += 1
    return grid


def _build_moves(rows, cols, solution):
    """Return (full, required, hint) move lists in pzprjs mouse format."""
    full, req, hint = [], [], []
    for r in range(rows):
        for c in range(cols):
            x, y = 1 + c * 2, 1 + r * 2
            if solution[r][c] == 1:
                m = f"mouse,left,{x},{y}"
                full.append(m)
                req.append(m)
            else:
                m = f"mouse,right,{x},{y}"
                full.append(m)
                hint.append(m)
    return full, req, hint


def generate_custom_hitori(difficulty="easy"):
    p = _PUZZLES[difficulty]
    rows, cols = p["rows"], p["cols"]
    url_body = p["url_body"]
    solution = p["solution"]
    now = datetime.now(timezone.utc).isoformat()

    full, req, hint = _build_moves(rows, cols, solution)
    shaded = sum(
        1 for r in range(rows) for c in range(cols) if solution[r][c] == 1
    )

    return {
        "puzzle_url": f"http://pzv.jp/p.html?hitori/{cols}/{rows}/{url_body}",
        "pid": "hitori",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": shaded,
        "number_total_solution_moves": rows * cols,
        "puzzlink_url": f"https://puzz.link/p?hitori/{cols}/{rows}/{url_body}",
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": True,
            "cspuz_is_unique": True,
            "db_w": cols,
            "db_h": rows,
            "extra_rules": [
                "diagonal_ban",
                "checkerboard_parity",
                "max_2_per_line",
            ],
        },
        "created_at": now,
        "solution": {
            "moves_full": full,
            "moves_required": req,
            "moves_hint": hint,
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
    puzzle_data = generate_custom_hitori(difficulty)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))

    meta = puzzle_data["metadata"]
    print(f"\nGrid: {puzzle_data['width']}x{puzzle_data['height']}")
    print(f"Extra rules: {', '.join(meta['extra_rules'])}")
    print(f"Shaded cells: {puzzle_data['number_required_moves']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")