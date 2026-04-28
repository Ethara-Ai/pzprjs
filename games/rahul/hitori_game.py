import sys
import time
from datetime import datetime, timezone


_PUZZLES = {
    "easy": {
        "rows": 5, "cols": 5,
        "url_body": "4253134512135244133531243",
        "shaded": [(0, 0), (0, 2), (1, 3), (2, 2), (3, 1), (3, 3), (4, 0)],
    },
    "medium": {
        "rows": 6, "cols": 6,
        "url_body": "124356351462356243413255166135645213",
        "shaded": [(0, 4), (1, 1), (2, 0), (3, 3), (3, 5), (4, 0), (4, 4), (5, 1), (5, 3)],
    },
    "hard": {
        "rows": 8, "cols": 8,
        "url_body": "1583264854326472838677153264715826471173647158327735832671583264",
        "shaded": [(0, 2), (1, 5), (1, 7), (2, 0), (2, 4), (3, 5), (3, 7), (4, 4), (4, 6), (5, 1), (6, 0), (6, 2)],
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