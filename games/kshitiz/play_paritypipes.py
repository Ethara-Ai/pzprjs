import sys
import time
from datetime import datetime, timezone


_PUZZLES = {
    "easy": {
        "rows": 6,
        "cols": 6,
        "url_body": "07fauss700",
    },
    "medium": {
        "rows": 8,
        "cols": 8,
        "url_body": "uv57ros1oe0lpqg70",
    },
    "hard": {
        "rows": 10,
        "cols": 10,
        "url_body": "toak7e0s0fr0lgeo1oetl0rg0",
    },
}


def _decode_parity(url_body, rows, cols):
    num_crosses = (rows + 1) * (cols + 1)
    colors = []
    for ch in url_body:
        val = int(ch, 32)
        for bit in range(4, -1, -1):
            if len(colors) >= num_crosses:
                break
            b = (val >> bit) & 1
            colors.append(1 if b == 1 else 2)
    grid = []
    idx = 0
    for r in range(rows + 1):
        row = []
        for c in range(cols + 1):
            row.append(colors[idx] if idx < len(colors) else 2)
            idx += 1
        grid.append(row)
    return grid


def _solve_paritypipes(vertex_grid, rows, cols):
    h_edges = [[0] * cols for _ in range(rows + 1)]
    v_edges = [[0] * (cols + 1) for _ in range(rows)]

    black_verts = set()
    for r in range(rows + 1):
        for c in range(cols + 1):
            if vertex_grid[r][c] == 1:
                black_verts.add((r, c))

    search_edges = []
    for r in range(rows + 1):
        for c in range(cols):
            if (r, c) in black_verts and (r, c + 1) in black_verts:
                search_edges.append(("h", r, c))
    for r in range(rows):
        for c in range(cols + 1):
            if (r, c) in black_verts and (r + 1, c) in black_verts:
                search_edges.append(("v", r, c))

    black_list = list(black_verts)

    edge_to_idx = {}
    for i, (kind, r, c) in enumerate(search_edges):
        edge_to_idx[(kind, r, c)] = i

    vert_edges = {v: [] for v in black_verts}
    for i, (kind, r, c) in enumerate(search_edges):
        if kind == "h":
            vert_edges[(r, c)].append(i)
            vert_edges[(r, c + 1)].append(i)
        else:
            vert_edges[(r, c)].append(i)
            vert_edges[(r + 1, c)].append(i)

    def set_edge(kind, r, c, val):
        if kind == "h":
            h_edges[r][c] = val
        else:
            v_edges[r][c] = val

    def vertex_lcnt(vr, vc):
        cnt = 0
        if vc > 0 and h_edges[vr][vc - 1] == 1:
            cnt += 1
        if vc < cols and h_edges[vr][vc] == 1:
            cnt += 1
        if vr > 0 and v_edges[vr - 1][vc] == 1:
            cnt += 1
        if vr < rows and v_edges[vr][vc] == 1:
            cnt += 1
        return cnt

    def edge_endpoints(kind, r, c):
        if kind == "h":
            return (r, c), (r, c + 1)
        return (r, c), (r + 1, c)

    def check_vertex(vr, vc, edge_idx):
        lcnt = vertex_lcnt(vr, vc)
        if lcnt > 2:
            return False
        remaining = sum(1 for j in vert_edges[(vr, vc)] if j > edge_idx)
        if lcnt + remaining < 2:
            return False
        return True

    def check_loops():
        adj = {}
        for r in range(rows + 1):
            for c in range(cols):
                if h_edges[r][c] == 1:
                    a, b = (r, c), (r, c + 1)
                    adj.setdefault(a, []).append(b)
                    adj.setdefault(b, []).append(a)
        for r in range(rows):
            for c in range(cols + 1):
                if v_edges[r][c] == 1:
                    a, b = (r, c), (r + 1, c)
                    adj.setdefault(a, []).append(b)
                    adj.setdefault(b, []).append(a)
        if not adj:
            return False
        for nbrs in adj.values():
            if len(nbrs) != 2:
                return False
        visited = set()
        for start in adj:
            if start in visited:
                continue
            stack = [start]
            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                for nb in adj[node]:
                    if nb not in visited:
                        stack.append(nb)
        return True

    def solve(idx):
        if idx == len(search_edges):
            for vr, vc in black_list:
                if vertex_lcnt(vr, vc) != 2:
                    return False
            return check_loops()

        kind, r, c = search_edges[idx]
        v1, v2 = edge_endpoints(kind, r, c)

        for val in (1, 0):
            set_edge(kind, r, c, val)
            ok = True
            for vr, vc in (v1, v2):
                if not check_vertex(vr, vc, idx):
                    ok = False
                    break
            if ok and solve(idx + 1):
                return True
            set_edge(kind, r, c, 0)

        return False

    if solve(0):
        return h_edges, v_edges
    return None


def _build_moves(rows, cols, h_edges, v_edges):
    moves = []
    for r in range(rows + 1):
        for c in range(cols):
            if h_edges[r][c] == 1:
                bx = 1 + c * 2
                by = r * 2
                moves.append(f"mouse,left,{bx},{by}")
    for r in range(rows):
        for c in range(cols + 1):
            if v_edges[r][c] == 1:
                bx = c * 2
                by = 1 + r * 2
                moves.append(f"mouse,left,{bx},{by}")
    return {
        "moves_full": moves,
        "moves_required": list(moves),
        "moves_hint": [],
    }


def generate_custom_paritypipes(difficulty="easy"):
    p = _PUZZLES[difficulty]
    rows, cols, url_body = p["rows"], p["cols"], p["url_body"]
    vertex_grid = _decode_parity(url_body, rows, cols)
    now = datetime.now(timezone.utc).isoformat()

    num_crosses = (rows + 1) * (cols + 1)
    num_black = sum(
        1
        for r in range(rows + 1)
        for c in range(cols + 1)
        if vertex_grid[r][c] == 1
    )

    result = _solve_paritypipes(vertex_grid, rows, cols)
    has_solution = result is not None
    if has_solution:
        h_edges, v_edges = result
        moves = _build_moves(rows, cols, h_edges, v_edges)
    else:
        moves = {"moves_full": [], "moves_required": [], "moves_hint": []}

    return {
        "puzzle_url": f"http://localhost:8000/p.html?paritypipes/{cols}/{rows}/{url_body}",
        "pid": "paritypipes",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves["moves_required"]),
        "number_total_solution_moves": len(moves["moves_full"]),
        "puzzlink_url": f"http://localhost:8000/p.html?paritypipes/{cols}/{rows}/{url_body}",
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
            "num_crosses": num_crosses,
            "num_black_vertices": num_black,
            "modified_rules": [
                "closed loops on grid edges",
                "black vertex = loop passes through (exactly 2 edges)",
                "white vertex = loop skips (exactly 0 edges)",
            ],
        },
        "created_at": now,
        "solution": moves,
    }


if __name__ == "__main__":
    import json

    difficulty = sys.argv[1].lower() if len(sys.argv) > 1 else "easy"
    if difficulty not in _PUZZLES:
        print(f"Unknown difficulty: {difficulty}")
        print(f"Available: {', '.join(_PUZZLES)}")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_custom_paritypipes(difficulty)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))

    meta = puzzle_data["metadata"]
    print(f"\nGrid: {puzzle_data['width']}x{puzzle_data['height']}")
    print(f"Crosses: {meta['num_crosses']} ({meta['num_black_vertices']} black)")
    print(f"Solution found: {meta['has_structured_solution']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
