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
        "shaded": [(0, 4), (4, 0)],
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
        "shaded": [(0, 2), (2, 0), (2, 4), (4, 4)],
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
        "shaded": [(0, 0), (0, 4), (2, 2), (4, 0), (4, 6), (6, 5)],
    },
}


def _build_moves(rows, cols, shaded):
    shaded_set = set(shaded)
    moves_required = []
    moves_hint = []

    for r, c in sorted(shaded_set):
        moves_required.append(f"mouse,left,{2 * c + 1},{2 * r + 1}")

    for r in range(rows):
        for c in range(cols):
            if (r, c) not in shaded_set:
                moves_hint.append(f"mouse,right,{2 * c + 1},{2 * r + 1}")

    moves_full = moves_required + moves_hint
    return moves_full, moves_required, moves_hint


def generate_custom_hitori(difficulty="easy"):
    p = _PUZZLES[difficulty]
    rows, cols = p["rows"], p["cols"]
    url_body = p["url_body"]
    now = datetime.now(timezone.utc).isoformat()

    moves_full, moves_required, moves_hint = _build_moves(
        rows, cols, p["shaded"]
    )

    return {
        "puzzle_url": f"http://localhost:8000/p.html?hitori/{cols}/{rows}/{url_body}",
        "pid": "hitori",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"http://localhost:8000/p.html?hitori/{cols}/{rows}/{url_body}",
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": True,
            "cspuz_is_unique": False,
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
    puzzle_data = generate_custom_hitori(difficulty)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))

    meta = puzzle_data["metadata"]
    print(f"\nGrid: {puzzle_data['width']}x{puzzle_data['height']}")
    print(f"Extra rules: {', '.join(meta['extra_rules'])}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
