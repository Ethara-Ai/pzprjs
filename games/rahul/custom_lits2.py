from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 5,
        "cols": 5,
        "url_body": "hrn6f03g",
    },
    "medium": {
        "rows": 6,
        "cols": 6,
        "url_body": "lquln5513c9q",
    },
    "hard": {
        "rows": 6,
        "cols": 6,
        "url_body": "jprl1160hjtu",
    },
}


def generate_custom_lits2(difficulty="easy"):
    if difficulty not in _PUZZLES:
        raise ValueError(f"Unknown difficulty: {difficulty!r}. Use easy, medium, or hard.")

    p = _PUZZLES[difficulty]
    rows, cols, url_body = p["rows"], p["cols"], p["url_body"]
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://localhost:8000/p.html?lits2/{cols}/{rows}/{url_body}",
        "pid": "lits2",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": 0,
        "number_total_solution_moves": 0,
        "puzzlink_url": f"http://localhost:8000/p.html?lits2/{cols}/{rows}/{url_body}",
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": False,
            "cspuz_is_unique": True,
            "db_w": cols,
            "db_h": rows,
            "difficulty": difficulty,
            "unsolvable": True,
        },
        "created_at": now,
        "solution": {
            "moves_full": [],
            "moves_required": [],
            "moves_hint": [],
        },
    }


if __name__ == "__main__":
    import json
    import sys

    diff = sys.argv[1] if len(sys.argv) > 1 else None

    targets = [diff] if diff else ["easy", "medium", "hard"]
    for d in targets:
        data = generate_custom_lits2(d)
        print(json.dumps(data, indent=2, default=str))
        print(f"\nPlay ({d}): {data['puzzlink_url']}\n")
