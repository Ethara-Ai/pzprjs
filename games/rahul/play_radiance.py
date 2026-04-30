
import json
import sys
import time
from datetime import datetime, timezone
from itertools import product



_PUZZLES = {
    "easy": {
        "rows": 6,
        "cols": 6,
        "url_body": "14d3l2d3l",

        "solution_mirrors": {(0, 5): "\\", (3, 5): "/"},
    },
    "medium": {
        "rows": 8,
        "cols": 8,
        "url_body": "14f3p3f3x2g",
 
        "solution_mirrors": {(0, 7): "\\", (3, 7): "/", (3, 0): "/"},
    },
    "hard": {
        "rows": 10,
        "cols": 10,
        "url_body": "14h3zd3h3t3h3s2",

        "solution_mirrors": {
            (0, 9): "\\",
            (4, 9): "/",
            (4, 0): "/",
            (7, 0): "\\",
            (7, 9): "\\",
        },
    },
}



EMPTY = 0
EMITTER = 1
TARGET = 2
MIRROR_SLOT = 3


UP, DN, LT, RT = 1, 2, 3, 4


_DIR_DELTA = {UP: (-1, 0), DN: (1, 0), LT: (0, -1), RT: (0, 1)}


_REFLECT_FORWARD = {UP: RT, RT: UP, DN: LT, LT: DN}   # /
_REFLECT_BACK = {UP: LT, LT: UP, DN: RT, RT: DN}      # \


def _decode_grid(url_body, rows, cols):
    grid = [[EMPTY] * cols for _ in range(rows)]
    emitter_pos = None
    emitter_dir = 0
    target_pos = None
    slots = []

    c = 0  
    i = 0  
    while i < len(url_body) and c < rows * cols:
        ch = url_body[i]
        if ch == "1":
            i += 1
            d = int(url_body[i])
            r, col = divmod(c, cols)
            grid[r][col] = EMITTER
            emitter_pos = (r, col)
            emitter_dir = d
            c += 1
        elif ch == "2":
            r, col = divmod(c, cols)
            grid[r][col] = TARGET
            target_pos = (r, col)
            c += 1
        elif ch == "3":
            r, col = divmod(c, cols)
            grid[r][col] = MIRROR_SLOT
            slots.append((r, col))
            c += 1
        elif "a" <= ch <= "z":
            c += ord(ch) - 96
        i += 1

    return grid, emitter_pos, emitter_dir, target_pos, slots



def _trace_beam(rows, cols, grid, emitter_pos, emitter_dir, mirrors):
    path = []
    r, col = emitter_pos
    d = emitter_dir
    visited = set()
    max_steps = (rows + cols) * 4

    for _ in range(max_steps):
        dr, dc = _DIR_DELTA[d]
        r, col = r + dr, col + dc

        if r < 0 or r >= rows or col < 0 or col >= cols:
            break

        cell_type = grid[r][col]

        if cell_type == EMITTER:
            break

        path.append((r, col))

        if cell_type == TARGET:
            break

        if cell_type == MIRROR_SLOT and (r, col) in mirrors:
            mirror = mirrors[(r, col)]
            if mirror == "/":
                d = _REFLECT_FORWARD[d]
            else:
                d = _REFLECT_BACK[d]

        key = (r, col, d)
        if key in visited:
            break
        visited.add(key)

    return path


def _solve(rows, cols, grid, emitter_pos, emitter_dir, target_pos, slots):
    
    num_slots = len(slots)
    mirror_types = ["/", "\\"]

    for combo in product(mirror_types, repeat=num_slots):
        mirrors = {slots[i]: combo[i] for i in range(num_slots)}
        path = _trace_beam(rows, cols, grid, emitter_pos, emitter_dir, mirrors)

        if not path or path[-1] != target_pos:
            continue

        slots_visited = set(pos for pos in path if grid[pos[0]][pos[1]] == MIRROR_SLOT)
        if slots_visited == set(slots):
            return mirrors

    return None




def _build_moves(rows, cols, slots, solution_mirrors):
   
    moves_required = []

    for r, c in slots:
        bx = 2 * c + 1
        by = 2 * r + 1
        mirror = solution_mirrors[(r, c)]
        if mirror == "/":
            # 1 left-click: empty → /
            moves_required.append(f"mouse,left,{bx},{by}")
        else:  # "\"
            # 2 left-clicks: empty → / → backslash
            moves_required.append(f"mouse,left,{bx},{by}")
            moves_required.append(f"mouse,left,{bx},{by}")

    moves_full = list(moves_required)
    moves_hint = []
    return moves_full, moves_required, moves_hint



_PID = "radiance"


def generate_custom_radiance(difficulty="easy"):
    level = difficulty
    p = _PUZZLES[level]

    rows = p["rows"]
    cols = p["cols"]
    url_body = p["url_body"]

    grid, emitter_pos, emitter_dir, target_pos, slots = _decode_grid(url_body, rows, cols)

    # Use pre-computed solution if available, otherwise solve
    if "solution_mirrors" in p:
        solution_mirrors = p["solution_mirrors"]
    else:
        solution_mirrors = _solve(rows, cols, grid, emitter_pos, emitter_dir, target_pos, slots)

    has_solution = solution_mirrors is not None

    if has_solution:
        # Verify solution
        path = _trace_beam(rows, cols, grid, emitter_pos, emitter_dir, solution_mirrors)
        reached_target = path and path[-1] == target_pos
        all_slots_used = set(pos for pos in path if grid[pos[0]][pos[1]] == MIRROR_SLOT) == set(slots)
        has_solution = reached_target and all_slots_used

    if has_solution:
        moves_full, moves_required, moves_hint = _build_moves(rows, cols, slots, solution_mirrors)
    else:
        moves_full, moves_required, moves_hint = [], [], []

    puzzle_url = f"http://localhost:8000/p.html?{_PID}/{cols}/{rows}/{url_body}"
    now = datetime.now(timezone.utc).isoformat()

    return {
        "puzzle_url": puzzle_url,
        "puzzlink_url": puzzle_url,
        "pid": _PID,
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),
        "source": {
            "site_name": "ppbench_golden",
            "page_url": None,
            "feed_type": "golden_dataset",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": has_solution,
            "cspuz_is_unique": True,
            "db_w": cols,
            "db_h": rows,
            "level": level,
            "num_mirror_slots": len(slots),
            "emitter_direction": {1: "UP", 2: "DN", 3: "LT", 4: "RT"}[emitter_dir],
        },
        "created_at": now,
        "solution": {
            "moves_full": moves_full,
            "moves_required": moves_required,
            "moves_hint": moves_hint,
        },
    }



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <easy|medium|hard>")
        sys.exit(1)

    level = sys.argv[1].lower()
    if level not in _PUZZLES:
        print(f"Invalid difficulty: {level}. Must be one of: easy, medium, hard")
        sys.exit(1)

    start = time.time()
    data = generate_custom_radiance(level)
    elapsed = time.time() - start

    print(json.dumps(data, indent=2, default=str))
    print(
        f"\n# {_PID} [{level}] — {data['width']}x{data['height']}, "
        f"{data['number_required_moves']} required moves, "
        f"{data['number_total_solution_moves']} total moves, "
        f"generated in {elapsed:.2f}s",
        file=sys.stderr,
    )
