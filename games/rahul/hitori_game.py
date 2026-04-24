import sys
import time
from datetime import datetime, timezone


_PUZZLES = {
    "easy": {
        "rows": 5,
        "cols": 5,
        "url_body": "1345225143425315132334225",
        "grid": [
            [1, 3, 4, 5, 2],
            [2, 5, 1, 4, 3],
            [4, 2, 5, 3, 1],
            [5, 1, 3, 2, 3],
            [3, 4, 2, 2, 5],
        ],
    },
    "medium": {
        "rows": 6,
        "cols": 6,
        "url_body": "156433213454641532524326332145435261",
        "grid": [
            [1, 5, 6, 4, 3, 3],
            [2, 1, 3, 4, 5, 4],
            [6, 4, 1, 5, 3, 2],
            [5, 2, 4, 3, 2, 6],
            [3, 3, 2, 1, 4, 5],
            [4, 3, 5, 2, 6, 1],
        ],
    },
    "hard": {
        "rows": 7,
        "cols": 7,
        "url_body": "6327345346771226514377313624413217652743661746243",
        "grid": [
            [6, 3, 2, 7, 3, 4, 5],
            [3, 4, 6, 7, 7, 1, 2],
            [2, 6, 5, 1, 4, 3, 7],
            [7, 3, 1, 3, 6, 2, 4],
            [4, 1, 3, 2, 1, 7, 6],
            [5, 2, 7, 4, 3, 6, 6],
            [1, 7, 4, 6, 2, 4, 3],
        ],
    },
}


def generate_custom_hitori(difficulty="easy"):
    p = _PUZZLES[difficulty]
    rows, cols = p["rows"], p["cols"]
    url_body = p["url_body"]
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://pzv.jp/p.html?hitori/{cols}/{rows}/{url_body}",
        "pid": "hitori",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "puzzlink_url": f"https://puzz.link/p?hitori/{cols}/{rows}/{url_body}",
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
            "published_at": now,
        },
        "metadata": {
            "db_w": cols,
            "db_h": rows,
        },
        "created_at": now,
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
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")