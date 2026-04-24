from datetime import datetime, timezone

_FLAGS = "ns"

_PUZZLES = {
    "easy": {
        "rows": 5,
        "cols": 5,
        "url_body": "gp1kb4t6",
        "shaded": [
            (0, 0), (0, 2), (0, 3), (0, 4),
            (1, 0), (1, 1), (1, 2), (1, 4),
            (2, 0), (2, 2), (2, 3), (2, 4),
            (3, 0), (3, 1), (3, 2), (3, 4),
            (4, 0), (4, 2), (4, 3), (4, 4),
        ],
    },
    "medium": {
        "rows": 5,
        "cols": 5,
        "url_body": "b7ik8am1",
        "shaded": [
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
            (1, 0), (1, 2), (1, 4),
            (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
            (3, 1), (3, 3),
            (4, 0), (4, 1), (4, 2), (4, 3), (4, 4),
        ],
    },
    "hard": {
        "rows": 5,
        "cols": 5,
        "url_body": "8bj94n8a",
        "shaded": [
            (0, 0), (0, 2), (0, 3), (0, 4),
            (1, 0), (1, 1), (1, 2), (1, 4),
            (2, 0), (2, 2), (2, 3), (2, 4),
            (3, 0), (3, 1), (3, 2), (3, 4),
            (4, 0), (4, 2), (4, 3), (4, 4),
        ],
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


def generate_custom_lits(difficulty="easy"):
    if difficulty not in _PUZZLES:
        raise ValueError(f"Unknown difficulty: {difficulty!r}. Use easy, medium, or hard.")

    p = _PUZZLES[difficulty]
    rows, cols, url_body = p["rows"], p["cols"], p["url_body"]
    now = datetime.now(timezone.utc).isoformat()

    moves_full, moves_required, moves_hint = _build_moves(
        rows, cols, p["shaded"]
    )

    return {
        "puzzle_url": f"http://localhost:8000/p.html?lits/{_FLAGS}/{cols}/{rows}/{url_body}",
        "pid": "lits",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"http://localhost:8000/p.html?lits/{_FLAGS}/{cols}/{rows}/{url_body}",
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
            "difficulty": difficulty,
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
    import sys

    diff = sys.argv[1] if len(sys.argv) > 1 else None

    targets = [diff] if diff else ["easy", "medium", "hard"]
    for d in targets:
        data = generate_custom_lits(d)
        print(json.dumps(data, indent=2, default=str))
        print(f"\nPlay ({d}): {data['puzzlink_url']}\n")
