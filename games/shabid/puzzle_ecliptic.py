import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        # 6x6 grid, 2 shaded per row/col
        # Clues: (r0,c2)=2, (r0,c4)=0, (r1,c5)=0, (r2,c0)=1, (r3,c0)=1, (r3,c5)=1, (r4,c0)=0, (r5,c2)=1
        # Solution shaded: r0:{c0,c1}, r1:{c0,c2}, r2:{c3,c4}, r3:{c1,c3}, r4:{c2,c5}, r5:{c4,c5}
        "rows": 6,
        "cols": 6,
        "url_body": "h2g0l01k1j10m1i",
        "num_clues": 8,
        "shaded_per_line": 2,
        "moves_required": [
            "mouse,left,1,1",  # r0c0
            "mouse,left,3,1",  # r0c1
            "mouse,left,1,3",  # r1c0
            "mouse,left,5,3",  # r1c2
        ],
        "moves_hint": [
            "mouse,left,7,5",  # r2c3
            "mouse,left,9,5",  # r2c4
            "mouse,left,3,7",  # r3c1
            "mouse,left,7,7",  # r3c3
            "mouse,left,5,9",  # r4c2
            "mouse,left,11,9",  # r4c5
            "mouse,left,9,11",  # r5c4
            "mouse,left,11,11",  # r5c5
        ],
    },
    "medium": {
        # 8x8 grid, 3 shaded per row/col (unique solution, verified by cspuz)
        # Solution shaded: r0:{c0,c1,c2}, r1:{c0,c2,c3}, r2:{c0,c2,c5},
        #   r3:{c4,c5,c6}, r4:{c1,c3,c4}, r5:{c1,c6,c7}, r6:{c3,c4,c7}, r7:{c5,c6,c7}
        # Clues (20): (r0,c3)=2, (r0,c4)=0, (r0,c5)=0, (r0,c6)=0, (r0,c7)=0,
        #   (r1,c1)=3, (r1,c4)=1, (r1,c5)=1, (r1,c6)=0, (r1,c7)=0,
        #   (r2,c4)=2, (r3,c0)=1, (r3,c1)=1, (r5,c0)=1, (r5,c5)=1,
        #   (r6,c1)=1, (r6,c6)=3, (r7,c0)=0, (r7,c1)=0, (r7,c3)=1
        "rows": 8,
        "cols": 8,
        "url_body": "i20000g3h1100j2i11t1j1i1j3g00g1",
        "num_clues": 20,
        "shaded_per_line": 3,
        "moves_required": [
            "mouse,left,1,1",  # r0c0
            "mouse,left,3,1",  # r0c1
            "mouse,left,5,1",  # r0c2
            "mouse,left,1,3",  # r1c0
            "mouse,left,5,3",  # r1c2
            "mouse,left,7,3",  # r1c3
            "mouse,left,1,5",  # r2c0
            "mouse,left,5,5",  # r2c2
            "mouse,left,11,5",  # r2c5
            "mouse,left,9,7",  # r3c4
            "mouse,left,11,7",  # r3c5
            "mouse,left,13,7",  # r3c6
        ],
        "moves_hint": [
            "mouse,left,3,9",  # r4c1
            "mouse,left,7,9",  # r4c3
            "mouse,left,9,9",  # r4c4
            "mouse,left,3,11",  # r5c1
            "mouse,left,13,11",  # r5c6
            "mouse,left,15,11",  # r5c7
            "mouse,left,7,13",  # r6c3
            "mouse,left,9,13",  # r6c4
            "mouse,left,15,13",  # r6c7
            "mouse,left,11,15",  # r7c5
            "mouse,left,13,15",  # r7c6
            "mouse,left,15,15",  # r7c7
        ],
    },
    "hard": {
        # 10x10 grid, 3 shaded per row/col (unique solution, verified by cspuz)
        # Solution shaded: r0:{c1,c3,c4}, r1:{c4,c6,c9}, r2:{c0,c5,c7},
        #   r3:{c2,c7,c8}, r4:{c2,c3,c5}, r5:{c0,c6,c8}, r6:{c0,c4,c7},
        #   r7:{c3,c5,c8}, r8:{c1,c6,c9}, r9:{c1,c2,c9}
        # Clues (17): (r0,c2)=2, (r0,c5)=1, (r0,c9)=1, (r1,c0)=1, (r1,c5)=3,
        #   (r1,c7)=2, (r2,c3)=0, (r2,c8)=2, (r3,c1)=1, (r4,c0)=1,
        #   (r5,c2)=1, (r5,c7)=3, (r6,c1)=1, (r6,c3)=2, (r6,c5)=2,
        #   (r6,c8)=3, (r7,c2)=1
        "rows": 10,
        "cols": 10,
        "url_body": "h2h1i11j3g2k0j2h1n1q1j3i1g2g2h3i1",
        "num_clues": 17,
        "shaded_per_line": 3,
        "moves_required": [
            "mouse,left,3,1",  # r0c1
            "mouse,left,7,1",  # r0c3
            "mouse,left,9,1",  # r0c4
            "mouse,left,9,3",  # r1c4
            "mouse,left,13,3",  # r1c6
            "mouse,left,19,3",  # r1c9
            "mouse,left,1,5",  # r2c0
            "mouse,left,11,5",  # r2c5
            "mouse,left,15,5",  # r2c7
            "mouse,left,5,7",  # r3c2
            "mouse,left,15,7",  # r3c7
            "mouse,left,17,7",  # r3c8
            "mouse,left,5,9",  # r4c2
            "mouse,left,7,9",  # r4c3
            "mouse,left,11,9",  # r4c5
        ],
        "moves_hint": [
            "mouse,left,1,11",  # r5c0
            "mouse,left,13,11",  # r5c6
            "mouse,left,17,11",  # r5c8
            "mouse,left,1,13",  # r6c0
            "mouse,left,9,13",  # r6c4
            "mouse,left,15,13",  # r6c7
            "mouse,left,7,15",  # r7c3
            "mouse,left,11,15",  # r7c5
            "mouse,left,17,15",  # r7c8
            "mouse,left,3,17",  # r8c1
            "mouse,left,13,17",  # r8c6
            "mouse,left,19,17",  # r8c9
            "mouse,left,3,19",  # r9c1
            "mouse,left,5,19",  # r9c2
            "mouse,left,19,19",  # r9c9
        ],
    },
}

_PID = "ecliptic"


def generate_puzzle_ecliptic(difficulty="easy"):
    p = _PUZZLES[difficulty]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    mr = p["moves_required"]
    mh = p["moves_hint"]
    mf = mr + mh

    return {
        "puzzle_url": f"http://localhost:8000/p.html?{_PID}/{cols}/{rows}/{p['url_body']}",
        "pid": _PID,
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(mr),
        "number_total_solution_moves": len(mf),
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
            "level": difficulty,
            "num_clues": p["num_clues"],
            "shaded_per_line": p["shaded_per_line"],
        },
        "created_at": now,
        "solution": {
            "moves_full": mf,
            "moves_required": mr,
            "moves_hint": mh,
        },
    }


if __name__ == "__main__":
    import json

    level = sys.argv[1] if len(sys.argv) > 1 else "easy"
    if level not in _PUZZLES:
        print(f"Usage: python puzzle_ecliptic.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_ecliptic(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}x{meta['db_h']}")
    print(f"Clues: {meta['num_clues']}")
    print(f"Shaded per row/col: {meta['shaded_per_line']}")
    print(f"Required moves: {puzzle_data['number_required_moves']}")
    print(f"Total moves: {puzzle_data['number_total_solution_moves']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
