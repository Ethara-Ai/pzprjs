import json
import sys
import time
from datetime import datetime, timezone


_PID = "resonance"

_PUZZLES = {
    "easy": {
        "rows": 6,
        "cols": 6,
        "regions": [
            [0, 0, 1, 1, 2, 2],
            [0, 3, 3, 1, 4, 2],
            [5, 5, 3, 6, 4, 4],
            [7, 5, 8, 6, 6, 9],
            [7, 7, 8, 8, 10, 9],
            [11, 11, 11, 10, 10, 9],
        ],
        "clues": [
            (0, 1, 1), (0, 4, 2), (0, 5, 1), (1, 1, 1), (1, 4, 1),
            (1, 5, 0), (2, 1, 1), (2, 3, 4), (2, 4, 1), (2, 5, 0),
            (3, 0, 0), (3, 1, 1), (3, 4, 2), (3, 5, 1), (4, 0, 0),
            (4, 5, 0), (5, 0, 0), (5, 1, 0), (5, 2, 1), (5, 5, 1),
        ],
        "solution": [
            (1, 0, 2), (0, 3, 3), (2, 2, 2), (3, 3, 3), (4, 2, 2), (5, 4, 2),
        ],
        "url_body": "g1h21g1h10g1g41001h210j0001h1anetb5ddddds",
    },
    "medium": {
        "rows": 8,
        "cols": 8,
        "regions": [
            [0, 0, 0, 1, 1, 1, 2, 2],
            [0, 3, 3, 3, 1, 2, 2, 2],
            [4, 4, 3, 3, 5, 5, 5, 6],
            [4, 4, 7, 7, 5, 8, 6, 6],
            [4, 7, 7, 7, 8, 8, 8, 6],
            [9, 9, 7, 10, 10, 8, 11, 6],
            [9, 9, 10, 10, 10, 11, 11, 6],
            [9, 9, 9, 10, 11, 11, 11, 6],
        ],
        "clues": [
            (0, 4, 2), (0, 6, 2), (0, 7, 1), (1, 1, 0), (1, 2, 2),
            (1, 3, 0), (1, 6, 2), (1, 7, 0), (2, 0, 0), (2, 3, 3),
            (2, 4, 2), (2, 7, 1), (3, 0, 0), (3, 1, 0), (3, 2, 2),
            (3, 3, 2), (3, 6, 1), (3, 7, 0), (4, 0, 0), (4, 1, 1),
            (4, 4, 2), (4, 5, 2), (4, 6, 0), (4, 7, 0), (5, 0, 1),
            (5, 4, 1), (5, 5, 1), (5, 6, 0), (5, 7, 0), (6, 1, 1),
            (6, 2, 0), (6, 3, 1), (6, 4, 1), (6, 5, 2), (6, 7, 0),
            (7, 0, 1), (7, 3, 1), (7, 7, 1),
        ],
        "solution": [
            (0, 2, 2), (0, 5, 3), (2, 2, 2), (2, 5, 3),
            (4, 3, 3), (6, 0, 2), (7, 5, 3),
        ],
        "url_body": "j2g21g020h200h32h10022h1001h22001i1100g10112g01h1i14koklq9dqacgej7jcimq4gk0",
    },
    "hard": {
        "rows": 10,
        "cols": 10,
        "regions": [
            [0, 0, 0, 1, 1, 2, 2, 2, 3, 3],
            [0, 0, 0, 1, 1, 2, 2, 2, 3, 3],
            [0, 0, 1, 1, 1, 2, 2, 3, 3, 3],
            [4, 4, 4, 1, 1, 5, 5, 5, 5, 3],
            [4, 4, 4, 6, 6, 5, 5, 5, 5, 7],
            [4, 4, 6, 6, 6, 6, 6, 7, 7, 7],
            [8, 8, 8, 8, 8, 6, 7, 7, 7, 7],
            [8, 8, 8, 9, 9, 9, 9, 9, 9, 11],
            [10, 10, 10, 10, 9, 9, 11, 11, 11, 11],
            [10, 10, 10, 10, 12, 12, 12, 12, 11, 11],
        ],
        "clues": [
            (0, 1, 1), (0, 3, 0), (0, 4, 0), (0, 6, 2), (0, 8, 2),
            (1, 1, 0), (1, 3, 0), (1, 4, 0), (1, 6, 1), (1, 9, 1),
            (2, 0, 0), (2, 1, 0), (2, 2, 0), (2, 3, 0), (2, 4, 0),
            (3, 0, 0), (3, 2, 0), (3, 3, 0), (3, 4, 0), (3, 5, 1),
            (3, 8, 2), (4, 2, 1), (4, 3, 0), (4, 8, 1), (4, 9, 0),
            (5, 1, 1), (5, 3, 1), (5, 7, 1), (5, 8, 0), (5, 9, 0),
            (6, 2, 0), (6, 3, 0), (6, 5, 1), (6, 6, 0), (6, 7, 0),
            (6, 8, 0), (6, 9, 0), (7, 0, 1), (7, 2, 1), (7, 7, 0),
            (7, 8, 0), (8, 0, 0), (8, 2, 0), (8, 3, 1), (8, 8, 1),
            (9, 0, 0), (9, 1, 0), (9, 2, 0), (9, 3, 0), (9, 4, 1),
            (9, 6, 1), (9, 7, 0), (9, 8, 0),
        ],
        "solution": [
            (0, 0, 2), (0, 7, 3), (2, 9, 2), (4, 1, 2),
            (3, 7, 3), (5, 4, 2), (7, 1, 2), (8, 5, 3),
            (8, 9, 2),
        ],
        "url_body": "g1g00g2g2h0g00g1h100000k0g0001h2i10j10g1g1i100h00g100001g1j00g0g01j1g00001g100g54a9518ih8830g8k120044su314uv83vue1s",
    },
}


def _build_moves(rows, cols, solution):
    moves_required = []
    moves_hint = []
    for r, c, val in solution:
        bx = 2 * c + 1
        by = 2 * r + 1
        move = f"mouse,left,{bx},{by}"
        for _ in range(val):
            moves_required.append(move)
    moves_full = moves_required + moves_hint
    return moves_full, moves_required, moves_hint


def generate_puzzle_resonance(difficulty="easy"):
    level = difficulty
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]

    moves_full, moves_required, moves_hint = _build_moves(
        rows, cols, p["solution"]
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
            "num_emitters": len(p["solution"]),
            "num_clues": len(p["clues"]),
            "num_regions": max(max(row) for row in p["regions"]) + 1,
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
        print(f"Usage: python puzzle_resonance.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_resonance(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}", file=sys.stderr)
    print(f"Grid: {meta['db_w']}x{meta['db_h']}", file=sys.stderr)
    print(f"Emitters: {meta['num_emitters']}, Clues: {meta['num_clues']}, Regions: {meta['num_regions']}", file=sys.stderr)
    print(f"Generated in {elapsed:.4f}s", file=sys.stderr)
    print(f"\nPlay: {puzzle_data['puzzlink_url']}", file=sys.stderr)
