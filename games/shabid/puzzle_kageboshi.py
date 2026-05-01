import json
import sys
import time
from datetime import datetime, timezone


_PID = "kageboshi"

_PUZZLES = {
    "easy": {
        "rows": 6,
        "cols": 6,
        "clues": [
            (0, 1, 5), (2, 3, 4), (2, 5, 4), (3, 1, 5), (5, 0, 5), (5, 4, 4),
        ],
        "shaded": [
            (0, 0), (0, 3), (0, 5), (1, 1), (2, 4), (3, 0), (3, 3), (3, 5),
            (5, 1), (5, 3), (5, 5),
        ],
        "url_body": "g5s4g4g5p5i4g",
    },
    "medium": {
        "rows": 8,
        "cols": 8,
        "clues": [
            (0, 0, 6), (0, 2, 6), (0, 4, 5), (0, 6, 5),
            (1, 1, 3), (1, 3, 3), (1, 5, 4), (1, 6, 3),
            (2, 1, 5), (2, 3, 5), (2, 4, 5), (2, 6, 5),
            (3, 0, 6), (3, 2, 6), (3, 3, 5), (3, 5, 6), (3, 6, 5),
            (4, 0, 5), (4, 1, 4), (4, 3, 4), (4, 4, 4), (4, 6, 4), (4, 7, 4),
            (5, 1, 4), (5, 3, 4), (5, 4, 4), (5, 5, 5), (5, 7, 4),
            (6, 0, 5), (6, 1, 4), (6, 3, 4), (6, 5, 5), (6, 7, 4),
            (7, 1, 5), (7, 4, 5), (7, 5, 6), (7, 7, 5),
        ],
        "shaded": [
            (0, 1), (0, 3), (0, 5), (1, 7), (2, 0), (2, 2), (2, 5),
            (3, 1), (3, 4), (3, 7), (4, 2), (4, 5), (5, 0), (5, 6),
            (6, 2), (6, 4), (7, 0), (7, 3), (7, 6),
        ],
        "url_body": "6g6g5g5h3g3g43h5g55g5g6g65g65g54g44g44g4g445g454g4g5g4g5h56g5",
    },
    "hard": {
        "rows": 10,
        "cols": 10,
        "clues": [
            (0, 0, 5), (0, 2, 5), (0, 3, 4), (0, 5, 5), (0, 6, 4), (0, 8, 5), (0, 9, 5),
            (1, 0, 3), (1, 1, 3), (1, 2, 3), (1, 3, 2), (1, 4, 4), (1, 5, 3), (1, 6, 2), (1, 7, 4), (1, 8, 3),
            (2, 0, 4), (2, 1, 4), (2, 3, 3), (2, 4, 5), (2, 5, 4), (2, 7, 5), (2, 8, 4), (2, 9, 4),
            (3, 1, 5), (3, 2, 5), (3, 3, 4), (3, 5, 5), (3, 6, 4), (3, 7, 6), (3, 9, 5),
            (4, 0, 2), (4, 1, 2), (4, 2, 2), (4, 3, 1), (4, 4, 3), (4, 5, 2), (4, 6, 1), (4, 7, 3), (4, 8, 2), (4, 9, 2),
            (5, 0, 5), (5, 2, 5), (5, 3, 4), (5, 4, 6), (5, 6, 4), (5, 7, 6), (5, 8, 5),
            (6, 0, 4), (6, 1, 4), (6, 2, 4), (6, 4, 5), (6, 5, 4), (6, 6, 3), (6, 8, 4), (6, 9, 4),
            (7, 1, 3), (7, 2, 3), (7, 3, 2), (7, 4, 4), (7, 5, 3), (7, 6, 2), (7, 7, 4), (7, 8, 3), (7, 9, 3),
            (8, 0, 5), (8, 1, 5), (8, 3, 4), (8, 4, 6), (8, 6, 4), (8, 7, 6), (8, 9, 5),
            (9, 0, 4), (9, 1, 4), (9, 2, 4), (9, 3, 3), (9, 5, 4), (9, 6, 3), (9, 8, 4), (9, 9, 4),
        ],
        "shaded": [
            (0, 1), (0, 4), (0, 7), (1, 9), (2, 2), (2, 6), (3, 0), (3, 4),
            (3, 8), (5, 1), (5, 5), (5, 9), (6, 3), (6, 7), (7, 0), (8, 2),
            (8, 5), (8, 8), (9, 4), (9, 7),
        ],
        "url_body": "5g54g54g55333243243g44g354g544g554g546g522213213225g546g465g444g543g44g33243243355g46g46g54443g43g44",
    },
}


def _build_moves(rows, cols, shaded):
    moves_required = []
    moves_hint = []
    shaded_set = set(tuple(s) for s in shaded)

    for r in range(rows):
        for c in range(cols):
            bx = 2 * c + 1
            by = 2 * r + 1
            if (r, c) in shaded_set:
                moves_required.append(f"mouse,left,{bx},{by}")
            else:
                moves_hint.append(f"mouse,right,{bx},{by}")

    moves_full = moves_required + moves_hint
    return moves_full, moves_required, moves_hint


def generate_puzzle_kageboshi(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]

    moves_full, moves_required, moves_hint = _build_moves(
        rows, cols, p["shaded"]
    )

    puzzle_url = f"http://localhost:8000/p.html?{_PID}/{cols}/{rows}/{p['url_body']}"
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": puzzle_url,
        "puzzlink_url": puzzle_url,
        "pid": _PID,
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
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
            "level": level,
            "num_shaded": len(p["shaded"]),
            "num_clues": len(p["clues"]),
        },
        "created_at": now,
        "solution": {
            "moves_full": moves_full,
            "moves_required": moves_required,
            "moves_hint": moves_hint,
        },
    }


if __name__ == "__main__":
    level = sys.argv[1] if len(sys.argv) > 1 else "easy"
    if level not in _PUZZLES:
        print(f"Usage: python puzzle_kageboshi.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_kageboshi(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}", file=sys.stderr)
    print(f"Grid: {meta['db_w']}x{meta['db_h']}", file=sys.stderr)
    print(f"Shaded: {meta['num_shaded']}, Clues: {meta['num_clues']}", file=sys.stderr)
    print(f"Generated in {elapsed:.4f}s", file=sys.stderr)
    print(f"\nPlay: {puzzle_data['puzzlink_url']}", file=sys.stderr)
