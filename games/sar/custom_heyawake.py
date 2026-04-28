"""Heyawake puzzle — fixed map sssskkcc51hoi2i0k in ppbench format.

Usage:
    .venv/bin/python custom_heyawake.py

Always outputs the same hardcoded 6×6 puzzle (heyawake/6/6/sssskkcc51hoi2i0k).
"""

import time
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Hardcoded puzzle: heyawake/6/6/sssskkcc51hoi2i0k
# ---------------------------------------------------------------------------

_ROWS = 6
_COLS = 6
_URL_BODY = "sssskkcc51hoi2i0k"

_ROOM_GRID = [
    [0, 1, 2, 3, 3, 3],
    [0, 4, 5, 3, 3, 3],
    [6, 7, 5, 3, 3, 3],
    [8, 7, 9, 3, 3, 3],
    [8, 10, 10, 3, 3, 3],
    [11, 12, 12, 3, 3, 3],
]

_ROOMS = {
    0: (0, 0, 2, 1),
    1: (0, 1, 1, 2),
    2: (0, 2, 1, 3),
    3: (0, 3, 6, 6),
    4: (1, 1, 2, 2),
    5: (1, 2, 3, 3),
    6: (2, 0, 3, 1),
    7: (2, 1, 4, 2),
    8: (3, 0, 5, 1),
    9: (3, 2, 4, 3),
    10: (4, 1, 5, 3),
    11: (5, 0, 6, 1),
    12: (5, 1, 6, 3),
}

_CLUES = {3: 2, 7: 0}

_SOLUTION = [
    [0, 1, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [1, 0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
]


def _build_moves(rows, cols, solution):
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


def generate_custom_heyawake():
    full, req, hint = _build_moves(_ROWS, _COLS, _SOLUTION)
    shaded = sum(1 for r in range(_ROWS) for c in range(_COLS) if _SOLUTION[r][c] == 1)
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://pzv.jp/p.html?heyawake/{_COLS}/{_ROWS}/{_URL_BODY}",
        "pid": "heyawake",
        "sort_key": None,
        "width": _COLS,
        "height": _ROWS,
        "area": _ROWS * _COLS,
        "number_required_moves": shaded,
        "number_total_solution_moves": _ROWS * _COLS,
        "puzzlink_url": f"https://puzz.link/p?heyawake/{_COLS}/{_ROWS}/{_URL_BODY}",
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
            "published_at": now
        },
        "metadata": {
            "has_structured_solution": True,
            "cspuz_is_unique": True,
            "db_w": _COLS,
            "db_h": _ROWS,
            "num_rooms": len(_ROOMS),
            "num_clued_rooms": len(_CLUES)
        },
        "created_at": now,
        "solution": {
            "moves_full": full,
            "moves_required": req,
            "moves_hint": hint
        }
    }


if __name__ == "__main__":
    import json

    t0 = time.monotonic()
    puzzle_data = generate_custom_heyawake()
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))

    meta = puzzle_data["metadata"]
    print(f"\nGrid: {_COLS}x{_ROWS}")
    print(f"Rooms: {meta['num_rooms']} ({meta['num_clued_rooms']} clued)")
    print(f"Shaded cells: {puzzle_data['number_required_moves']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
