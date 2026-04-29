import sys
import time
from datetime import datetime, timezone


_PUZZLES = {
    "easy": {
        "rows": 5, "cols": 5,
        "url_body": "0934sr43",
        "room_grid": [
            [3, 3, 3, 3, 3],
            [0, 0, 0, 3, 3],
            [1, 1, 0, 0, 0],
            [1, 1, 2, 0, 0],
            [1, 1, 2, 2, 2],
        ],
        "shaded": [
            (0, 2), (0, 3), (0, 4), (1, 1), (1, 2), (1, 4),
            (2, 0), (2, 2), (2, 3), (3, 0), (3, 1), (3, 2),
            (4, 0), (4, 2), (4, 3), (4, 4),
        ],
    },
    "medium": {
        "rows": 6, "cols": 6,
        "url_body": "4ptiuhki2p8a",
        "room_grid": [
            [4, 4, 4, 3, 3, 3],
            [1, 4, 3, 3, 3, 5],
            [1, 4, 0, 3, 3, 5],
            [1, 0, 0, 0, 5, 5],
            [1, 2, 0, 2, 5, 5],
            [1, 2, 2, 2, 2, 5],
        ],
        "shaded": [
            (0, 0), (0, 1), (0, 2), (0, 3), (1, 1), (1, 3), (1, 4),
            (2, 0), (2, 2), (2, 4), (3, 0), (3, 1), (3, 2), (3, 3),
            (3, 4), (3, 5), (4, 0), (4, 3), (4, 5), (5, 0), (5, 1),
            (5, 2), (5, 3), (5, 5),
        ],
    },
    "hard": {
        "rows": 7, "cols": 7,
        "url_body": "10gpc6i20v7gcce4e0",
        "room_grid": [
            [6, 6, 6, 6, 6, 3, 3],
            [1, 1, 1, 1, 1, 3, 3],
            [4, 4, 4, 4, 1, 3, 3],
            [4, 4, 2, 2, 1, 3, 3],
            [2, 2, 2, 2, 1, 5, 5],
            [0, 2, 2, 2, 5, 5, 5],
            [0, 0, 0, 5, 5, 5, 5],
        ],
        "shaded": [
            (0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (1, 4), (1, 6),
            (2, 0), (2, 1), (2, 2), (2, 4), (2, 5), (2, 6), (3, 1),
            (3, 4), (3, 6), (4, 1), (4, 2), (4, 6), (5, 0), (5, 2),
            (5, 3), (5, 4), (5, 5), (5, 6), (6, 0), (6, 1), (6, 2),
        ],
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


def generate_custom_lits(difficulty="easy"):
    p = _PUZZLES[difficulty]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    moves_full, moves_required, moves_hint = _build_moves(rows, cols, p["shaded"])

    return {
        "puzzle_url": f"http://localhost:8000/p.html?lits/{cols}/{rows}/{p['url_body']}",
        "pid": "lits",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"http://localhost:8000/p.html?lits/{cols}/{rows}/{p['url_body']}",
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
            "level": difficulty,
            "num_rooms": len(set(c for row in p["room_grid"] for c in row)),
            "num_shaded": len(p["shaded"]),
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
        print(f"Usage: python custom_lits.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_custom_lits(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}x{meta['db_h']}")
    print(f"Rooms: {meta['num_rooms']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")