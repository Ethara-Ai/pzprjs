import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 6, "cols": 6, "max_val": 4,
        "url_body": "1g1434g3h4g1i1g4g41g1k4414g4340040o00k020",
        "solution": [
            [1, 2, 1, 4, 3, 4],
            [2, 3, 2, 3, 4, 3],
            [1, 2, 3, 2, 1, 2],
            [4, 3, 4, 1, 2, 1],
            [3, 2, 3, 2, 3, 4],
            [4, 1, 4, 3, 4, 3],
        ],
        "clues": {
            "0,0": 1, "0,2": 1, "0,3": 4, "0,4": 3, "0,5": 4,
            "1,1": 3, "1,4": 4,
            "2,0": 1, "2,4": 1,
            "3,0": 4, "3,2": 4, "3,3": 1, "3,5": 1,
            "4,5": 4,
            "5,0": 4, "5,1": 1, "5,2": 4, "5,4": 4, "5,5": 3,
        },
    },
    "medium": {
        "rows": 8, "cols": 8, "max_val": 5,
        "url_body": "1i5j1g3g5g1h5i1j5j5i1j5i1g5h1i5g2h14h3024h1088i440000000000000",
        "solution": [
            [1, 2, 3, 4, 5, 4, 3, 2],
            [2, 1, 4, 3, 4, 5, 2, 1],
            [3, 2, 5, 4, 3, 4, 1, 2],
            [4, 3, 4, 5, 2, 3, 2, 3],
            [5, 4, 3, 4, 1, 2, 3, 4],
            [4, 5, 2, 3, 2, 1, 4, 5],
            [3, 4, 1, 2, 3, 2, 5, 4],
            [2, 3, 2, 1, 4, 3, 4, 3],
        ],
        "clues": {
            "0,0": 1, "0,4": 5,
            "1,1": 1, "1,3": 3, "1,5": 5, "1,7": 1,
            "2,2": 5, "2,6": 1,
            "3,3": 5,
            "4,0": 5, "4,4": 1,
            "5,1": 5, "5,5": 1, "5,7": 5,
            "6,2": 1, "6,6": 5,
            "7,0": 2, "7,3": 1, "7,4": 4, "7,7": 3,
        },
    },
    "hard": {
        "rows": 10, "cols": 10, "max_val": 6,
        "url_body": "h14g6h12j4j1i6l6i6g6j6k6j6h1h6p6i1l1i1g1i21g3g521h4g80g0c0o5g80g0c0o000000000000000000",
        "solution": [
            [3, 2, 1, 4, 5, 6, 3, 2, 1, 2],
            [4, 3, 2, 5, 4, 5, 4, 3, 2, 1],
            [5, 4, 3, 6, 5, 4, 5, 4, 3, 2],
            [6, 5, 4, 5, 6, 3, 6, 5, 4, 3],
            [5, 6, 5, 4, 5, 2, 5, 6, 5, 4],
            [4, 5, 6, 3, 4, 1, 4, 5, 6, 5],
            [3, 4, 5, 2, 3, 2, 3, 4, 5, 6],
            [2, 3, 4, 1, 2, 3, 2, 3, 4, 5],
            [1, 2, 3, 2, 1, 4, 1, 2, 3, 4],
            [2, 1, 2, 3, 2, 5, 2, 1, 2, 3],
        ],
        "clues": {
            "0,2": 1, "0,3": 4, "0,5": 6, "0,8": 1, "0,9": 2,
            "1,4": 4, "1,9": 1,
            "2,3": 6,
            "3,0": 6, "3,4": 6, "3,6": 6,
            "4,1": 6, "4,7": 6,
            "5,2": 6, "5,5": 1, "5,8": 6,
            "6,9": 6,
            "7,3": 1,
            "8,0": 1, "8,4": 1, "8,6": 1,
            "9,0": 2, "9,1": 1, "9,3": 3, "9,5": 5, "9,6": 2, "9,7": 1,
        },
    },
}

_PID = "gradientwalls"


def _build_moves(rows, cols, solution, clues):
    clue_set = set()
    for key in clues:
        r, c = map(int, key.split(","))
        clue_set.add((r, c))

    moves_full = []
    moves_required = []
    moves_hint = []

    for r in range(rows):
        for c in range(cols):
            if (r, c) in clue_set:
                continue
            bx = 2 * c + 1
            by = 2 * r + 1
            val = solution[r][c]
            move = f"mouse,left,{bx},{by}"
            # First click sets cursor, then val clicks to cycle to value
            for _ in range(val + 1):
                moves_full.append(move)
                moves_required.append(move)

    return moves_full, moves_required, moves_hint


def generate_puzzle_gradientwalls(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    moves_full, moves_required, moves_hint = _build_moves(
        rows, cols, p["solution"], p["clues"]
    )

    return {
        "puzzle_url": f"http://localhost:8000/p.html?{_PID}/{cols}/{rows}/{p['url_body']}",
        "pid": _PID,
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"http://localhost:8000/p.html?{_PID}/{cols}/{rows}/{p['url_body']}",
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
            "max_val": p["max_val"],
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
    import json

    level = sys.argv[1] if len(sys.argv) > 1 else "easy"
    if level not in _PUZZLES:
        print(f"Usage: python puzzle_gradientwalls.py [easy|medium|hard]", file=sys.stderr)
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_gradientwalls(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}", file=sys.stderr)
    print(f"Grid: {meta['db_w']}x{meta['db_h']}", file=sys.stderr)
    print(f"Max value: {meta['max_val']}", file=sys.stderr)
    print(f"Clues: {meta['num_clues']}", file=sys.stderr)
    print(f"Required moves: {puzzle_data['number_required_moves']}", file=sys.stderr)
    print(f"Generated in {elapsed:.4f}s", file=sys.stderr)
    print(f"\nPlay: {puzzle_data['puzzlink_url']}", file=sys.stderr)
