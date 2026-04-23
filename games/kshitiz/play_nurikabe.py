import sys
import time
from collections import deque
from datetime import datetime, timezone


_PUZZLES = {
    "easy": {
        "rows": 5,
        "cols": 5,
        "url_body": "h2l22n1h3",
    },
    "medium": {
        "rows": 6,
        "cols": 6,
        "url_body": "2h1g2m3h1m1h3m2",
    },
    "hard": {
        "rows": 7,
        "cols": 7,
        "url_body": "2h1g2n1g2h1n2h1g2n1g2h1",
    },
}

_DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]


def _decode_number16(url_body, rows, cols):
    grid = [[-1] * cols for _ in range(rows)]
    pos = 0
    i = 0
    total = rows * cols
    while i < len(url_body) and pos < total:
        ch = url_body[i]
        if ch == '.':
            pos += 1
        elif ch == '-':
            val = int(url_body[i + 1:i + 3], 16)
            r, c = divmod(pos, cols)
            grid[r][c] = val
            pos += 1
            i += 2
        elif ch == '+':
            val = int(url_body[i + 1:i + 4], 16)
            r, c = divmod(pos, cols)
            grid[r][c] = val
            pos += 1
            i += 3
        elif 'g' <= ch <= 'z':
            gap = ord(ch) - ord('g') + 1
            pos += gap
        else:
            val = int(ch, 16)
            r, c = divmod(pos, cols)
            grid[r][c] = val
            pos += 1
        i += 1
    return grid


def _gen_polyominoes(r0, c0, n, rows, cols):
    if n == 1:
        return [frozenset([(r0, c0)])]
    results = set()

    def _expand(cells, border):
        if len(cells) == n:
            results.add(cells)
            return
        for (r, c) in sorted(border):
            new_cells = cells | frozenset([(r, c)])
            new_border = set(border)
            new_border.discard((r, c))
            for dr, dc in _DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in new_cells:
                    new_border.add((nr, nc))
            _expand(new_cells, frozenset(new_border))

    border_set = set()
    for dr, dc in _DIRS:
        nr, nc = r0 + dr, c0 + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            border_set.add((nr, nc))
    _expand(frozenset([(r0, c0)]), frozenset(border_set))
    return list(results)


def _solve_nurikabe(grid, rows, cols):
    clues = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] > 0:
                clues.append((r, c, grid[r][c]))

    options = []
    for r, c, n in clues:
        polys = _gen_polyominoes(r, c, n, rows, cols)
        options.append(polys)

    if any(len(o) == 0 for o in options):
        return None

    indices = sorted(range(len(clues)), key=lambda i: len(options[i]))
    cell_owner = {}
    chosen = [None] * len(clues)

    def _neighbors(r, c):
        for dr, dc in _DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                yield nr, nc

    def _island_adj_conflict(poly, idx):
        for r, c in poly:
            for nr, nc in _neighbors(r, c):
                if (nr, nc) in cell_owner and cell_owner[(nr, nc)] != idx and (nr, nc) not in poly:
                    return True
        return False

    def _has_2x2_shaded():
        all_island = set(cell_owner.keys())
        for r in range(rows - 1):
            for c in range(cols - 1):
                if ((r, c) not in all_island
                        and (r, c + 1) not in all_island
                        and (r + 1, c) not in all_island
                        and (r + 1, c + 1) not in all_island):
                    return True
        return False

    def _shaded_connected():
        all_island = set(cell_owner.keys())
        shaded = []
        for r in range(rows):
            for c in range(cols):
                if (r, c) not in all_island:
                    shaded.append((r, c))
        if len(shaded) <= 1:
            return True
        shaded_set = set(shaded)
        visited = {shaded[0]}
        queue = deque([shaded[0]])
        while queue:
            cr, cc = queue.popleft()
            for nr, nc in _neighbors(cr, cc):
                if (nr, nc) in shaded_set and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
        return len(visited) == len(shaded)

    def _backtrack(order_idx):
        if order_idx == len(clues):
            if _has_2x2_shaded():
                return False
            if not _shaded_connected():
                return False
            return True
        idx = indices[order_idx]
        for poly in options[idx]:
            if any(c in cell_owner for c in poly):
                continue
            if _island_adj_conflict(poly, idx):
                continue
            chosen[idx] = poly
            for c in poly:
                cell_owner[c] = idx
            if _backtrack(order_idx + 1):
                return True
            for c in poly:
                del cell_owner[c]
            chosen[idx] = None
        return False

    if not _backtrack(0):
        return None

    solution = [[1] * cols for _ in range(rows)]
    for cells in chosen:
        for r, c in cells:
            solution[r][c] = 0
    return solution


def _build_moves(rows, cols, grid, solution):
    moves_full = []
    moves_required = []
    moves_hint = []

    for r in range(rows):
        for c in range(cols):
            x = 1 + c * 2
            y = 1 + r * 2
            if solution[r][c] == 1:
                move = f"mouse,left,{x},{y}"
                moves_full.append(move)
                moves_required.append(move)
            else:
                if grid[r][c] <= 0:
                    move = f"mouse,right,{x},{y}"
                    moves_full.append(move)
                    moves_hint.append(move)

    return moves_full, moves_required, moves_hint


def generate_custom_nurikabe(difficulty="easy"):
    p = _PUZZLES[difficulty]
    rows, cols, url_body = p["rows"], p["cols"], p["url_body"]
    grid = _decode_number16(url_body, rows, cols)
    now = datetime.now(timezone.utc).isoformat()

    num_clues = sum(1 for r in range(rows) for c in range(cols) if grid[r][c] > 0)

    solution = _solve_nurikabe(grid, rows, cols)
    if solution is not None:
        moves_full, moves_required, moves_hint = _build_moves(
            rows, cols, grid, solution,
        )
        has_solution = True
    else:
        moves_full, moves_required, moves_hint = [], [], []
        has_solution = False

    return {
        "puzzle_url": f"http://pzv.jp/p.html?nurikabe/{cols}/{rows}/{url_body}",
        "pid": "nurikabe",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"https://puzz.link/p?nurikabe/{cols}/{rows}/{url_body}",
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": has_solution,
            "cspuz_is_unique": None,
            "db_w": cols,
            "db_h": rows,
            "num_island_clues": num_clues,
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

    difficulty = sys.argv[1].lower() if len(sys.argv) > 1 else "easy"
    if difficulty not in _PUZZLES:
        print(f"Unknown difficulty: {difficulty}")
        print(f"Available: {', '.join(_PUZZLES)}")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_custom_nurikabe(difficulty)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))

    meta = puzzle_data["metadata"]
    print(f"\nGrid: {puzzle_data['width']}x{puzzle_data['height']}")
    print(f"Island clues: {meta['num_island_clues']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
