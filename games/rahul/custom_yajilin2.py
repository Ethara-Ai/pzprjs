from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 4,
        "cols": 4,
        "url_body": "20b40l",
        "moves_required": [
            "mouse,left,3,1,3,3", "mouse,left,5,1,5,3",
            "mouse,left,1,3,1,5", "mouse,left,1,5,1,7",
            "mouse,left,3,1,5,1", "mouse,left,1,3,3,3",
            "mouse,left,1,7,3,7",
        ],
        "moves_hint": [],
    },
    "medium": {
        "rows": 5,
        "cols": 5,
        "url_body": "21a20v",
        "moves_required": [
            "mouse,left,3,1", "mouse,left,1,3", "mouse,left,9,9",
            "mouse,left,7,1,7,3", "mouse,left,9,1,9,3",
            "mouse,left,3,3,3,5", "mouse,left,5,3,5,5",
            "mouse,left,7,3,7,5", "mouse,left,9,3,9,5",
            "mouse,left,1,5,1,7", "mouse,left,9,5,9,7",
            "mouse,left,1,7,1,9", "mouse,left,3,7,3,9",
            "mouse,left,5,7,5,9", "mouse,left,7,7,7,9",
            "mouse,left,7,1,9,1", "mouse,left,3,3,5,3",
            "mouse,left,1,5,3,5", "mouse,left,5,5,7,5",
            "mouse,left,3,7,5,7", "mouse,left,7,7,9,7",
            "mouse,left,1,9,3,9", "mouse,left,5,9,7,9",
        ],
        "moves_hint": [],
    },
    "hard": {
        "rows": 6,
        "cols": 6,
        "url_body": "22d22zd",
        "moves_required": [
            "mouse,left,1,3", "mouse,left,11,3",
            "mouse,left,1,11", "mouse,left,11,11",
            "mouse,left,3,1,3,3", "mouse,left,9,1,9,3",
            "mouse,left,5,3,5,5", "mouse,left,7,3,7,5",
            "mouse,left,1,5,1,7", "mouse,left,3,5,3,7",
            "mouse,left,5,5,5,7", "mouse,left,7,5,7,7",
            "mouse,left,9,5,9,7", "mouse,left,11,5,11,7",
            "mouse,left,1,7,1,9", "mouse,left,11,7,11,9",
            "mouse,left,3,9,3,11", "mouse,left,5,9,5,11",
            "mouse,left,7,9,7,11", "mouse,left,9,9,9,11",
            "mouse,left,3,1,5,1", "mouse,left,5,1,7,1",
            "mouse,left,7,1,9,1", "mouse,left,3,3,5,3",
            "mouse,left,7,3,9,3", "mouse,left,1,5,3,5",
            "mouse,left,9,5,11,5", "mouse,left,3,7,5,7",
            "mouse,left,7,7,9,7", "mouse,left,1,9,3,9",
            "mouse,left,5,9,7,9", "mouse,left,9,9,11,9",
            "mouse,left,3,11,5,11", "mouse,left,7,11,9,11",
        ],
        "moves_hint": [],
    },
}


def generate_custom_yajilin2(difficulty="easy"):
    if difficulty not in _PUZZLES:
        raise ValueError(f"Unknown difficulty: {difficulty!r}. Use easy, medium, or hard.")

    p = _PUZZLES[difficulty]
    rows, cols, url_body = p["rows"], p["cols"], p["url_body"]
    now = datetime.now(timezone.utc).isoformat()

    moves_required = p["moves_required"]
    moves_hint = p["moves_hint"]
    moves_full = moves_required + moves_hint

    return {
        "puzzle_url": f"http://localhost:8000/p.html?yajilin2/{cols}/{rows}/{url_body}",
        "pid": "yajilin2",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"http://localhost:8000/p.html?yajilin2/{cols}/{rows}/{url_body}",
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
        data = generate_custom_yajilin2(d)
        print(json.dumps(data, indent=2, default=str))
        print(f"\nPlay ({d}): {data['puzzlink_url']}\n")
