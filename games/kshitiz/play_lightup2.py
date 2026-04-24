import sys
import time
from datetime import datetime, timezone


_PUZZLES = {
    "easy": {
        "rows": 4,
        "cols": 4,
        "url_body": "m2i0j",
        "bulbs": [(0, 2), (1, 0), (2, 2), (3, 0)],
    },
    "medium": {
        "rows": 5,
        "cols": 5,
        "url_body": "n2o2l",
        "bulbs": [(0, 0), (0, 4), (1, 2), (2, 0), (2, 4), (3, 2), (4, 0), (4, 4)],
    },
    "hard": {
        "rows": 6,
        "cols": 6,
        "url_body": "i0p0g1y",
        "bulbs": [(0, 0), (0, 2), (1, 5), (3, 0), (3, 2), (3, 4), (5, 1), (5, 3), (5, 5)],
    },
}


def _decode_4cell(url_body, rows, cols):
    grid = [[-1] * cols for _ in range(rows)]
    pos = 0
    i = 0
    total = rows * cols
    while i < len(url_body) and pos < total:
        ch = url_body[i]
        if ch == '.':
            r, c = divmod(pos, cols)
            grid[r][c] = -2
            pos += 1
        elif '0' <= ch <= '4':
            r, c = divmod(pos, cols)
            grid[r][c] = int(ch)
            pos += 1
        elif '5' <= ch <= '9':
            r, c = divmod(pos, cols)
            grid[r][c] = int(ch) - 5
            pos += 1
            pos += 1
        elif 'a' <= ch <= 'e':
            r, c = divmod(pos, cols)
            grid[r][c] = ord(ch) - ord('a')
            pos += 1
            pos += 2
        elif 'g' <= ch <= 'z':
            gap = ord(ch) - ord('g') + 1
            pos += gap
        i += 1
    return grid


def _build_moves(bulb_positions):
    moves = []
    for r, c in sorted(bulb_positions):
        moves.append(f"mouse,left,{1 + c * 2},{1 + r * 2}")
    return moves


def generate_custom_lightup2(difficulty="easy"):
    p = _PUZZLES[difficulty]
    rows, cols, url_body = p["rows"], p["cols"], p["url_body"]
    grid = _decode_4cell(url_body, rows, cols)
    now = datetime.now(timezone.utc).isoformat()

    num_black = sum(1 for r in range(rows) for c in range(cols) if grid[r][c] != -1)
    num_numbered = sum(1 for r in range(rows) for c in range(cols) if grid[r][c] >= 0)

    bulbs = p["bulbs"]
    moves = _build_moves(bulbs)
    has_solution = len(bulbs) > 0

    return {
        "puzzle_url": f"http://localhost:8000/p.html?lightup2/{cols}/{rows}/{url_body}",
        "pid": "lightup2",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves),
        "number_total_solution_moves": len(moves),
        "puzzlink_url": f"http://localhost:8000/p.html?lightup2/{cols}/{rows}/{url_body}",
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": has_solution,
            "cspuz_is_unique": True,
            "db_w": cols,
            "db_h": rows,
            "num_black_cells": num_black,
            "num_numbered_cells": num_numbered,
            "modified_rules": [
                "diagonal illumination (4 diagonal rays until wall/edge)",
                "diagonal wall counting (numbered walls count diagonal neighbours)",
                "no two bulbs orthogonally adjacent",
            ],
        },
        "created_at": now,
        "solution": {
            "moves_full": moves,
            "moves_required": moves,
            "moves_hint": [],
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
    puzzle_data = generate_custom_lightup2(difficulty)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))

    meta = puzzle_data["metadata"]
    print(f"\nGrid: {puzzle_data['width']}x{puzzle_data['height']}")
    print(f"Black cells: {meta['num_black_cells']} ({meta['num_numbered_cells']} numbered)")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
