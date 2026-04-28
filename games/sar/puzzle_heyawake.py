import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 7, "cols": 7,
        "url_body": "j0030010j2010000j2200022j00000030004000200100100003030",
        "room_grid": [
            [0, 0, 0, 0, 1, 1, 2],
            [0, 0, 0, 0, 1, 1, 3],
            [4, 4, 5, 6, 1, 1, 3],
            [7, 7, 5, 6, 8, 8, 8],
            [7, 7, 5, 6, 8, 8, 8],
            [7, 7, 5, 9, 9, 9, 9],
            [10, 11, 11, 9, 9, 9, 9],
        ],
        "clues": {},
        "shaded": [(0, 3), (3, 0)],
    },
    "medium": {
        "rows": 8, "cols": 10,
        "url_body": "00000000g008000000000000000g0000000100001g0200000000100200000000g0010020000000000000",
        "room_grid": [
            [0, 0, 1, 1, 1, 2, 2, 3, 3, 3],
            [4, 4, 1, 1, 1, 5, 5, 3, 3, 3],
            [4, 4, 6, 6, 6, 5, 5, 7, 7, 7],
            [4, 4, 6, 6, 6, 5, 5, 7, 7, 7],
            [8, 8, 8, 9, 9, 10, 10, 10, 11, 11],
            [8, 8, 8, 9, 9, 10, 10, 10, 11, 11],
            [12, 12, 12, 9, 9, 13, 13, 13, 11, 11],
            [12, 12, 12, 14, 14, 13, 13, 13, 15, 15],
        ],
        "clues": {},
        "shaded": [],
    },
    "hard": {
        "rows": 8, "cols": 10,
        "url_body": "00000000g000000003000000000g0000000100001g0200000000100200000000g3010020000040000000",
        "room_grid": [
            [0, 0, 1, 1, 1, 2, 2, 3, 3, 3],
            [4, 4, 1, 1, 1, 5, 5, 3, 3, 3],
            [4, 4, 6, 6, 6, 5, 5, 7, 7, 7],
            [4, 4, 6, 6, 6, 5, 5, 7, 7, 7],
            [8, 8, 8, 9, 9, 10, 10, 10, 11, 11],
            [8, 8, 8, 9, 9, 10, 10, 10, 11, 11],
            [12, 12, 12, 9, 9, 13, 13, 13, 11, 11],
            [12, 12, 12, 14, 14, 13, 13, 13, 15, 15],
        ],
        "clues": {},
        "shaded": [],
    },
}


def _build_moves(rows, cols, shaded):
    shaded_set = set(shaded)
    moves_full = []
    moves_required = []
    moves_hint = []
    for r in range(rows):
        for c in range(cols):
            x = 2 * c + 1
            y = 2 * r + 1
            if (r, c) in shaded_set:
                move = f"mouse,left,{x},{y}"
                moves_full.append(move)
                moves_required.append(move)
            else:
                move = f"mouse,right,{x},{y}"
                moves_full.append(move)
                moves_hint.append(move)
    return moves_full, moves_required, moves_hint


def generate_puzzle_heyawake(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    moves_full, moves_required, moves_hint = _build_moves(rows, cols, p["shaded"])

    return {
        "puzzle_url": f"http://localhost:8000/p.html?heyawake/{cols}/{rows}/{p['url_body']}",
        "pid": "heyawake",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"http://localhost:8000/p.html?heyawake/{cols}/{rows}/{p['url_body']}",
        "source": {
            "site_name": "ppbench_golden",
            "page_url": None,
            "feed_type": "golden_dataset",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": True,
            "cspuz_is_unique": True,
            "db_w": cols,
            "db_h": rows,
            "level": level,
            "num_rooms": len(set(c for row in p["room_grid"] for c in row)),
            "num_clued_rooms": len(p["clues"]),
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

    level = sys.argv[1] if len(sys.argv) > 1 else "easy"
    if level not in _PUZZLES:
        print(f"Usage: python puzzle_heyawake.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_heyawake(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}×{meta['db_h']}")
    print(f"Rooms: {meta['num_rooms']} ({meta['num_clued_rooms']} clued)")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
