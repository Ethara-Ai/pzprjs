import sys
import time
from datetime import datetime, timezone


_PUZZLES = {
    "easy": {
        "rows": 4,
        "cols": 4,
        "url_body": "2g2l2g2j",
    },
    "medium": {
        "rows": 6,
        "cols": 6,
        "url_body": "2g2g2n2g2g2l2g2g2m",
    },
    "hard": {
        "rows": 8,
        "cols": 8,
        "url_body": "2g2g2g2p2g2g2g2n2g2g2g2p2g2g2g2n",
    },
}


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


def _solve_nurikabe2(grid, rows, cols):
    DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    clues = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] > 0:
                clues.append((r, c))

    sol = [[-1] * cols for _ in range(rows)]

    for r, c in clues:
        sol[r][c] = 0

    clue_neighbors = []
    for r, c in clues:
        nbrs = []
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                nbrs.append((nr, nc))
        clue_neighbors.append(nbrs)

    owner = [[-1] * cols for _ in range(rows)]
    for i, (r, c) in enumerate(clues):
        owner[r][c] = i

    def _no_2x2_unshaded(r, c):
        for dr in (0, -1):
            for dc in (0, -1):
                tr, tc = r + dr, c + dc
                if 0 <= tr < rows - 1 and 0 <= tc < cols - 1:
                    if all(sol[tr + a][tc + b] == 0
                           for a in range(2) for b in range(2)):
                        return False
        return True

    def _islands_no_touch(r, c, clue_idx):
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if owner[nr][nc] != -1 and owner[nr][nc] != clue_idx:
                    if sol[nr][nc] == 0:
                        return False
        return True

    def _check_shaded_domino_valid():
        visited = [[False] * cols for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                if sol[r][c] == 1 and not visited[r][c]:
                    stack = [(r, c)]
                    visited[r][c] = True
                    size = 0
                    while stack:
                        cr, cc = stack.pop()
                        size += 1
                        if size > 2:
                            return False
                        for dr, dc in DIRS:
                            nr, nc = cr + dr, cc + dc
                            if 0 <= nr < rows and 0 <= nc < cols:
                                if sol[nr][nc] == 1 and not visited[nr][nc]:
                                    visited[nr][nc] = True
                                    stack.append((nr, nc))
                    if size != 2:
                        return False
        return True

    result = [None]

    def _backtrack(idx):
        if idx == len(clues):
            for r in range(rows):
                for c in range(cols):
                    if sol[r][c] == -1:
                        sol[r][c] = 1
            if _check_shaded_domino_valid():
                result[0] = [row[:] for row in sol]
                return True
            for r in range(rows):
                for c in range(cols):
                    if owner[r][c] == -1 and sol[r][c] == 1:
                        sol[r][c] = -1
            return False

        cr, cc = clues[idx]
        for nr, nc in clue_neighbors[idx]:
            if sol[nr][nc] != -1:
                continue
            if owner[nr][nc] != -1:
                continue

            sol[nr][nc] = 0
            owner[nr][nc] = idx

            if (_no_2x2_unshaded(nr, nc)
                    and _islands_no_touch(nr, nc, idx)
                    and _islands_no_touch(cr, cc, idx)):
                if _backtrack(idx + 1):
                    return True

            sol[nr][nc] = -1
            owner[nr][nc] = -1

        return False

    _backtrack(0)
    return result[0]


def _build_moves(rows, cols, solution):
    moves_required = []
    moves_hint = []
    for r in range(rows):
        for c in range(cols):
            x = 1 + c * 2
            y = 1 + r * 2
            if solution[r][c] == 1:
                moves_required.append(f"mouse,left,{x},{y}")
            elif solution[r][c] == 0:
                moves_hint.append(f"mouse,right,{x},{y}")
    moves_full = moves_required + moves_hint
    return moves_full, moves_required, moves_hint


def generate_custom_nurikabe2(difficulty="easy"):
    p = _PUZZLES[difficulty]
    rows, cols, url_body = p["rows"], p["cols"], p["url_body"]
    grid = _decode_number16(url_body, rows, cols)
    now = datetime.now(timezone.utc).isoformat()

    num_clues = sum(1 for r in range(rows) for c in range(cols) if grid[r][c] > 0)

    solution = _solve_nurikabe2(grid, rows, cols)
    if solution is None:
        raise RuntimeError(f"No solution found for {difficulty} puzzle")

    moves_full, moves_required, moves_hint = _build_moves(rows, cols, solution)

    return {
        "puzzle_url": f"http://pzv.jp/p.html?nurikabe2/{cols}/{rows}/{url_body}",
        "pid": "nurikabe2",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"https://puzz.link/p?nurikabe2/{cols}/{rows}/{url_body}",
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": True,
            "cspuz_is_unique": None,
            "db_w": cols,
            "db_h": rows,
            "num_island_clues": num_clues,
            "modified_rules": [
                "no 2x2 unshaded squares",
                "shaded groups must be exactly 2 cells (dominoes)",
                "connected-shade requirement removed",
            ],
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
    puzzle_data = generate_custom_nurikabe2(difficulty)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))

    meta = puzzle_data["metadata"]
    print(f"\nGrid: {puzzle_data['width']}x{puzzle_data['height']}")
    print(f"Island clues: {meta['num_island_clues']}")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
