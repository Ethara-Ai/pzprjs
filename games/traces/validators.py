from __future__ import annotations
"""Post-solve validators for R6 (move ordering) and R7-R8 (solution constraints).

These validators check custom rules that go beyond what pzprjs check() verifies.
Each game type with custom rules gets specific validator functions.
"""

import math
import re
from typing import Any, Optional


# ---------------------------------------------------------------------------
# R6 Move Ordering Validators
# ---------------------------------------------------------------------------

def validate_r6_sudoku(moves: list[str], grid_width: int, grid_height: int) -> dict:
    """R6: No consecutive same digit input.
    R8: Digit parity alternation (odd must follow even, etc.)."""
    violations = []
    last_digit = None
    last_parity = None  # 0=even, 1=odd

    for i, move in enumerate(moves):
        digit = _extract_sudoku_digit(move)
        if digit is None:
            continue

        if last_digit is not None and digit == last_digit:
            violations.append(f"Step {i}: digit {digit} same as previous (R6)")

        parity = digit % 2
        if last_parity is not None and parity == last_parity:
            violations.append(f"Step {i}: parity violation, digit {digit} same parity as previous (R8)")

        last_digit = digit
        last_parity = parity

    return {"valid": len(violations) == 0, "violations": violations, "rule": "R6+R8"}


def validate_r6_sudoku2(moves: list[str], grid_width: int, grid_height: int) -> dict:
    """R6: Row alternation -- consecutive entries in different rows.
    R7: Box alternation -- consecutive entries in different 3x3 boxes."""
    violations = []
    last_row = None
    last_box = None

    for i, move in enumerate(moves):
        row, col = _extract_cell_coords(move)
        if row is None:
            continue

        box = (row // 3, col // 3)

        if last_row is not None and row == last_row:
            violations.append(f"Step {i}: row {row} same as previous (R6)")
        if last_box is not None and box == last_box:
            violations.append(f"Step {i}: box {box} same as previous (R7)")

        last_row = row
        last_box = box

    return {"valid": len(violations) == 0, "violations": violations, "rule": "R6+R7"}


def validate_r6_heyawake(moves: list[str], rooms: Any, grid_width: int, grid_height: int) -> dict:
    """R6: No consecutive same-room shading."""
    violations = []
    last_room = None

    for i, move in enumerate(moves):
        row, col = _extract_cell_coords(move)
        if row is None:
            continue

        room = _get_room_for_cell(row, col, rooms)
        if last_room is not None and room == last_room and room is not None:
            violations.append(f"Step {i}: cell ({row},{col}) in same room {room} as previous (R6)")

        last_room = room

    return {"valid": len(violations) == 0, "violations": violations, "rule": "R6"}


def validate_r6_heyawake2(moves: list[str], grid_width: int, grid_height: int) -> dict:
    """R6: Half-grid alternation -- alternate between left half and right half."""
    violations = []
    last_half = None  # 'left' or 'right'
    mid = grid_width / 2

    for i, move in enumerate(moves):
        row, col = _extract_cell_coords(move)
        if row is None:
            continue

        half = "left" if col < mid else "right"
        if last_half is not None and half == last_half:
            violations.append(f"Step {i}: cell ({row},{col}) in same half '{half}' as previous (R6)")
        last_half = half

    return {"valid": len(violations) == 0, "violations": violations, "rule": "R6"}


def validate_r6_mines(moves: list[str], grid_width: int, grid_height: int) -> dict:
    """R6: No consecutive same-row reveals."""
    violations = []
    last_row = None

    for i, move in enumerate(moves):
        row, col = _extract_cell_coords(move)
        if row is None:
            continue

        if last_row is not None and row == last_row:
            violations.append(f"Step {i}: cell ({row},{col}) in same row {row} as previous (R6)")
        last_row = row

    return {"valid": len(violations) == 0, "violations": violations, "rule": "R6"}


def validate_r6_country(moves: list[str], rooms: Any, grid_width: int, grid_height: int) -> dict:
    """R6: No consecutive same-room lines."""
    violations = []
    last_room = None

    for i, move in enumerate(moves):
        row, col = _extract_line_start(move)
        if row is None:
            continue

        room = _get_room_for_cell(row, col, rooms)
        if last_room is not None and room == last_room and room is not None:
            violations.append(f"Step {i}: line in same room {room} as previous (R6)")
        last_room = room

    return {"valid": len(violations) == 0, "violations": violations, "rule": "R6"}


# ---------------------------------------------------------------------------
# R7-R8 Solution Constraint Validators
# ---------------------------------------------------------------------------

def validate_r7_sudoku(grid: list[list[int]], metadata: dict) -> dict:
    """R7: Killer cage -- 3x3 region sum must equal target.
    Cage info expected in metadata['killer_cage'] = {'box_row': r, 'box_col': c, 'target': n}."""
    cage = metadata.get("killer_cage")
    if not cage:
        return {"valid": True, "violations": [], "rule": "R7", "note": "no cage defined"}

    box_row = cage.get("box_row", 0)
    box_col = cage.get("box_col", 0)
    target = cage.get("target", 45)

    total = 0
    for r in range(box_row * 3, box_row * 3 + 3):
        for c in range(box_col * 3, box_col * 3 + 3):
            if r < len(grid) and c < len(grid[0]):
                total += grid[r][c]

    violations = []
    if total != target:
        violations.append(f"Killer cage sum={total}, expected={target}")
    return {"valid": len(violations) == 0, "violations": violations, "rule": "R7"}


def validate_r8_sudoku2(grid: list[list[int]]) -> dict:
    """R8: Every row must contain exactly 4 even digits."""
    violations = []
    for r, row in enumerate(grid):
        even_count = sum(1 for d in row if d % 2 == 0)
        if even_count != 4:
            violations.append(f"Row {r}: {even_count} even digits, expected 4")
    return {"valid": len(violations) == 0, "violations": violations, "rule": "R8"}


def validate_r7_heyawake(shaded: set[tuple[int, int]], grid_width: int, grid_height: int) -> dict:
    """R7: Row shade balance -- no row has more than ceil(cols/2) shaded."""
    violations = []
    limit = math.ceil(grid_width / 2)
    for r in range(grid_height):
        count = sum(1 for (rr, cc) in shaded if rr == r)
        if count > limit:
            violations.append(f"Row {r}: {count} shaded cells, max={limit}")
    return {"valid": len(violations) == 0, "violations": violations, "rule": "R7"}


def validate_r7_heyawake2(shaded: set[tuple[int, int]], grid_width: int, grid_height: int) -> dict:
    """R7: Column shade balance -- no column has more than ceil(rows/2) shaded."""
    violations = []
    limit = math.ceil(grid_height / 2)
    for c in range(grid_width):
        count = sum(1 for (rr, cc) in shaded if cc == c)
        if count > limit:
            violations.append(f"Col {c}: {count} shaded cells, max={limit}")
    return {"valid": len(violations) == 0, "violations": violations, "rule": "R7"}


def validate_r8_heyawake2(shaded: set[tuple[int, int]], grid_width: int, grid_height: int) -> dict:
    """R8: Shading density 10-50%."""
    total = grid_width * grid_height
    count = len(shaded)
    density = count / total if total > 0 else 0
    violations = []
    if density < 0.10:
        violations.append(f"Density {density:.1%} < 10%")
    if density > 0.50:
        violations.append(f"Density {density:.1%} > 50%")
    return {"valid": len(violations) == 0, "violations": violations, "rule": "R8"}


def validate_r7_mines(mine_cells: set[tuple[int, int]], grid_width: int, grid_height: int) -> dict:
    """R7: No 2x2 mine block."""
    violations = []
    for r in range(grid_height - 1):
        for c in range(grid_width - 1):
            if all((r + dr, c + dc) in mine_cells for dr in (0, 1) for dc in (0, 1)):
                violations.append(f"2x2 mine block at ({r},{c})")
    return {"valid": len(violations) == 0, "violations": violations, "rule": "R7"}


def validate_r8_mines(mine_cells: set[tuple[int, int]], grid_width: int, grid_height: int) -> dict:
    """R8: Mine density <= 25%."""
    total = grid_width * grid_height
    count = len(mine_cells)
    density = count / total if total > 0 else 0
    violations = []
    if density > 0.25:
        violations.append(f"Mine density {density:.1%} > 25%")
    return {"valid": len(violations) == 0, "violations": violations, "rule": "R8"}


def validate_r7_mines2(mine_cells: set[tuple[int, int]], grid_width: int, grid_height: int) -> dict:
    """R7: Row mine cap -- no row has more than ceil(2*cols/3) mines."""
    violations = []
    limit = math.ceil(2 * grid_width / 3)
    for r in range(grid_height):
        count = sum(1 for (rr, cc) in mine_cells if rr == r)
        if count > limit:
            violations.append(f"Row {r}: {count} mines, max={limit}")
    return {"valid": len(violations) == 0, "violations": violations, "rule": "R7"}


def validate_r8_mines2(mine_cells: set[tuple[int, int]], grid_width: int, grid_height: int) -> dict:
    """R8: No 2x2 mine block (same as mines R7)."""
    return validate_r7_mines(mine_cells, grid_width, grid_height)


def validate_r7_country(loop_cells: set[tuple[int, int]], grid_width: int, grid_height: int) -> dict:
    """R7: Minimum 50% loop coverage."""
    total = grid_width * grid_height
    count = len(loop_cells)
    coverage = count / total if total > 0 else 0
    violations = []
    if coverage < 0.50:
        violations.append(f"Loop coverage {coverage:.1%} < 50%")
    return {"valid": len(violations) == 0, "violations": violations, "rule": "R7"}


def validate_r8_country(loop_cells: set[tuple[int, int]], grid_width: int, grid_height: int) -> dict:
    """R8: At most 1 empty row."""
    empty_rows = 0
    for r in range(grid_height):
        row_cells = {(rr, cc) for (rr, cc) in loop_cells if rr == r}
        if len(row_cells) == 0:
            empty_rows += 1
    violations = []
    if empty_rows > 1:
        violations.append(f"{empty_rows} empty rows, max=1")
    return {"valid": len(violations) == 0, "violations": violations, "rule": "R8"}


def validate_r6_country2(loop_cells: set[tuple[int, int]], edges: list, grid_width: int, grid_height: int) -> dict:
    """R6 (solution): Turn balance -- turns <= 2 * straights."""
    turns = 0
    straights = 0
    # This needs the actual loop path, not just cells
    # Simplified: count from edge directions
    return {"valid": True, "violations": [], "rule": "R6", "note": "requires loop path analysis"}


def validate_r7_country2(loop_cells: set[tuple[int, int]], grid_width: int, grid_height: int) -> dict:
    """R7: Maximum 85% loop coverage."""
    total = grid_width * grid_height
    count = len(loop_cells)
    coverage = count / total if total > 0 else 0
    violations = []
    if coverage > 0.85:
        violations.append(f"Loop coverage {coverage:.1%} > 85%")
    return {"valid": len(violations) == 0, "violations": violations, "rule": "R7"}


def validate_r8_country2(loop_cells: set[tuple[int, int]], grid_width: int, grid_height: int) -> dict:
    """R8: At most 1 empty row."""
    return validate_r8_country(loop_cells, grid_width, grid_height)


def validate_r6_yajilin2(shaded_cells: set[tuple[int, int]], grid_width: int, grid_height: int) -> dict:
    """R6: Shaded cells must be on grid border."""
    violations = []
    for r, c in shaded_cells:
        if r > 0 and r < grid_height - 1 and c > 0 and c < grid_width - 1:
            violations.append(f"Shaded cell ({r},{c}) not on border")
    return {"valid": len(violations) == 0, "violations": violations, "rule": "R6"}


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def validate_move_ordering(pid: str, moves: list[str], puzzle_data: dict) -> dict:
    """Dispatch R6 validation by game type."""
    w = puzzle_data.get("width", 0)
    h = puzzle_data.get("height", 0)
    rooms = puzzle_data.get("metadata", {}).get("rooms")

    validators = {
        "sudoku": lambda: validate_r6_sudoku(moves, w, h),
        "sudoku2": lambda: validate_r6_sudoku2(moves, w, h),
        "heyawake": lambda: validate_r6_heyawake(moves, rooms, w, h),
        "heyawake2": lambda: validate_r6_heyawake2(moves, w, h),
        "mines": lambda: validate_r6_mines(moves, w, h),
        "country": lambda: validate_r6_country(moves, rooms, w, h),
    }

    if pid in validators:
        return validators[pid]()

    return {"valid": True, "violations": [], "rule": "R6", "note": f"no R6 validator for {pid}"}


def validate_solution_constraints(pid: str, puzzle_data: dict, solution_state: dict) -> dict:
    """Dispatch R7-R8 validation by game type.

    solution_state should contain parsed solution data:
      - grid: for sudoku (list[list[int]])
      - shaded: for heyawake (set of (r,c))
      - mine_cells: for mines (set of (r,c))
      - loop_cells: for country (set of (r,c))
      - shaded_cells: for yajilin2 (set of (r,c))
    """
    w = puzzle_data.get("width", 0)
    h = puzzle_data.get("height", 0)
    metadata = puzzle_data.get("metadata", {})
    results = []

    if pid == "sudoku":
        grid = solution_state.get("grid", [])
        results.append(validate_r7_sudoku(grid, metadata))
    elif pid == "sudoku2":
        grid = solution_state.get("grid", [])
        results.append(validate_r8_sudoku2(grid))
    elif pid == "heyawake":
        shaded = solution_state.get("shaded", set())
        results.append(validate_r7_heyawake(shaded, w, h))
    elif pid == "heyawake2":
        shaded = solution_state.get("shaded", set())
        results.append(validate_r7_heyawake2(shaded, w, h))
        results.append(validate_r8_heyawake2(shaded, w, h))
    elif pid == "mines":
        mines = solution_state.get("mine_cells", set())
        results.append(validate_r7_mines(mines, w, h))
        results.append(validate_r8_mines(mines, w, h))
    elif pid == "mines2":
        mines = solution_state.get("mine_cells", set())
        results.append(validate_r7_mines2(mines, w, h))
        results.append(validate_r8_mines2(mines, w, h))
    elif pid == "country":
        loop = solution_state.get("loop_cells", set())
        results.append(validate_r7_country(loop, w, h))
        results.append(validate_r8_country(loop, w, h))
    elif pid == "country2":
        loop = solution_state.get("loop_cells", set())
        results.append(validate_r7_country2(loop, w, h))
        results.append(validate_r8_country2(loop, w, h))
    elif pid == "yajilin2":
        shaded = solution_state.get("shaded_cells", set())
        results.append(validate_r6_yajilin2(shaded, w, h))

    if not results:
        return {"valid": True, "all_results": [], "note": f"no solution validators for {pid}"}

    all_valid = all(r["valid"] for r in results)
    all_violations = []
    for r in results:
        all_violations.extend(r.get("violations", []))

    return {"valid": all_valid, "all_results": results, "violations": all_violations}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_sudoku_digit(move: str) -> int | None:
    """Extract digit from a sudoku move string like 'mouse,left,3,5;key,7'."""
    parts = move.split(";")
    for part in parts:
        part = part.strip()
        if part.startswith("key,"):
            try:
                return int(part.split(",")[1])
            except (IndexError, ValueError):
                pass
    return None


def _extract_cell_coords(move: str) -> tuple[int | None, int | None]:
    """Extract (row, col) from a move string like 'mouse,left,bx,by'.
    Board coords: bx=2*col+1, by=2*row+1."""
    match = re.match(r"mouse,(?:left|right),(\d+),(\d+)", move)
    if match:
        bx, by = int(match.group(1)), int(match.group(2))
        col = (bx - 1) // 2
        row = (by - 1) // 2
        return row, col
    return None, None


def _extract_line_start(move: str) -> tuple[int | None, int | None]:
    """Extract starting cell from a line-drawing move like 'mouse,left,bx1,by1,bx2,by2'."""
    match = re.match(r"mouse,(?:left|right),(\d+),(\d+)", move)
    if match:
        bx, by = int(match.group(1)), int(match.group(2))
        col = (bx - 1) // 2
        row = (by - 1) // 2
        return row, col
    return None, None


def _get_room_for_cell(row: int, col: int, rooms: Any) -> int | None:
    """Look up which room a cell belongs to. rooms is a 2D list of room IDs."""
    if rooms is None:
        return None
    try:
        if row < len(rooms) and col < len(rooms[row]):
            return rooms[row][col]
    except (TypeError, IndexError):
        pass
    return None
