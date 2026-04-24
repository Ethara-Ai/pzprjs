import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 6, "cols": 6, "num_mines": 6,
        "url_body": "g1000012221001h1002342112g2g11g2211",
        "mines": [(0, 0), (2, 2), (2, 3), (4, 2), (4, 4), (5, 1)],
    },
    "medium": {
        "rows": 9, "cols": 9, "num_mines": 15,
        "url_body": "001g2110000112g100000012210000001g1000001222111001g23h433323m12g324g421111",
        "mines": [(0, 3), (1, 5), (3, 6), (5, 5), (5, 8), (6, 0), (6, 7), (6, 8), (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 7), (8, 2)],
    },
    "hard": {
        "rows": 12, "cols": 12, "num_mines": 30,
        "url_body": (
            "1g101121212g11101g2g3g42001232213h1112h20023311g24g4122g101234g3g3g3"
            "1001h2224g2000123212g32110001g12g32g2111233213g4g1g11h213g421111222g22g1"
        ),
        "mines": [
            (0, 1), (0, 11), (1, 5), (1, 7), (1, 9), (2, 9), (2, 10),
            (3, 3), (3, 4), (4, 1), (4, 4), (4, 9),
            (5, 4), (5, 6), (5, 8), (6, 2), (6, 3), (6, 8),
            (7, 7), (8, 4), (8, 7), (8, 10), (9, 9), (9, 11),
            (10, 1), (10, 4), (10, 5), (10, 9), (11, 7), (11, 10),
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


def generate_puzzle_minesweeper2(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    moves_full, moves_required, moves_hint = _build_moves(rows, cols, p["mines"])

    return {
        "puzzle_url": f"http://localhost:8000/p.html?mines2/{cols}/{rows}/{p['url_body']}",
        "pid": "mines2",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"http://localhost:8000/p.html?mines2/{cols}/{rows}/{p['url_body']}",
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
        print(f"Usage: python puzzle_minesweeper2.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_minesweeper2(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}×{meta['db_h']}, Mines: {meta['num_mines']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
