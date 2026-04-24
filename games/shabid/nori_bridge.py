import sys
import time
import json
from datetime import datetime, timezone

_EASY = {
    "rows": 6,
    "cols": 6,
    "room_grid": [
        [0, 0, 1, 1, 2, 2],
        [0, 0, 1, 1, 2, 2],
        [3, 3, 4, 4, 5, 5],
        [3, 3, 4, 4, 5, 5],
        [3, 3, 4, 4, 5, 5],
        [3, 3, 4, 4, 5, 5],
    ],
    "region_numbers": {0: 2, 1: 3, 2: 2, 3: 1, 4: 1, 5: 1},
    "bridges": [(0, 1), (1, 2), (0, 3), (1, 4), (2, 5)],
}

_MEDIUM = {
    "rows": 8,
    "cols": 8,
    "room_grid": [
        [0, 0, 1, 1, 2, 2, 3, 3],
        [0, 0, 1, 1, 2, 2, 3, 3],
        [0, 0, 1, 1, 2, 2, 3, 3],
        [0, 0, 1, 1, 2, 2, 3, 3],
        [4, 4, 5, 5, 6, 6, 7, 7],
        [4, 4, 5, 5, 6, 6, 7, 7],
        [4, 4, 5, 5, 6, 6, 7, 7],
        [4, 4, 5, 5, 6, 6, 7, 7],
    ],
    "region_numbers": {1: 3, 2: 3, 4: 1, 5: 1, 6: 1, 7: 1},
    "bridges": [
        (0, 1), (0, 4), (1, 2), (1, 5),
        (2, 3), (2, 6), (3, 7),
    ],
}

_HARD = {
    "rows": 10,
    "cols": 10,
    "room_grid": [
        [ 0,  0,  1,  1,  2,  2,  3,  3,  3,  3],
        [ 0,  0,  1,  1,  2,  2,  3,  3,  3,  3],
        [ 4,  4,  5,  5,  6,  6,  7,  7,  7,  7],
        [ 4,  4,  5,  5,  6,  6,  7,  7,  7,  7],
        [ 8,  8,  9,  9, 10, 10, 11, 11, 11, 11],
        [ 8,  8,  9,  9, 10, 10, 11, 11, 11, 11],
        [12, 12, 13, 13, 14, 14, 15, 15, 15, 15],
        [12, 12, 13, 13, 14, 14, 15, 15, 15, 15],
        [12, 12, 13, 13, 14, 14, 15, 15, 15, 15],
        [12, 12, 13, 13, 14, 14, 15, 15, 15, 15],
    ],
    "region_numbers": {1: 3, 2: 3, 12: 1, 13: 1, 14: 1, 15: 1},
    "bridges": [
        (0, 1), (1, 2), (2, 3),
        (0, 4), (1, 5), (2, 6), (3, 7),
        (4, 8), (5, 9), (6, 10), (7, 11),
        (8, 12), (9, 13), (10, 14), (11, 15),
    ],
}

_PUZZLES = {"easy": _EASY, "medium": _MEDIUM, "hard": _HARD}

def _encode_border(room_grid, rows, cols):
    """Encode region borders as a base-32 string (pzprjs encodeBorder).

    cspuz Rooms deserializer decodes vertical and horizontal border arrays
    separately, each padded to a multiple of 5 bits. So we must encode them
    as two independent base-32 segments concatenated together.
    """
    def _bits_to_base32(bits):
        encoded = ""
        for i in range(0, len(bits), 5):
            val = 0
            for j in range(5):
                if i + j < len(bits):
                    val += bits[i + j] * [16, 8, 4, 2, 1][j]
            if val < 10:
                encoded += str(val)
            else:
                encoded += chr(ord('a') + val - 10)
        return encoded

    vert_bits = []
    for r in range(rows):
        for c in range(cols - 1):
            vert_bits.append(1 if room_grid[r][c] != room_grid[r][c + 1] else 0)

    horiz_bits = []
    for r in range(rows - 1):
        for c in range(cols):
            horiz_bits.append(1 if room_grid[r][c] != room_grid[r + 1][c] else 0)

    return _bits_to_base32(vert_bits) + _bits_to_base32(horiz_bits)

def _find_border_segments(room_grid, rows, cols):
    segments = []
    for r in range(rows):
        for c in range(cols - 1):
            ra, rb = room_grid[r][c], room_grid[r][c + 1]
            if ra != rb:
                bx = 2 + c * 2
                by = 1 + r * 2
                segments.append((bx, by, min(ra, rb), max(ra, rb)))
    # Horizontal borders: between cell(r,c) and cell(r+1,c)
    for r in range(rows - 1):
        for c in range(cols):
            ra, rb = room_grid[r][c], room_grid[r + 1][c]
            if ra != rb:
                bx = 1 + c * 2
                by = 2 + r * 2
                segments.append((bx, by, min(ra, rb), max(ra, rb)))
    return segments

def _bridge_to_border(border_segments, bridges):
    mapping = {}
    for bx, by, ra, rb in border_segments:
        pair = (min(ra, rb), max(ra, rb))
        if pair not in mapping:
            mapping[pair] = (bx, by)
    result = {}
    for a, b in bridges:
        pair = (min(a, b), max(a, b))
        result[pair] = mapping[pair]
    return result

def _build_moves(border_segments, bridges):
    bridge_set = set()
    for a, b in bridges:
        bridge_set.add((min(a, b), max(a, b)))
    bridge_positions = _bridge_to_border(border_segments, bridges)
    bridged_positions = set(bridge_positions.values())

    full, req, hint = [], [], []

    for bx, by, ra, rb in border_segments:
        pair = (min(ra, rb), max(ra, rb))
        if pair in bridge_set and (bx, by) == bridge_positions[pair]:
            m = f"mouse,left,{bx},{by}"
            full.append(m)
            req.append(m)
        else:
            m = f"mouse,right,{bx},{by}"
            full.append(m)
            hint.append(m)

    return full, req, hint

def _verify(room_grid, region_numbers, bridges, rows, cols):
    """Verify all 4 Nori Bridges rules. Raises AssertionError on failure."""
    border_segments = _find_border_segments(room_grid, rows, cols)
    valid_pairs = set()
    for _, _, ra, rb in border_segments:
        valid_pairs.add((min(ra, rb), max(ra, rb)))

    all_regions = set()
    for r in range(rows):
        for c in range(cols):
            all_regions.add(room_grid[r][c])

    bridge_pairs = []
    for a, b in bridges:
        pair = (min(a, b), max(a, b))
        assert pair[0] != pair[1], f"Bridge {a}-{b} connects same region"
        assert pair in valid_pairs, f"Bridge {a}-{b} has no shared border"
        bridge_pairs.append(pair)

    assert len(bridge_pairs) == len(set(bridge_pairs)), "Duplicate bridges"

    adj = {reg: set() for reg in all_regions}
    for a, b in bridges:
        adj[a].add(b)
        adj[b].add(a)
    start = next(iter(all_regions))
    visited = set()
    queue = [start]
    while queue:
        node = queue.pop()
        if node in visited:
            continue
        visited.add(node)
        for nb in adj[node]:
            if nb not in visited:
                queue.append(nb)
    assert visited == all_regions, (
        f"Not all regions connected: reached {visited}, missing {all_regions - visited}"
    )

    degree = {reg: 0 for reg in all_regions}
    for a, b in bridges:
        degree[a] += 1
        degree[b] += 1
    for reg, expected in region_numbers.items():
        assert degree[reg] == expected, (
            f"Region {reg}: expected degree {expected}, got {degree[reg]}"
        )

def generate_puzzle(difficulty):
    puzzle = _PUZZLES[difficulty]
    rows = puzzle["rows"]
    cols = puzzle["cols"]
    room_grid = puzzle["room_grid"]
    region_numbers = puzzle["region_numbers"]
    bridges = puzzle["bridges"]

    _verify(room_grid, region_numbers, bridges, rows, cols)

    url_body = _encode_border(room_grid, rows, cols)
    border_segments = _find_border_segments(room_grid, rows, cols)
    full, req, hint = _build_moves(border_segments, bridges)
    now = datetime.now(timezone.utc).isoformat()

    all_regions = set()
    for r in range(rows):
        for c in range(cols):
            all_regions.add(room_grid[r][c])
    num_regions = len(all_regions)

    return {
        "puzzle_url": f"http://localhost:8000/p.html?norinori/{cols}/{rows}/{url_body}",
        "pid": "norinori",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(bridges),
        "number_total_solution_moves": len(border_segments),
        "puzzlink_url": f"http://localhost:8000/p.html?norinori/{cols}/{rows}/{url_body}",
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": True,
            "cspuz_is_unique": False,
            "db_w": cols,
            "db_h": rows,
            "num_regions": num_regions,
            "num_numbered_regions": len(region_numbers),
            "num_bridges": len(bridges),
            "custom_rules": [
                "bridge_placement",
                "connected_graph",
                "degree_match",
                "single_bridge_per_border",
            ],
        },
        "created_at": now,
        "solution": {
            "moves_full": full,
            "moves_required": req,
            "moves_hint": hint,
        },
    }


if __name__ == "__main__":
    level = sys.argv[1] if len(sys.argv) > 1 else "easy"
    levels = ["easy", "medium", "hard"] if level == "all" else [level]

    t0 = time.monotonic()
    results = []
    for lv in levels:
        data = generate_puzzle(lv)
        results.append((lv, data))

    elapsed = time.monotonic() - t0

    for lv, data in results:
        print(json.dumps(data, indent=2, default=str))

        meta = data["metadata"]
        w, h = data["width"], data["height"]
        print(f"\nGrid: {w}x{h}")
        print(f"Regions: {meta['num_regions']} ({meta['num_numbered_regions']} numbered)")
        print(f"Bridges: {meta['num_bridges']}")
        print(f"Generated in {elapsed:.4f}s")
        print(f"\nPlay: {data['puzzlink_url']}")
        print()