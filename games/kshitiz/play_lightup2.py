import sys
import time
from datetime import datetime, timezone


_PUZZLES = {
    "easy": {
        "rows": 4,
        "cols": 4,
        "url_body": "1l0n",
    },
    "medium": {
        "rows": 5,
        "cols": 5,
        "url_body": "1h1zg",
    },
    "hard": {
        "rows": 6,
        "cols": 6,
        "url_body": "1zm3m",
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


def _diag_ray_cells(grid, r, c, rows, cols):
    cells = []
    for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        nr, nc = r + dr, c + dc
        while 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == -1:
            cells.append((nr, nc))
            nr += dr
            nc += dc
    return cells


def _solve_lightup2(grid, rows, cols):
    empty_cells = []
    wall_cells = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == -1:
                empty_cells.append((r, c))
            elif grid[r][c] >= 0:
                wall_cells.append((r, c, grid[r][c]))

    empty_set = set(empty_cells)

    ray_cache = {}
    for r, c in empty_cells:
        ray_cache[(r, c)] = _diag_ray_cells(grid, r, c, rows, cols)

    diag_adj_cache = {}
    for wr, wc, num in wall_cells:
        adj = []
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = wr + dr, wc + dc
            if (nr, nc) in empty_set:
                adj.append((nr, nc))
        diag_adj_cache[(wr, wc)] = adj

    illuminators = {cell: set() for cell in empty_cells}
    for r, c in empty_cells:
        illuminators[(r, c)].add((r, c))
        for cell in ray_cache[(r, c)]:
            illuminators[cell].add((r, c))

    empty_idx = {cell: i for i, cell in enumerate(empty_cells)}

    bulbs = set()
    lit = set()
    skipped = set()
    best = [None]

    def _check_walls():
        for wr, wc, num in wall_cells:
            adj = diag_adj_cache[(wr, wc)]
            count = sum(1 for nr, nc in adj if (nr, nc) in bulbs)
            remaining = sum(1 for nr, nc in adj if (nr, nc) not in bulbs and (nr, nc) not in skipped)
            if count > num:
                return False
            if count + remaining < num:
                return False
        return True

    def _walls_satisfied():
        for wr, wc, num in wall_cells:
            adj = diag_adj_cache[(wr, wc)]
            count = sum(1 for nr, nc in adj if (nr, nc) in bulbs)
            if count != num:
                return False
        return True

    def _can_be_lit(idx):
        for cell in empty_cells[idx:]:
            if cell in lit:
                continue
            has_future_illuminator = False
            for illum in illuminators[cell]:
                if illum in bulbs or (illum not in skipped and empty_idx[illum] >= idx):
                    has_future_illuminator = True
                    break
            if not has_future_illuminator:
                return False
        return True

    def _backtrack(idx):
        if best[0] is not None:
            return

        if not _check_walls():
            return

        if not _can_be_lit(idx):
            return

        if idx == len(empty_cells):
            if _walls_satisfied() and lit >= empty_set:
                best[0] = set(bulbs)
            return

        r, c = empty_cells[idx]

        skipped.add((r, c))
        _backtrack(idx + 1)
        skipped.discard((r, c))
        if best[0] is not None:
            return

        bulbs.add((r, c))
        newly_lit = set()
        newly_lit.add((r, c))
        for cell in ray_cache[(r, c)]:
            if cell not in lit:
                newly_lit.add(cell)
        lit.update(newly_lit)
        _backtrack(idx + 1)
        bulbs.discard((r, c))
        lit.difference_update(newly_lit)

    _backtrack(0)
    return best[0]


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

    solution = _solve_lightup2(grid, rows, cols)
    if solution is not None:
        moves = _build_moves(solution)
        has_solution = True
    else:
        moves = []
        has_solution = False

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
            "cspuz_is_unique": None,
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
