from datetime import datetime, timezone

_FLAGS = "d"

_PUZZLES = {
    "easy": {
        "rows": 4,
        "cols": 4,
        "url_body": "a21n",
    },
    "medium": {
        "rows": 6,
        "cols": 6,
        "url_body": "42u32m",
    },
    "hard": {
        "rows": 6,
        "cols": 4,
        "url_body": "i31g40f",
    },
}


def generate_custom_yajilin(difficulty="easy"):
    if difficulty not in _PUZZLES:
        raise ValueError(f"Unknown difficulty: {difficulty!r}. Use easy, medium, or hard.")

    p = _PUZZLES[difficulty]
    rows, cols, url_body = p["rows"], p["cols"], p["url_body"]
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://pzv.jp/p.html?yajilin/{_FLAGS}/{cols}/{rows}/{url_body}",
        "pid": "yajilin",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "puzzlink_url": f"https://puzz.link/p?yajilin/{_FLAGS}/{cols}/{rows}/{url_body}",
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": False,
            "db_w": cols,
            "db_h": rows,
            "difficulty": difficulty,
        },
        "created_at": now,
    }


if __name__ == "__main__":
    import json
    import sys

    diff = sys.argv[1] if len(sys.argv) > 1 else None

    targets = [diff] if diff else ["easy", "medium", "hard"]
    for d in targets:
        data = generate_custom_yajilin(d)
        print(json.dumps(data, indent=2, default=str))
        print(f"\nPlay ({d}): {data['puzzlink_url']}\n")
