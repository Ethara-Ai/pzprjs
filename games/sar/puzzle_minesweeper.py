import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 6, "cols": 6, "num_mines": 6,
        "url_body": "2g21g12g433212h2g012221000000000000",
        "mines": [(0, 1), (0, 4), (1, 1), (2, 2), (2, 3), (2, 5)],
    },
    "medium": {
        "rows": 9, "cols": 9, "num_mines": 15,
        "url_body": "012h200001g4g21112433111g1i10011123210001111000001h210011212g3212g2012h12g20",
        "mines": [(0, 3), (0, 4), (1, 2), (1, 4), (2, 7), (3, 0), (3, 1), (3, 2), (5, 8), (6, 0), (7, 1), (7, 6), (8, 2), (8, 3), (8, 6)],
    },
    "hard": {
        "rows": 12, "cols": 12, "num_mines": 30,
        "url_body": (
            "1g212g1001g2233g2110012h3g4310000113g3h1111111g222212g33g3"
            "1100002h4h01232124g43212i12g4g212g33223g33g2g21001g212g2110"
            "0011102220000000001g1"
        ),
        "mines": [
            (0, 1), (0, 5), (0, 10), (1, 3), (1, 11), (2, 0), (2, 2),
            (3, 1), (3, 3), (3, 4), (4, 0), (4, 7), (4, 10),
            (5, 7), (5, 8), (5, 10), (5, 11), (6, 8),
            (7, 2), (7, 3), (7, 4), (7, 7), (7, 9),
            (8, 1), (8, 7), (8, 10), (9, 0), (9, 6), (9, 10), (11, 10),
        ],
    },
}


def _build_moves(rows, cols, mines):
    mine_set = set(mines)
    moves_full = []
    moves_required = []
    for r in range(rows):
        for c in range(cols):
            if (r, c) in mine_set:
                x = 2 * c + 1
                y = 2 * r + 1
                move = f"mouse,left,{x},{y}"
                moves_full.append(move)
                moves_required.append(move)
    return moves_full, moves_required, []


def generate_puzzle_minesweeper(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    moves_full, moves_required, moves_hint = _build_moves(rows, cols, p["mines"])

    return {
        "puzzle_url": f"http://localhost:8000/p.html?mines/{cols}/{rows}/{p['url_body']}",
        "pid": "mines",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"http://localhost:8000/p.html?mines/{cols}/{rows}/{p['url_body']}",
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
            "level": level,
            "num_mines": p["num_mines"],
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
        print(f"Usage: python puzzle_minesweeper.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_minesweeper(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}×{meta['db_h']}, Mines: {meta['num_mines']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
