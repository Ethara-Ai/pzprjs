import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 6, "cols": 6,
        "url_body": "17h71i1n0g1h0g51g5h1g1h",
        "num_clues": 9,
        "num_arrows": 4,
        "moves_required": [
            "mouse,left,10,0,10,2", "mouse,left,10,4,10,6",
            "mouse,left,10,8,10,10", "mouse,left,2,0,2,2",
            "mouse,left,2,0,4,0", "mouse,left,2,10,4,10",
            "mouse,left,2,2,4,2", "mouse,left,2,4,2,6",
            "mouse,left,2,4,4,4", "mouse,left,2,6,4,6",
            "mouse,left,2,8,2,10", "mouse,left,2,8,4,8",
            "mouse,left,4,0,6,0", "mouse,left,4,10,6,10",
            "mouse,left,4,2,4,4", "mouse,left,4,6,4,8",
            "mouse,left,6,0,8,0", "mouse,left,6,10,8,10",
            "mouse,left,8,0,10,0", "mouse,left,8,10,10,10",
            "mouse,left,8,2,10,2", "mouse,left,8,2,8,4",
            "mouse,left,8,4,10,4", "mouse,left,8,6,10,6",
            "mouse,left,8,6,8,8", "mouse,left,8,8,10,8",
        ],
        "moves_hint": [
            "mouse,left,0,0,0,2", "mouse,left,0,0,2,0",
            "mouse,left,0,10,0,12", "mouse,left,0,10,2,10",
            "mouse,left,0,12,2,12", "mouse,left,0,2,0,4",
            "mouse,left,0,2,2,2", "mouse,left,0,4,0,6",
            "mouse,left,0,4,2,4", "mouse,left,0,6,0,8",
            "mouse,left,0,6,2,6", "mouse,left,0,8,0,10",
            "mouse,left,0,8,2,8", "mouse,left,10,0,12,0",
            "mouse,left,10,10,10,12", "mouse,left,10,10,12,10",
            "mouse,left,10,12,12,12", "mouse,left,10,2,10,4",
            "mouse,left,10,2,12,2", "mouse,left,10,4,12,4",
            "mouse,left,10,6,10,8", "mouse,left,10,6,12,6",
            "mouse,left,10,8,12,8", "mouse,left,12,0,12,2",
            "mouse,left,12,10,12,12", "mouse,left,12,2,12,4",
            "mouse,left,12,4,12,6", "mouse,left,12,6,12,8",
            "mouse,left,12,8,12,10", "mouse,left,2,10,2,12",
            "mouse,left,2,12,4,12", "mouse,left,2,2,2,4",
            "mouse,left,2,6,2,8", "mouse,left,4,0,4,2",
            "mouse,left,4,10,4,12", "mouse,left,4,12,6,12",
            "mouse,left,4,2,6,2", "mouse,left,4,4,4,6",
            "mouse,left,4,4,6,4", "mouse,left,4,6,6,6",
            "mouse,left,4,8,4,10", "mouse,left,4,8,6,8",
            "mouse,left,6,0,6,2", "mouse,left,6,10,6,12",
            "mouse,left,6,12,8,12", "mouse,left,6,2,6,4",
            "mouse,left,6,2,8,2", "mouse,left,6,4,6,6",
            "mouse,left,6,4,8,4", "mouse,left,6,6,6,8",
            "mouse,left,6,6,8,6", "mouse,left,6,8,6,10",
            "mouse,left,6,8,8,8", "mouse,left,8,0,8,2",
            "mouse,left,8,10,8,12", "mouse,left,8,12,10,12",
            "mouse,left,8,4,8,6", "mouse,left,8,8,8,10",
        ],
    },
    "medium": {
        "rows": 7, "cols": 7,
        "url_body": "06g2g802k2h0g0h2k2h0g0h2k206g2g80",
        "num_clues": 20,
        "num_arrows": 4,
        "moves_required": [
            "mouse,left,4,0,4,2", "mouse,left,6,0,6,2",
            "mouse,left,8,0,8,2", "mouse,left,10,0,10,2",
            "mouse,left,2,2,2,4", "mouse,left,6,2,6,4",
            "mouse,left,8,2,8,4", "mouse,left,12,2,12,4",
            "mouse,left,0,4,0,6", "mouse,left,14,4,14,6",
            "mouse,left,4,6,4,8", "mouse,left,10,6,10,8",
            "mouse,left,0,8,0,10", "mouse,left,14,8,14,10",
            "mouse,left,2,10,2,12", "mouse,left,6,10,6,12",
            "mouse,left,8,10,8,12", "mouse,left,12,10,12,12",
            "mouse,left,4,12,4,14", "mouse,left,6,12,6,14",
            "mouse,left,8,12,8,14", "mouse,left,10,12,10,14",
            "mouse,left,4,0,6,0", "mouse,left,8,0,10,0",
            "mouse,left,2,2,4,2", "mouse,left,10,2,12,2",
            "mouse,left,0,4,2,4", "mouse,left,6,4,8,4",
            "mouse,left,12,4,14,4", "mouse,left,0,6,2,6",
            "mouse,left,2,6,4,6", "mouse,left,10,6,12,6",
            "mouse,left,12,6,14,6", "mouse,left,0,8,2,8",
            "mouse,left,2,8,4,8", "mouse,left,10,8,12,8",
            "mouse,left,12,8,14,8", "mouse,left,0,10,2,10",
            "mouse,left,6,10,8,10", "mouse,left,12,10,14,10",
            "mouse,left,2,12,4,12", "mouse,left,10,12,12,12",
            "mouse,left,4,14,6,14", "mouse,left,8,14,10,14",
        ],
        "moves_hint": [
            "mouse,left,0,0,0,2", "mouse,left,2,0,2,2",
            "mouse,left,12,0,12,2", "mouse,left,14,0,14,2",
            "mouse,left,0,2,0,4", "mouse,left,4,2,4,4",
            "mouse,left,10,2,10,4", "mouse,left,14,2,14,4",
            "mouse,left,2,4,2,6", "mouse,left,4,4,4,6",
            "mouse,left,6,4,6,6", "mouse,left,8,4,8,6",
            "mouse,left,10,4,10,6", "mouse,left,12,4,12,6",
            "mouse,left,0,6,0,8", "mouse,left,2,6,2,8",
            "mouse,left,6,6,6,8", "mouse,left,8,6,8,8",
            "mouse,left,12,6,12,8", "mouse,left,14,6,14,8",
            "mouse,left,2,8,2,10", "mouse,left,4,8,4,10",
            "mouse,left,6,8,6,10", "mouse,left,8,8,8,10",
            "mouse,left,10,8,10,10", "mouse,left,12,8,12,10",
            "mouse,left,0,10,0,12", "mouse,left,4,10,4,12",
            "mouse,left,10,10,10,12", "mouse,left,14,10,14,12",
            "mouse,left,0,12,0,14", "mouse,left,2,12,2,14",
            "mouse,left,12,12,12,14", "mouse,left,14,12,14,14",
            "mouse,left,0,0,2,0", "mouse,left,2,0,4,0",
            "mouse,left,6,0,8,0", "mouse,left,10,0,12,0",
            "mouse,left,12,0,14,0", "mouse,left,0,2,2,2",
            "mouse,left,4,2,6,2", "mouse,left,6,2,8,2",
            "mouse,left,8,2,10,2", "mouse,left,12,2,14,2",
            "mouse,left,2,4,4,4", "mouse,left,4,4,6,4",
            "mouse,left,8,4,10,4", "mouse,left,10,4,12,4",
            "mouse,left,4,6,6,6", "mouse,left,6,6,8,6",
            "mouse,left,8,6,10,6", "mouse,left,4,8,6,8",
            "mouse,left,6,8,8,8", "mouse,left,8,8,10,8",
            "mouse,left,2,10,4,10", "mouse,left,4,10,6,10",
            "mouse,left,8,10,10,10", "mouse,left,10,10,12,10",
            "mouse,left,0,12,2,12", "mouse,left,4,12,6,12",
            "mouse,left,6,12,8,12", "mouse,left,8,12,10,12",
            "mouse,left,12,12,14,12", "mouse,left,0,14,2,14",
            "mouse,left,2,14,4,14", "mouse,left,6,14,8,14",
            "mouse,left,10,14,12,14", "mouse,left,12,14,14,14",
        ],
    },
    "hard": {
        "rows": 8, "cols": 8,
        "url_body": "06j802h22h2h0h0i2j2h2j2i0h0h2h22h206j80",
        "num_clues": 24,
        "num_arrows": 4,
        "moves_required": [
            "mouse,left,4,0,4,2", "mouse,left,6,0,6,2",
            "mouse,left,10,0,10,2", "mouse,left,12,0,12,2",
            "mouse,left,2,2,2,4", "mouse,left,6,2,6,4",
            "mouse,left,10,2,10,4", "mouse,left,14,2,14,4",
            "mouse,left,0,4,0,6", "mouse,left,16,4,16,6",
            "mouse,left,4,6,4,8", "mouse,left,12,6,12,8",
            "mouse,left,4,8,4,10", "mouse,left,12,8,12,10",
            "mouse,left,0,10,0,12", "mouse,left,16,10,16,12",
            "mouse,left,2,12,2,14", "mouse,left,6,12,6,14",
            "mouse,left,10,12,10,14", "mouse,left,14,12,14,14",
            "mouse,left,4,14,4,16", "mouse,left,6,14,6,16",
            "mouse,left,10,14,10,16", "mouse,left,12,14,12,16",
            "mouse,left,4,0,6,0", "mouse,left,10,0,12,0",
            "mouse,left,2,2,4,2", "mouse,left,12,2,14,2",
            "mouse,left,0,4,2,4", "mouse,left,6,4,8,4",
            "mouse,left,8,4,10,4", "mouse,left,14,4,16,4",
            "mouse,left,0,6,2,6", "mouse,left,2,6,4,6",
            "mouse,left,12,6,14,6", "mouse,left,14,6,16,6",
            "mouse,left,0,10,2,10", "mouse,left,2,10,4,10",
            "mouse,left,12,10,14,10", "mouse,left,14,10,16,10",
            "mouse,left,0,12,2,12", "mouse,left,6,12,8,12",
            "mouse,left,8,12,10,12", "mouse,left,14,12,16,12",
            "mouse,left,2,14,4,14", "mouse,left,12,14,14,14",
            "mouse,left,4,16,6,16", "mouse,left,10,16,12,16",
        ],
        "moves_hint": [
            "mouse,left,0,0,0,2", "mouse,left,2,0,2,2",
            "mouse,left,8,0,8,2", "mouse,left,14,0,14,2",
            "mouse,left,16,0,16,2", "mouse,left,0,2,0,4",
            "mouse,left,4,2,4,4", "mouse,left,8,2,8,4",
            "mouse,left,12,2,12,4", "mouse,left,16,2,16,4",
            "mouse,left,2,4,2,6", "mouse,left,4,4,4,6",
            "mouse,left,6,4,6,6", "mouse,left,8,4,8,6",
            "mouse,left,10,4,10,6", "mouse,left,12,4,12,6",
            "mouse,left,14,4,14,6", "mouse,left,0,6,0,8",
            "mouse,left,2,6,2,8", "mouse,left,6,6,6,8",
            "mouse,left,8,6,8,8", "mouse,left,10,6,10,8",
            "mouse,left,14,6,14,8", "mouse,left,16,6,16,8",
            "mouse,left,0,8,0,10", "mouse,left,2,8,2,10",
            "mouse,left,6,8,6,10", "mouse,left,8,8,8,10",
            "mouse,left,10,8,10,10", "mouse,left,14,8,14,10",
            "mouse,left,16,8,16,10", "mouse,left,2,10,2,12",
            "mouse,left,4,10,4,12", "mouse,left,6,10,6,12",
            "mouse,left,8,10,8,12", "mouse,left,10,10,10,12",
            "mouse,left,12,10,12,12", "mouse,left,14,10,14,12",
            "mouse,left,0,12,0,14", "mouse,left,4,12,4,14",
            "mouse,left,8,12,8,14", "mouse,left,12,12,12,14",
            "mouse,left,16,12,16,14", "mouse,left,0,14,0,16",
            "mouse,left,2,14,2,16", "mouse,left,8,14,8,16",
            "mouse,left,14,14,14,16", "mouse,left,16,14,16,16",
            "mouse,left,0,0,2,0", "mouse,left,2,0,4,0",
            "mouse,left,6,0,8,0", "mouse,left,8,0,10,0",
            "mouse,left,12,0,14,0", "mouse,left,14,0,16,0",
            "mouse,left,0,2,2,2", "mouse,left,4,2,6,2",
            "mouse,left,6,2,8,2", "mouse,left,8,2,10,2",
            "mouse,left,10,2,12,2", "mouse,left,14,2,16,2",
            "mouse,left,2,4,4,4", "mouse,left,4,4,6,4",
            "mouse,left,10,4,12,4", "mouse,left,12,4,14,4",
            "mouse,left,4,6,6,6", "mouse,left,6,6,8,6",
            "mouse,left,8,6,10,6", "mouse,left,10,6,12,6",
            "mouse,left,0,8,2,8", "mouse,left,2,8,4,8",
            "mouse,left,4,8,6,8", "mouse,left,6,8,8,8",
            "mouse,left,8,8,10,8", "mouse,left,10,8,12,8",
            "mouse,left,12,8,14,8", "mouse,left,14,8,16,8",
            "mouse,left,4,10,6,10", "mouse,left,6,10,8,10",
            "mouse,left,8,10,10,10", "mouse,left,10,10,12,10",
            "mouse,left,2,12,4,12", "mouse,left,4,12,6,12",
            "mouse,left,10,12,12,12", "mouse,left,12,12,14,12",
            "mouse,left,0,14,2,14", "mouse,left,4,14,6,14",
            "mouse,left,6,14,8,14", "mouse,left,8,14,10,14",
            "mouse,left,10,14,12,14", "mouse,left,14,14,16,14",
            "mouse,left,0,16,2,16", "mouse,left,2,16,4,16",
            "mouse,left,6,16,8,16", "mouse,left,8,16,10,16",
            "mouse,left,12,16,14,16", "mouse,left,14,16,16,16",
        ],
    },
}

_PID = "pairloop"


def generate_puzzle_pairloop(difficulty="easy"):
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
            "num_arrows": p["num_arrows"],
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
        print(f"Usage: python puzzle_pairloop.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_pairloop(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}x{meta['db_h']}")
    print(f"Clues: {meta['num_clues']} ({meta['num_arrows']} arrows)")
    print(f"Required moves: {puzzle_data['number_required_moves']}")
    print(f"Total moves: {puzzle_data['number_total_solution_moves']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
