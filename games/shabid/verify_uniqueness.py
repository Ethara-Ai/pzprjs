"""
Verify that each Gradient Walls puzzle has exactly one unique solution.

Rules:
- Fill every empty cell with a number 1..max_val
- Wall between adjacent cells ↔ |val_a - val_b| > 1
- No wall between adjacent cells ↔ |val_a - val_b| <= 1
"""
import sys
import time

# Puzzle data from puzzle_gradientwalls.py
_PUZZLES = {
    "easy": {
        "rows": 6, "cols": 6, "max_val": 4,
        "url_body": "1g1434g3h4g1i1g4g41g1k4414g4340040o00k020",
        "solution": [
            [1, 2, 1, 4, 3, 4],
            [2, 3, 2, 3, 4, 3],
            [1, 2, 3, 2, 1, 2],
            [4, 3, 4, 1, 2, 1],
            [3, 2, 3, 2, 3, 4],
            [4, 1, 4, 3, 4, 3],
        ],
        "clues": {
            "0,0": 1, "0,2": 1, "0,3": 4, "0,4": 3, "0,5": 4,
            "1,1": 3, "1,4": 4,
            "2,0": 1, "2,4": 1,
            "3,0": 4, "3,2": 4, "3,3": 1, "3,5": 1,
            "4,5": 4,
            "5,0": 4, "5,1": 1, "5,2": 4, "5,4": 4, "5,5": 3,
        },
    },
    "medium": {
        "rows": 8, "cols": 8, "max_val": 5,
        "url_body": "1i5j1g3g5g1h5i1j5j5i1j5i1g5h1i5g2h14h3024h1088i440000000000000",
        "solution": [
            [1, 2, 3, 4, 5, 4, 3, 2],
            [2, 1, 4, 3, 4, 5, 2, 1],
            [3, 2, 5, 4, 3, 4, 1, 2],
            [4, 3, 4, 5, 2, 3, 2, 3],
            [5, 4, 3, 4, 1, 2, 3, 4],
            [4, 5, 2, 3, 2, 1, 4, 5],
            [3, 4, 1, 2, 3, 2, 5, 4],
            [2, 3, 2, 1, 4, 3, 4, 3],
        ],
        "clues": {
            "0,0": 1, "0,4": 5,
            "1,1": 1, "1,3": 3, "1,5": 5, "1,7": 1,
            "2,2": 5, "2,6": 1,
            "3,3": 5,
            "4,0": 5, "4,4": 1,
            "5,1": 5, "5,5": 1, "5,7": 5,
            "6,2": 1, "6,6": 5,
            "7,0": 2, "7,3": 1, "7,4": 4, "7,7": 3,
        },
    },
    "hard": {
        "rows": 10, "cols": 10, "max_val": 6,
        "url_body": "h14g6h12j4j1i6l6i6g6j6k6j6h1h6p6i1l1i1g1i21g3g521h4g80g0c0o5g80g0c0o000000000000000000",
        "solution": [
            [3, 2, 1, 4, 5, 6, 3, 2, 1, 2],
            [4, 3, 2, 5, 4, 5, 4, 3, 2, 1],
            [5, 4, 3, 6, 5, 4, 5, 4, 3, 2],
            [6, 5, 4, 5, 6, 3, 6, 5, 4, 3],
            [5, 6, 5, 4, 5, 2, 5, 6, 5, 4],
            [4, 5, 6, 3, 4, 1, 4, 5, 6, 5],
            [3, 4, 5, 2, 3, 2, 3, 4, 5, 6],
            [2, 3, 4, 1, 2, 3, 2, 3, 4, 5],
            [1, 2, 3, 2, 1, 4, 1, 2, 3, 4],
            [2, 1, 2, 3, 2, 5, 2, 1, 2, 3],
        ],
        "clues": {
            "0,2": 1, "0,3": 4, "0,5": 6, "0,8": 1, "0,9": 2,
            "1,4": 4, "1,9": 1,
            "2,3": 6,
            "3,0": 6, "3,4": 6, "3,6": 6,
            "4,1": 6, "4,7": 6,
            "5,2": 6, "5,5": 1, "5,8": 6,
            "6,9": 6,
            "7,3": 1,
            "8,0": 1, "8,4": 1, "8,6": 1,
            "9,0": 2, "9,1": 1, "9,3": 3, "9,5": 5, "9,6": 2, "9,7": 1,
        },
    },
}


def decode_border_string(border_str, rows, cols):
    """
    Decode pzpr border string into wall sets.
    
    Border encoding order (matches pzpr.js):
    - First (cols-1)*rows bits: horizontal borders (between columns, row by row)
      These are VERTICAL walls between cell (r,c) and (r,c+1)
    - Then cols*(rows-1) bits: vertical borders (between rows, col by col) 
      These are HORIZONTAL walls between cell (r,c) and (r+1,c)
    
    Each base-32 digit encodes 5 borders via bitmask [16, 8, 4, 2, 1]
    """
    # Decode all bits from the base-32 string
    bits = []
    for ch in border_str:
        val = int(ch, 32)
        bits.extend([(val >> (4-i)) & 1 for i in range(5)])
    
    h_walls = set()  # Walls between (r,c) and (r,c+1) — vertical line between cols
    v_walls = set()  # Walls between (r,c) and (r+1,c) — horizontal line between rows
    
    # First (cols-1)*rows bits: borders between adjacent columns
    idx = 0
    for r in range(rows):
        for c in range(cols - 1):
            if idx < len(bits) and bits[idx]:
                h_walls.add((r, c))  # wall between (r,c) and (r,c+1)
            idx += 1
    
    # Next cols*(rows-1) bits: borders between adjacent rows
    for r in range(rows - 1):
        for c in range(cols):
            if idx < len(bits) and bits[idx]:
                v_walls.add((r, c))  # wall between (r,c) and (r+1,c)
            idx += 1
    
    return h_walls, v_walls


def decode_number_string(num_str, rows, cols):
    """
    Decode pzpr number16 encoding.
    Returns dict of (row, col) -> value for clue cells.
    
    Format: numbers 0-9a-f are literal hex values (but we use 1-6).
    Letters g-z represent gaps: g=1 empty, h=2 empties, ..., z=16 empties.
    """
    clues = {}
    cell_idx = 0
    total_cells = rows * cols
    i = 0
    
    while i < len(num_str) and cell_idx < total_cells:
        ch = num_str[i]
        if ch in '0123456789abcdef':
            val = int(ch, 16)
            if val > 0:
                r = cell_idx // cols
                c = cell_idx % cols
                clues[(r, c)] = val
            cell_idx += 1
        elif 'g' <= ch <= 'z':
            # Gap: skip (ord(ch) - ord('f')) cells
            skip = ord(ch) - ord('f')
            cell_idx += skip
        i += 1
    
    return clues


def parse_url_body(url_body, rows, cols):
    """Parse the combined url_body (numbers + borders concatenated)."""
    # Determine where numbers end and borders begin
    # Number encoding covers exactly `rows*cols` cells
    # We need to parse it to find the boundary
    total_cells = rows * cols
    cell_idx = 0
    i = 0
    
    while i < len(url_body) and cell_idx < total_cells:
        ch = url_body[i]
        if ch in '0123456789abcdef':
            cell_idx += 1
        elif 'g' <= ch <= 'z':
            skip = ord(ch) - ord('f')
            cell_idx += skip
        i += 1
    
    num_part = url_body[:i]
    border_part = url_body[i:]
    
    clues = decode_number_string(num_part, rows, cols)
    h_walls, v_walls = decode_border_string(border_part, rows, cols)
    
    return clues, h_walls, v_walls


def has_wall(r1, c1, r2, c2, h_walls, v_walls):
    """Check if there's a wall between adjacent cells (r1,c1) and (r2,c2)."""
    if r1 == r2:
        # Horizontal neighbors — check h_walls (vertical wall between cols)
        min_c = min(c1, c2)
        return (r1, min_c) in h_walls
    else:
        # Vertical neighbors — check v_walls (horizontal wall between rows)
        min_r = min(r1, r2)
        return (min_r, c1) in v_walls


def verify_solution(solution, clues, h_walls, v_walls, rows, cols, max_val):
    """Verify a complete solution satisfies all constraints."""
    for r in range(rows):
        for c in range(cols):
            val = solution[r][c]
            if val < 1 or val > max_val:
                return False
            # Check clue consistency
            if (r, c) in clues and clues[(r, c)] != val:
                return False
            # Check right neighbor
            if c + 1 < cols:
                diff = abs(val - solution[r][c+1])
                wall = has_wall(r, c, r, c+1, h_walls, v_walls)
                if wall and diff <= 1:
                    return False
                if not wall and diff > 1:
                    return False
            # Check bottom neighbor
            if r + 1 < rows:
                diff = abs(val - solution[r+1][c])
                wall = has_wall(r, c, r+1, c, h_walls, v_walls)
                if wall and diff <= 1:
                    return False
                if not wall and diff > 1:
                    return False
    return True


def solve_count(clues, h_walls, v_walls, rows, cols, max_val, max_solutions=2):
    """
    Count solutions using backtracking with constraint propagation.
    Stops early once max_solutions found (for uniqueness, set to 2).
    Returns (count, first_solution_or_None).
    """
    grid = [[0] * cols for _ in range(rows)]
    
    # Pre-fill clues
    for (r, c), val in clues.items():
        grid[r][c] = val
    
    # Build ordered list of empty cells
    empty_cells = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                empty_cells.append((r, c))
    
    solutions_found = [0]
    first_solution = [None]
    
    def get_possible_values(r, c):
        """Get valid values for cell (r,c) given current partial assignment."""
        possible = set(range(1, max_val + 1))
        
        neighbors = []
        if c > 0: neighbors.append((r, c-1))
        if c < cols-1: neighbors.append((r, c+1))
        if r > 0: neighbors.append((r-1, c))
        if r < rows-1: neighbors.append((r+1, c))
        
        for nr, nc in neighbors:
            nval = grid[nr][nc]
            if nval == 0:
                continue
            wall = has_wall(r, c, nr, nc, h_walls, v_walls)
            if wall:
                # Must differ by > 1, so exclude nval-1, nval, nval+1
                possible.discard(nval - 1)
                possible.discard(nval)
                possible.discard(nval + 1)
            else:
                # Must differ by <= 1, so only nval-1, nval, nval+1 are valid
                possible &= {nval - 1, nval, nval + 1}
                if not possible:
                    return set()
        
        return possible
    
    def backtrack(idx):
        if solutions_found[0] >= max_solutions:
            return
        
        if idx == len(empty_cells):
            solutions_found[0] += 1
            if first_solution[0] is None:
                first_solution[0] = [row[:] for row in grid]
            return
        
        r, c = empty_cells[idx]
        possible = get_possible_values(r, c)
        
        for val in sorted(possible):
            grid[r][c] = val
            backtrack(idx + 1)
            if solutions_found[0] >= max_solutions:
                grid[r][c] = 0
                return
            grid[r][c] = 0
    
    backtrack(0)
    return solutions_found[0], first_solution[0]


def main():
    levels = sys.argv[1:] if len(sys.argv) > 1 else ["easy", "medium", "hard"]
    
    all_unique = True
    
    for level in levels:
        if level not in _PUZZLES:
            print(f"Unknown level: {level}")
            continue
        
        p = _PUZZLES[level]
        rows, cols, max_val = p["rows"], p["cols"], p["max_val"]
        
        print(f"\n{'='*60}")
        print(f"Verifying {level} ({rows}x{cols}, values 1-{max_val})")
        print(f"{'='*60}")
        
        # Parse URL body
        clues, h_walls, v_walls = parse_url_body(p["url_body"], rows, cols)
        
        print(f"Clues decoded: {len(clues)}")
        print(f"H-walls (between cols): {len(h_walls)} -> {sorted(h_walls)}")
        print(f"V-walls (between rows): {len(v_walls)} -> {sorted(v_walls)}")
        print(f"Empty cells to fill: {rows*cols - len(clues)}")
        
        # First verify the claimed solution
        expected = p["solution"]
        valid = verify_solution(expected, clues, h_walls, v_walls, rows, cols, max_val)
        print(f"\nClaimed solution valid: {valid}")
        
        if not valid:
            print("ERROR: Claimed solution does NOT satisfy constraints!")
            all_unique = False
            continue
        
        # Count solutions (stop at 2)
        print(f"\nSearching for all solutions (will stop at 2)...")
        t0 = time.monotonic()
        count, found_sol = solve_count(clues, h_walls, v_walls, rows, cols, max_val, max_solutions=2)
        elapsed = time.monotonic() - t0
        
        print(f"Solutions found: {count}")
        print(f"Search time: {elapsed:.3f}s")
        
        if count == 1:
            print(f"✅ UNIQUE SOLUTION CONFIRMED")
            # Verify it matches claimed
            if found_sol == expected:
                print(f"✅ Found solution matches claimed solution")
            else:
                print(f"⚠️  Found solution differs from claimed!")
                print(f"Found: {found_sol}")
        elif count == 0:
            print(f"❌ NO SOLUTION EXISTS")
            all_unique = False
        else:
            print(f"❌ MULTIPLE SOLUTIONS ({count}+)")
            all_unique = False
    
    print(f"\n{'='*60}")
    if all_unique:
        print("✅ ALL PUZZLES HAVE UNIQUE SOLUTIONS")
    else:
        print("❌ SOME PUZZLES FAILED UNIQUENESS CHECK")
    print(f"{'='*60}")
    
    return 0 if all_unique else 1


if __name__ == "__main__":
    sys.exit(main())
