import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 7, "cols": 7,
        "url_body": "2hblosca00fhjg0fs012g1i313h",
        "room_grid": [
            [0, 0, 0, 0, 1, 1, 2],
            [0, 0, 0, 0, 1, 1, 3],
            [4, 4, 5, 6, 1, 1, 3],
            [7, 7, 5, 6, 8, 8, 8],
            [7, 7, 5, 6, 8, 8, 8],
            [7, 7, 5, 9, 9, 9, 9],
            [10, 11, 11, 9, 9, 9, 9],
        ],
        "clues": {0: 1, 1: 2, 3: 1, 7: 3, 8: 1, 9: 3},
        "shaded": [(0, 5), (1, 0), (1, 4), (2, 2), (2, 6), (3, 1), (3, 4), (4, 0), (4, 3), (5, 1), (5, 5), (6, 3), (6, 6)],
    },
    "medium": {
        "rows": 8, "cols": 10,
        "url_body": "98ih52a2i54a8kgoo7700vv00ss33i0222332321i",
        "room_grid": [
            [0, 0, 1, 1, 1, 2, 2, 3, 3, 3],
            [4, 4, 1, 1, 1, 5, 5, 3, 3, 3],
            [4, 4, 6, 6, 6, 5, 5, 7, 7, 7],
            [4, 4, 6, 6, 6, 5, 5, 7, 7, 7],
            [8, 8, 8, 9, 9, 10, 10, 10, 11, 11],
            [8, 8, 8, 9, 9, 10, 10, 10, 11, 11],
            [12, 12, 12, 9, 9, 13, 13, 13, 11, 11],
            [12, 12, 12, 14, 14, 13, 13, 13, 15, 15],
        ],
        "clues": {3: 0, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 2, 10: 3, 11: 2, 12: 1},
        "shaded": [(0, 4), (1, 1), (1, 6), (2, 0), (2, 2), (2, 4), (2, 7), (2, 9), (3, 5), (3, 8), (4, 1), (4, 3), (4, 6), (5, 0), (5, 2), (5, 5), (5, 7), (5, 9), (6, 4), (6, 8), (7, 2), (7, 6)],
    },
    "hard": {
        "rows": 14, "cols": 24,
        "url_body": (
            "8i289289548ikkh2aiii9aaa959992951494k4okigl2ia2ka99ah9at155bk4kl8o"
            "007ofvvgc00007vv1vg000007vopvg0ec0vv00f01u00000vg1vvjvg0000000g"
            "32g3h3g3g3g3j52g4g21223h221425g32g01h311g0h3"
        ),
        "room_grid": [
            [0,0,1,1,1,1,2,2,2,3,3,3,3,3,4,4,4,5,5,5,5,5,6,6],
            [7,7,1,1,1,1,2,2,2,3,3,3,3,3,4,4,4,8,8,8,9,9,6,6],
            [7,7,10,10,10,10,11,11,11,11,12,12,12,13,13,14,14,8,8,8,9,9,15,15],
            [7,7,10,10,10,10,11,11,11,11,12,12,12,13,13,14,14,8,8,8,9,9,15,15],
            [16,16,17,17,18,18,18,19,19,19,20,20,20,13,13,14,14,21,21,21,22,22,23,23],
            [16,16,17,17,18,18,18,19,19,19,20,20,20,13,13,14,14,21,21,21,22,22,23,23],
            [16,16,17,17,18,18,18,24,24,24,24,25,25,25,26,26,26,21,21,21,27,27,23,23],
            [28,28,28,28,29,29,29,24,24,24,24,25,25,25,26,26,26,30,30,30,27,27,31,31],
            [28,28,28,28,29,29,29,32,33,33,33,33,34,34,35,35,35,30,30,30,27,27,31,31],
            [28,28,28,28,36,36,37,37,33,33,33,33,34,34,35,35,35,38,38,38,39,39,31,31],
            [28,28,28,28,36,36,37,37,33,33,33,33,34,34,35,35,35,38,38,38,39,39,31,31],
            [40,40,41,41,42,42,37,37,33,33,33,33,34,34,43,43,43,44,44,45,45,46,46,47],
            [48,49,41,41,50,50,50,50,50,51,51,51,34,34,43,43,43,44,44,45,45,46,46,47],
            [48,49,41,41,50,50,50,50,50,51,51,51,34,34,43,43,43,44,44,45,45,46,46,47],
        ],
        "clues": {
            1: 3, 2: 2, 4: 3, 7: 3, 9: 3, 11: 3, 13: 3, 18: 5,
            19: 2, 21: 4, 23: 2, 24: 1, 25: 2, 26: 2, 27: 3, 30: 2,
            31: 2, 32: 1, 33: 4, 34: 2, 35: 5, 37: 3, 38: 2,
            40: 0, 41: 1, 44: 3, 45: 1, 46: 1, 48: 0, 51: 3,
        },
        "shaded": [
            (0, 4), (0, 7), (0, 12), (0, 15), (0, 18),
            (1, 1), (1, 3), (1, 5), (1, 8), (1, 10), (1, 14), (1, 16), (1, 20), (1, 22),
            (2, 0), (2, 6), (2, 9), (2, 13), (2, 17), (2, 21),
            (3, 1), (3, 7), (3, 11), (3, 14), (3, 20),
            (4, 2), (4, 4), (4, 6), (4, 9), (4, 12), (4, 17), (4, 19), (4, 23),
            (5, 1), (5, 5), (5, 8), (5, 10), (5, 13), (5, 15), (5, 18), (5, 22),
            (6, 4), (6, 6), (6, 11), (6, 14), (6, 16), (6, 19), (6, 21),
            (7, 0), (7, 3), (7, 8), (7, 12), (7, 17), (7, 20), (7, 23),
            (8, 1), (8, 5), (8, 7), (8, 9), (8, 11), (8, 14), (8, 16), (8, 19), (8, 21),
            (9, 2), (9, 6), (9, 10), (9, 12), (9, 15), (9, 18), (9, 22),
            (10, 0), (10, 3), (10, 7), (10, 9), (10, 14), (10, 16), (10, 19),
            (11, 4), (11, 6), (11, 12), (11, 17), (11, 20),
            (12, 1), (12, 5), (12, 9), (12, 11), (12, 15), (12, 18), (12, 23),
            (13, 2), (13, 7), (13, 10), (13, 14), (13, 17), (13, 21),
        ],
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


def generate_puzzle_heyawake(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    moves_full, moves_required, moves_hint = _build_moves(rows, cols, p["shaded"])

    return {
        "puzzle_url": f"http://localhost:8000/p.html?heyawake/{cols}/{rows}/{p['url_body']}",
        "pid": "heyawake",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"http://localhost:8000/p.html?heyawake/{cols}/{rows}/{p['url_body']}",
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
            "num_rooms": len(set(c for row in p["room_grid"] for c in row)),
            "num_clued_rooms": len(p["clues"]),
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
        print(f"Usage: python puzzle_heyawake.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_heyawake(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}×{meta['db_h']}")
    print(f"Rooms: {meta['num_rooms']} ({meta['num_clued_rooms']} clued)")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
