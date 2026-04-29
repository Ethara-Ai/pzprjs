import sys
import time
from datetime import datetime, timezone


_PUZZLES = {
    "easy": {
        "rows": 4, "cols": 4,
        "url_body": "f10a30f20",
        "shaded": [(3, 0)],
    },
    "medium": {
        "rows": 6, "cols": 6,
        "url_body": "g20h201010o31a",
        "shaded": [(2, 3), (5, 3), (5, 5)],
    },
    "hard": {
        "rows": 7, "cols": 7,
        "url_body": "c22i30i11b31d30g31c31a122020a",
        "shaded": [(0, 2), (0, 6), (3, 3), (5, 3), (6, 0), (6, 2), (6, 6)],
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
                move = f"mouse,right,{x},{y}"
                moves_full.append(move)
                moves_required.append(move)
            else:
                move = f"mouse,right,{x},{y}"
                moves_full.append(move)
                moves_hint.append(move)
    return moves_full, moves_required, moves_hint


def generate_custom_yajilin(difficulty="easy"):
    p = _PUZZLES[difficulty]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    moves_full, moves_required, moves_hint = _build_moves(rows, cols, p["shaded"])

    return {
        "puzzle_url": f"http://localhost:8000/p.html?yajilin/{cols}/{rows}/{p['url_body']}",
        "pid": "yajilin",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"http://localhost:8000/p.html?yajilin/{cols}/{rows}/{p['url_body']}",
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
        print(f"Usage: python custom_yajilin.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_custom_yajilin(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}x{meta['db_h']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")