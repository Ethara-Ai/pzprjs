import sys
from datetime import datetime, timezone


_PUZZLES = {
    "easy": {
        "rows": 6,
        "cols": 6,
        "url_body": "00000001h100g33g0g1h1g01111000h00",
        "shaded": [
            (1, 2), (1, 3), (2, 1), (2, 4),
        ],
    },
    "medium": {
        "rows": 8,
        "cols": 8,
        "url_body": "00g0h00011g1110g1g4g21k3k2332i122221g011h11000j00",
        "shaded": [
            (1, 3), (2, 2), (2, 4),
        ],
    },
    "hard": {
        "rows": 10,
        "cols": 10,
        "url_body": "00g0j00011i1110g123i21j3334g1j3443l3443i0g333332i12i221g011j11000l00",
        "shaded": [
            (1, 3), (2, 6), (3, 7), (6, 1),
        ],
    },
}


def _decode_number16(url_body, rows, cols):
    grid = [[None] * cols for _ in range(rows)]
    pos = 0
    i = 0
    total = rows * cols
    while i < len(url_body) and pos < total:
        ch = url_body[i]
        if "0" <= ch <= "9" or "a" <= ch <= "f":
            r, c = divmod(pos, cols)
            grid[r][c] = int(ch, 16)
            pos += 1
        elif ch == "-":
            hi = int(url_body[i + 1], 16)
            lo = int(url_body[i + 2], 16)
            r, c = divmod(pos, cols)
            grid[r][c] = hi * 16 + lo
            pos += 1
            i += 2
        elif ch == "+":
            val = int(url_body[i + 1 : i + 4], 16)
            r, c = divmod(pos, cols)
            grid[r][c] = val
            pos += 1
            i += 3
        elif "g" <= ch <= "z":
            pos += ord(ch) - ord("f")
        i += 1
    return grid


def _compute_bfs_depth(shaded, rows, cols):
    from collections import deque

    dist = [[-1] * cols for _ in range(rows)]
    q = deque()
    for r in range(rows):
        for c in range(cols):
            if shaded[r][c]:
                continue
            if r == 0 or r == rows - 1 or c == 0 or c == cols - 1:
                dist[r][c] = 0
                q.append((r, c))
    while q:
        cr, cc = q.popleft()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = cr + dr, cc + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if not shaded[nr][nc] and dist[nr][nc] == -1:
                    dist[nr][nc] = dist[cr][cc] + 1
                    q.append((nr, nc))
    return dist


def _verify_solution(clue_grid, shaded_grid, rows, cols):
    for r in range(rows - 1):
        for c in range(cols - 1):
            if (
                shaded_grid[r][c]
                and shaded_grid[r][c + 1]
                and shaded_grid[r + 1][c]
                and shaded_grid[r + 1][c + 1]
            ):
                return False

    visited = [[False] * cols for _ in range(rows)]
    start = None
    for r in range(rows):
        for c in range(cols):
            if not shaded_grid[r][c]:
                start = (r, c)
                break
        if start:
            break
    if start is None:
        return False
    stack = [start]
    visited[start[0]][start[1]] = True
    count = 1
    total_unshaded = sum(
        1 for r in range(rows) for c in range(cols) if not shaded_grid[r][c]
    )
    while stack:
        cr, cc = stack.pop()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = cr + dr, cc + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if not shaded_grid[nr][nc] and not visited[nr][nc]:
                    visited[nr][nc] = True
                    count += 1
                    stack.append((nr, nc))
    if count != total_unshaded:
        return False

    dist = _compute_bfs_depth(shaded_grid, rows, cols)
    for r in range(rows):
        for c in range(cols):
            if clue_grid[r][c] is not None:
                if dist[r][c] != clue_grid[r][c]:
                    return False
    return True


def _build_moves(shaded_grid, rows, cols):
    moves_full = []
    moves_required = []
    moves_hint = []
    for r in range(rows):
        for c in range(cols):
            x = 1 + c * 2
            y = 1 + r * 2
            if shaded_grid[r][c]:
                move = f"mouse,left,{x},{y}"
                moves_full.append(move)
                moves_required.append(move)
            else:
                move = f"mouse,right,{x},{y}"
                moves_full.append(move)
                moves_hint.append(move)
    return moves_full, moves_required, moves_hint


def generate_custom_tidepool(difficulty="easy"):
    if difficulty not in _PUZZLES:
        difficulty = "easy"
    puzzle = _PUZZLES[difficulty]
    rows = puzzle["rows"]
    cols = puzzle["cols"]
    url_body = puzzle["url_body"]

    clue_grid = _decode_number16(url_body, rows, cols)

    shaded_grid = [[False] * cols for _ in range(rows)]
    for r, c in puzzle["shaded"]:
        shaded_grid[r][c] = True

    if not _verify_solution(clue_grid, shaded_grid, rows, cols):
        return {"error": "hardcoded solution does not verify"}

    moves_full, moves_required, moves_hint = _build_moves(shaded_grid, rows, cols)
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": f"http://localhost:8000/p.html?tidepool/{cols}/{rows}/{url_body}",
        "pid": "tidepool",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "puzzlink_url": f"https://pzprxs.vercel.app/p?tidepool/{cols}/{rows}/{url_body}",
        "source": {
            "site_name": "custom_generated",
            "page_url": None,
            "feed_type": "generated",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": True,
            "cspuz_is_unique": True,
            "db_w": cols,
            "db_h": rows,
            "difficulty": difficulty,
        },
        "created_at": now,
        "solution": {
            "moves_full": moves_full,
            "moves_required": moves_required,
            "moves_hint": moves_hint,
        },
    }


if __name__ == "__main__":
    difficulty = sys.argv[1] if len(sys.argv) > 1 else "easy"
    import json

    result = generate_custom_tidepool(difficulty)
    print(json.dumps(result, indent=2))
