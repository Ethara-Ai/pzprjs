import random
import sys
from collections import deque
from itertools import product


def is_valid_shading(grid, shaded, rows, cols):
    for r in range(rows):
        for c in range(cols):
            if not shaded[r][c]:
                continue
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and shaded[nr][nc]:
                    return False
    return True


def unshaded_connected(shaded, rows, cols):
    start = None
    for r in range(rows):
        for c in range(cols):
            if not shaded[r][c]:
                start = (r, c)
                break
        if start:
            break
    if start is None:
        return False

    visited = set()
    queue = deque([start])
    visited.add(start)
    while queue:
        r, c = queue.popleft()
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not shaded[nr][nc] and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc))

    total_unshaded = sum(1 for r in range(rows) for c in range(cols) if not shaded[r][c])
    return len(visited) == total_unshaded


def no_duplicate_unshaded(grid, shaded, rows, cols):
    for r in range(rows):
        seen = []
        for c in range(cols):
            if not shaded[r][c]:
                if grid[r][c] in seen:
                    return False
                seen.append(grid[r][c])
    for c in range(cols):
        seen = []
        for r in range(rows):
            if not shaded[r][c]:
                if grid[r][c] in seen:
                    return False
                seen.append(grid[r][c])
    return True


def is_valid_solution(grid, shaded, rows, cols):
    if not is_valid_shading(grid, shaded, rows, cols):
        return False
    if not unshaded_connected(shaded, rows, cols):
        return False
    if not no_duplicate_unshaded(grid, shaded, rows, cols):
        return False
    return True


def solve_hitori(grid, rows, cols, max_solutions=2):
    solutions = []
    shaded = [[False] * cols for _ in range(rows)]

    cells_with_dups = []
    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            row_dups = any(grid[r][c2] == val and c2 != c for c2 in range(cols))
            col_dups = any(grid[r2][c] == val and r2 != r for r2 in range(rows))
            if row_dups or col_dups:
                cells_with_dups.append((r, c))

    must_unshade = set()
    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            row_dups = any(grid[r][c2] == val and c2 != c for c2 in range(cols))
            col_dups = any(grid[r2][c] == val and r2 != r for r2 in range(rows))
            if not row_dups and not col_dups:
                must_unshade.add((r, c))

    def can_shade(r, c):
        if (r, c) in must_unshade:
            return False
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and shaded[nr][nc]:
                return False
        return True

    def has_duplicates():
        for r in range(rows):
            seen = {}
            for c in range(cols):
                if not shaded[r][c]:
                    v = grid[r][c]
                    if v in seen:
                        return True
                    seen[v] = True
        for c in range(cols):
            seen = {}
            for r in range(rows):
                if not shaded[r][c]:
                    v = grid[r][c]
                    if v in seen:
                        return True
                    seen[v] = True
        return False

    def backtrack(idx):
        if len(solutions) >= max_solutions:
            return

        if idx == len(cells_with_dups):
            if not has_duplicates() and unshaded_connected(shaded, rows, cols):
                solutions.append([row[:] for row in shaded])
            return

        r, c = cells_with_dups[idx]

        if shaded[r][c]:
            backtrack(idx + 1)
            return

        backtrack(idx + 1)
        if len(solutions) >= max_solutions:
            return

        if can_shade(r, c):
            shaded[r][c] = True
            backtrack(idx + 1)
            shaded[r][c] = False

    backtrack(0)
    return solutions


def generate_latin_square(n):
    square = [[(i + j) % n + 1 for j in range(n)] for i in range(n)]
    rows = list(range(n))
    cols = list(range(n))
    random.shuffle(rows)
    random.shuffle(cols)
    shuffled = [[square[rows[i]][cols[j]] for j in range(n)] for i in range(n)]

    nums = list(range(1, n + 1))
    random.shuffle(nums)
    mapping = {i + 1: nums[i] for i in range(n)}
    return [[mapping[shuffled[r][c]] for c in range(n)] for r in range(n)]


def introduce_duplicates(latin, n, num_shaded):
    grid = [row[:] for row in latin]
    shaded_cells = []

    candidates = []
    for r in range(n):
        for c in range(n):
            candidates.append((r, c))
    random.shuffle(candidates)

    for r, c in candidates:
        if len(shaded_cells) >= num_shaded:
            break

        adjacent_shaded = False
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if (nr, nc) in [(sr, sc) for sr, sc in shaded_cells]:
                adjacent_shaded = True
                break
        if adjacent_shaded:
            continue

        row_vals = [grid[r][c2] for c2 in range(n) if c2 != c and (r, c2) not in shaded_cells]
        col_vals = [grid[r2][c] for r2 in range(n) if r2 != r and (r2, c) not in shaded_cells]

        possible_vals = set(row_vals) | set(col_vals)
        if possible_vals:
            grid[r][c] = random.choice(list(possible_vals))
            shaded_cells.append((r, c))

    return grid, shaded_cells


def generate_puzzle(n, target_shaded, max_attempts=500):
    for attempt in range(max_attempts):
        latin = generate_latin_square(n)
        grid, shaded_cells = introduce_duplicates(latin, n, target_shaded)

        if len(shaded_cells) < target_shaded:
            continue

        solutions = solve_hitori(grid, n, n, max_solutions=2)

        if len(solutions) == 1:
            sol_grid = [[1 if solutions[0][r][c] else 0 for c in range(n)] for r in range(n)]
            print(f"  Found unique puzzle on attempt {attempt + 1}", file=sys.stderr)
            return grid, sol_grid

    return None, None


def grid_to_url_body(grid):
    body = ""
    for row in grid:
        for val in row:
            if val < 36:
                if val < 10:
                    body += str(val)
                else:
                    body += chr(ord('a') + val - 10)
            else:
                body += "-" + format(val, 'x').zfill(2)
    return body


def main():
    random.seed(42)

    configs = [
        ("easy", 5, 2),
        ("medium", 6, 4),
        ("hard", 7, 6),
    ]

    for name, size, target_shaded in configs:
        print(f"\nGenerating {name} ({size}x{size}, target {target_shaded} shaded)...", file=sys.stderr)
        grid, solution = generate_puzzle(size, target_shaded, max_attempts=1000)

        if grid is None:
            print(f"  FAILED to generate {name}!", file=sys.stderr)
            continue

        url_body = grid_to_url_body(grid)
        shaded_count = sum(sum(row) for row in solution)

        print(f"\n=== {name.upper()} ({size}x{size}) ===")
        print(f"url_body: {url_body}")
        print(f"grid:")
        for row in grid:
            print(f"  {row},")
        print(f"solution ({shaded_count} shaded):")
        for row in solution:
            print(f"  {row},")
        print(f"Play: https://puzz.link/p?hitori/{size}/{size}/{url_body}")

        solutions = solve_hitori(grid, size, size, max_solutions=2)
        print(f"Uniqueness verified: {len(solutions)} solution(s) found")


if __name__ == "__main__":
    main()
