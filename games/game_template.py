"""
ppbench Game Generator Template
================================

Standard template for creating new puzzle generators that conform to the
ppbench benchmarking pipeline.

Usage:
    1. Copy this file and rename to your game: e.g. `puzzle_akari.py`
    2. Replace all TODO markers with your game-specific logic
    3. Register in `traces/generate_dataset.py` GAME_REGISTRY
    4. Run: python your_file.py easy

ppbench Contract:
    - Generator function receives a difficulty string ("easy", "medium", "hard")
    - Returns a single dict with ALL required fields (see below)
    - `generate_dataset.py` injects `puzzle_id` automatically — do NOT add it
    - Move strings use pzprjs board coordinates: bx = 2*col + 1, by = 2*row + 1

Required JSON Fields:
    Top-level: puzzle_url, puzzlink_url, pid, sort_key, width, height, area,
               number_required_moves, number_total_solution_moves,
               source, metadata, created_at, solution

    source:    site_name, page_url, feed_type, published_at
    metadata:  has_structured_solution, cspuz_is_unique, db_w, db_h, level
    solution:  moves_full, moves_required, moves_hint
"""

import json
import sys
import time
from datetime import datetime, timezone


# =============================================================================
# PUZZLE DATA
# =============================================================================
# Define one entry per difficulty. Each entry must have at minimum:
#   rows, cols, url_body — used to build the puzzle URL and grid dimensions
#
# Add any game-specific keys needed by _build_moves() (e.g. shaded, clue_grid,
# mines, room_grid, solution_grid, bulbs, etc.)

_PUZZLES = {
    "easy": {
        "rows": 0,       # TODO: grid height in cells
        "cols": 0,       # TODO: grid width in cells
        "url_body": "",  # TODO: pzprjs URL-encoded puzzle body
        # TODO: add game-specific keys (shaded, clue_grid, etc.)
    },
    "medium": {
        "rows": 0,
        "cols": 0,
        "url_body": "",
    },
    "hard": {
        "rows": 0,
        "cols": 0,
        "url_body": "",
    },
}


# =============================================================================
# MOVE BUILDER
# =============================================================================
# Convert puzzle solution data into pzprjs move strings.
#
# Move format examples:
#   Cell left-click:    "mouse,left,{bx},{by}"
#   Cell right-click:   "mouse,right,{bx},{by}"
#   Key after click:    "mouse,left,{bx},{by};key,{digit}"
#   Line drag:          "mouse,left,{bx1},{by1},{bx2},{by2}"
#
# Board coordinates: bx = 2*col + 1, by = 2*row + 1 (odd = cell center)

def _build_moves(rows, cols, **kwargs):
    """Build move lists from solution data.

    TODO: Adjust parameters to match your game's solution data.
    Common signatures across existing games:
        (rows, cols, shaded)                — shading puzzles
        (clue_grid, solution_grid)          — number placement
        (rows, cols, mines)                 — minesweeper-style
        (rows, cols, solution)              — generic 2D solution grid
        (rows, cols, grid, bulbs)           — lightup-style
        (border_segments, bridges)          — graph-based

    Returns:
        tuple: (moves_full, moves_required, moves_hint)
            moves_full     = ALL moves to completely solve the puzzle
            moves_required = essential moves (usually left-clicks)
            moves_hint     = auxiliary moves (usually right-clicks / marks)
            Relationship:  moves_full = moves_required + moves_hint
    """
    moves_required = []
    moves_hint = []

    # TODO: Build moves from your puzzle solution data
    #
    # Example for a shading puzzle:
    #   shaded = kwargs.get("shaded", [])
    #   for (r, c) in shaded:
    #       bx, by = 2 * c + 1, 2 * r + 1
    #       moves_required.append(f"mouse,left,{bx},{by}")
    #   for r in range(rows):
    #       for c in range(cols):
    #           if (r, c) not in shaded_set:
    #               bx, by = 2 * c + 1, 2 * r + 1
    #               moves_hint.append(f"mouse,right,{bx},{by}")

    moves_full = moves_required + moves_hint
    return moves_full, moves_required, moves_hint


# =============================================================================
# GENERATOR (ppbench entry point)
# =============================================================================
# This is the function registered in GAME_REGISTRY. It MUST:
#   - Accept a single `difficulty` parameter ("easy" / "medium" / "hard")
#   - Return a dict with ALL required ppbench fields
#   - Never return None for number_required_moves or number_total_solution_moves

_PID = "your_pid"  # TODO: must match traces/custom_rules.yaml key and GAME_REGISTRY

def generate_puzzle_template(difficulty):
    """Generate a single puzzle instance for ppbench.

    TODO: Rename this function to match your game:
        generate_puzzle_{name}  (for sar/shabid convention)
        generate_custom_{name}  (for rahul/kshitiz convention)

    Args:
        difficulty: One of "easy", "medium", "hard"

    Returns:
        dict: Complete ppbench puzzle record
    """
    level = difficulty
    p = _PUZZLES[level]

    rows = p["rows"]
    cols = p["cols"]
    url_body = p["url_body"]

    # Build the puzzle URL
    puzzle_url = f"http://localhost:8000/p.html?{_PID}/{cols}/{rows}/{url_body}"

    # Build move lists from solution data
    # TODO: pass the right kwargs for your _build_moves signature
    moves_full, moves_required, moves_hint = _build_moves(
        rows, cols,
        # shaded=p.get("shaded"),
        # solution_grid=p.get("solution_grid"),
    )

    now = datetime.now(timezone.utc).isoformat()

    return {
        # --- Core identifiers ---
        "puzzle_url": puzzle_url,
        "puzzlink_url": puzzle_url,
        "pid": _PID,
        "sort_key": None,

        # --- Dimensions ---
        "width": cols,
        "height": rows,
        "area": rows * cols,

        # --- Move counts (MUST be int, never None) ---
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),

        # --- Source metadata ---
        "source": {
            "site_name": "ppbench_golden",
            "page_url": None,
            "feed_type": "golden_dataset",
            "published_at": now,
        },

        # --- Puzzle metadata ---
        "metadata": {
            "has_structured_solution": True,
            "cspuz_is_unique": None,  # Set True if SAT-verified, False if not, None if unchecked
            "db_w": cols,
            "db_h": rows,
            "level": level,
            # TODO: add game-specific metadata (num_rooms, clue_count, etc.)
        },

        # --- Timestamps ---
        "created_at": now,

        # --- Solution ---
        "solution": {
            "moves_full": moves_full,
            "moves_required": moves_required,
            "moves_hint": moves_hint,
        },
    }


# =============================================================================
# CLI (for manual testing)
# =============================================================================
# Usage: python game_template.py <difficulty>
#        python game_template.py easy

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <easy|medium|hard>")
        sys.exit(1)

    level = sys.argv[1]
    if level not in ("easy", "medium", "hard"):
        print(f"Invalid difficulty: {level}. Must be one of: easy, medium, hard")
        sys.exit(1)

    start = time.time()
    data = generate_puzzle_template(level)  # TODO: rename to your function
    elapsed = time.time() - start

    print(json.dumps(data, indent=2, default=str))
    print(f"\n# {_PID} [{level}] — {data['width']}x{data['height']}, "
          f"{data['number_required_moves']} required moves, "
          f"{data['number_total_solution_moves']} total moves, "
          f"generated in {elapsed:.2f}s", file=sys.stderr)
