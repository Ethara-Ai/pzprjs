import sys
import time
from datetime import datetime, timezone


_PUZZLES = {
    "easy": {
        "rows": 5,
        "cols": 5,
        "url_body": "k2i4h4j1k2g",
    },
    "medium": {
        "rows": 6,
        "cols": 6,
        "url_body": "mabh8o6ja7i2h3i",
    },
    "hard": {
        "rows": 7,
        "cols": 7,
        "url_body": "j31g5g8ha8n5u5habj3i",
    },
}


def _decode_number_tapa(url_body, rows, cols):
    grid = [[None] * cols for _ in range(rows)]
    pos = 0
    i = 0
    total = rows * cols
    while i < len(url_body) and pos < total:
        ch = url_body[i]
        if '0' <= ch <= '8':
            r, c = divmod(pos, cols)
            grid[r][c] = [int(ch)]
            pos += 1
        elif ch == '9':
            r, c = divmod(pos, cols)
            grid[r][c] = [1, 1, 1, 1]
            pos += 1
        elif ch == '.':
            r, c = divmod(pos, cols)
            grid[r][c] = [-2]
            pos += 1
        elif 'a' <= ch <= 'f':
            i += 1
            if i >= len(url_body):
                break
            ch2 = url_body[i]
            num = int(ch, 36) * 36 + int(ch2, 36)
            r, c = divmod(pos, cols)
            if 360 <= num < 396:
                v = num - 360
                v0, v1 = v // 6, v % 6
                grid[r][c] = [v0 if v0 != 0 else -2, v1 if v1 != 0 else -2]
            elif 396 <= num < 460:
                v = num - 396
                v0, v1, v2 = v // 16, (v % 16) // 4, v % 4
                grid[r][c] = [
                    v0 if v0 != 0 else -2,
                    v1 if v1 != 0 else -2,
                    v2 if v2 != 0 else -2,
                ]
            elif 460 <= num < 476:
                v = num - 460
                v0 = v // 8
                v1 = (v % 8) // 4
                v2 = (v % 4) // 2
                v3 = v % 2
                grid[r][c] = [
                    v0 if v0 != 0 else -2,
                    v1 if v1 != 0 else -2,
                    v2 if v2 != 0 else -2,
                    v3 if v3 != 0 else -2,
                ]
            pos += 1
        elif 'g' <= ch <= 'z':
            gap = ord(ch) - ord('g') + 1
            pos += gap
        i += 1
    return grid


def _solve_tapa(grid, rows, cols):
    sol = [[None] * cols for _ in range(rows)]
    empty_cells = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] is not None:
                sol[r][c] = None
            else:
                empty_cells.append((r, c))
                sol[r][c] = -1

    clue_positions = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] is not None:
                clue_positions.append((r, c))

    _DIRS8 = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]

    def _check_clue(r, c):
        clue = grid[r][c]
        ring = []
        for dr, dc in _DIRS8:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols):
                ring.append(0)
            elif grid[nr][nc] is not None:
                ring.append(0)
            elif sol[nr][nc] == -1:
                return None
            else:
                ring.append(sol[nr][nc])

        runs = []
        current_run = 0
        for v in ring:
            if v == 1:
                current_run += 1
            else:
                if current_run > 0:
                    runs.append(current_run)
                current_run = 0
        if current_run > 0:
            runs.append(current_run)

        if len(runs) >= 2 and ring[0] == 1 and ring[-1] == 1:
            runs[0] += runs[-1]
            runs.pop()

        expected = sorted(v for v in clue if v != -2)
        actual = sorted(runs)
        return actual == expected

    def _check_no_2x2_shaded(r, c):
        for dr in range(0, -2, -1):
            for dc in range(0, -2, -1):
                tr, tc = r + dr, c + dc
                if tr < 0 or tc < 0 or tr + 1 >= rows or tc + 1 >= cols:
                    continue
                all_shaded = True
                for rr in range(tr, tr + 2):
                    for cc in range(tc, tc + 2):
                        if grid[rr][cc] is not None:
                            all_shaded = False
                            break
                        if sol[rr][cc] != 1:
                            all_shaded = False
                            break
                    if not all_shaded:
                        break
                if all_shaded:
                    return False
        return True

    def _check_connectivity():
        shaded_cells = set()
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] is None and sol[r][c] == 1:
                    shaded_cells.add((r, c))

        if not shaded_cells:
            return True

        start = next(iter(shaded_cells))
        visited = {start}
        queue = [start]
        while queue:
            cr, cc = queue.pop()
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = cr + dr, cc + dc
                if (nr, nc) in shaded_cells and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))

        return len(visited) == len(shaded_cells)

    def _partial_clue_ok(r, c):
        result = _check_clue(r, c)
        if result is None:
            return True
        return result

    adj_clues = {}
    for r, c in empty_cells:
        result = []
        for dr, dc in _DIRS8:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] is not None:
                result.append((nr, nc))
        adj_clues[(r, c)] = result

    def solve(idx):
        if idx == len(empty_cells):
            if not _check_connectivity():
                return False
            for cr, cc in clue_positions:
                if not _check_clue(cr, cc):
                    return False
            return True

        r, c = empty_cells[idx]

        for val in (1, 0):
            sol[r][c] = val

            if val == 1 and not _check_no_2x2_shaded(r, c):
                sol[r][c] = -1
                continue

            clue_ok = True
            for cr, cc in adj_clues[(r, c)]:
                if not _partial_clue_ok(cr, cc):
                    clue_ok = False
                    break
            if not clue_ok:
                sol[r][c] = -1
                continue

            if solve(idx + 1):
                return True

            sol[r][c] = -1

        return False

    if solve(0):
        result = [[None] * cols for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] is not None:
                    result[r][c] = None
                else:
                    result[r][c] = sol[r][c]
        return result
    return None


def _build_moves(rows, cols, solution):
    moves_full = []
    for r in range(rows):
        for c in range(cols):
            if solution[r][c] == 1:
                x = 1 + c * 2
                y = 1 + r * 2
                moves_full.append(f"mouse,left,{x},{y}")
    return {
        "moves_full": moves_full,
        "moves_required": list(moves_full),
        "moves_hint": [],
    }


def generate_custom_tapa(difficulty="easy"):
    p = _PUZZLES[difficulty]
    rows, cols, url_body = p["rows"], p["cols"], p["url_body"]
    grid = _decode_number_tapa(url_body, rows, cols)
    now = datetime.now(timezone.utc).isoformat()

    num_clue_cells = sum(
        1 for r in range(rows) for c in range(cols) if grid[r][c] is not None
    )

    solution = _solve_tapa(grid, rows, cols)
    has_solution = solution is not None
    if has_solution:
        moves = _build_moves(rows, cols, solution)
    else:
        moves = {"moves_full": [], "moves_required": [], "moves_hint": []}

    return {
        "puzzle_url": f"http://localhost:8000/p.html?tapa/{cols}/{rows}/{url_body}",
        "pid": "tapa",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves["moves_required"]),
        "number_total_solution_moves": len(moves["moves_full"]),
        "puzzlink_url": f"http://localhost:8000/p.html?tapa/{cols}/{rows}/{url_body}",
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
            "num_clue_cells": num_clue_cells,
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
    puzzle_data = generate_custom_tapa(difficulty)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))

    meta = puzzle_data["metadata"]
    print(f"\nGrid: {puzzle_data['width']}x{puzzle_data['height']}")
    print(f"Clue cells: {meta['num_clue_cells']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")