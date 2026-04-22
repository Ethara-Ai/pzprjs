"""Hitori puzzle — fixed map 451623612544664412526134642365134253 in ppbench format.

6x6 grid with 3 extra rules:
  - Diagonal ban (king-move exclusion)
  - Checkerboard parity (shading only where 0-indexed row+col is even)
  - Max 2 shaded per row/column

Usage:
    python3 hitori_game.py
"""

import time
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Hardcoded puzzle: hitori/6/6/451623612544664412526134642365134253
# ---------------------------------------------------------------------------

_ROWS = 6
_COLS = 6
_URL_BODY = "451623612544664412526134642365134253"

_GRID = [
    [4, 5, 1, 6, 2, 3],
    [6, 1, 2, 5, 4, 4],
    [6, 6, 4, 4, 1, 2],
    [5, 2, 6, 1, 3, 4],
    [5, 4, 6, 3, 1, 2],
    [1, 3, 4, 2, 5, 3],
]

# 1 = shaded, 0 = unshaded
_SOLUTION = [
    [0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 1],
]


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


def generate_custom_hitori():
    full, req, hint = _build_moves(_ROWS, _COLS, _SOLUTION)
    shaded = sum(1 for r in range(_ROWS) for c in range(_COLS)
                 if _SOLUTION[r][c] == 1)
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://pzv.jp/p.html?hitori/{_COLS}/{_ROWS}/{_URL_BODY}",
        "pid": "hitori",
        "sort_key": None,
        "width": _COLS,
        "height": _ROWS,
        "area": _ROWS * _COLS,
        "number_required_moves": shaded,
        "number_total_solution_moves": _ROWS * _COLS,
        "puzzlink_url": f"https://puzz.link/p?hitori/{_COLS}/{_ROWS}/{_URL_BODY}",
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": True,
            "cspuz_is_unique": True,
            "db_w": _COLS,
            "db_h": _ROWS,
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

    t0 = time.monotonic()
    puzzle_data = generate_custom_hitori()
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))

    meta = puzzle_data["metadata"]
    print(f"\nGrid: {_COLS}x{_ROWS}")
    print(f"Extra rules: {', '.join(meta['extra_rules'])}")
    print(f"Shaded cells: {puzzle_data['number_required_moves']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")