import sys
import time
from datetime import datetime, timezone


_PUZZLES = {
    "easy": {
        "rows": 5, "cols": 5,
        "url_body": "5214354254455322451535421",
        "shaded": [(0, 0), (1, 1), (1, 3), (2, 2), (3, 4), (4, 1)],
    },
    "medium": {
        "rows": 6, "cols": 6,
        "url_body": "146321235246213654152543655435324465",
        "shaded": [(0, 5), (1, 0), (1, 2), (1, 4), (3, 0), (3, 3), (4, 1), (4, 5), (5, 3)],
    },
    "hard": {
        "rows": 7, "cols": 7,
        "url_body": "2147365447162165347323252776173635176253434162525",
        "shaded": [(0, 4), (1, 0), (1, 3), (1, 5), (2, 2), (3, 1), (3, 4), (4, 2), (4, 6), (5, 4), (6, 1), (6, 3), (6, 6)],
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


def generate_custom_hitori(difficulty="easy"):
    p = _PUZZLES[difficulty]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    moves_full, moves_required, moves_hint = _build_moves(rows, cols, p["shaded"])

    return {
        "puzzle_url": f"http://localhost:8000/p.html?hitori/{cols}/{rows}/{p['url_body']}",
        "pid": "hitori",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"http://localhost:8000/p.html?hitori/{cols}/{rows}/{p['url_body']}",
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
        print(f"Usage: python hitori_game.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_custom_hitori(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    print(f"\nLevel: {level}")
    print(f"Grid: {puzzle_data['width']}x{puzzle_data['height']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")