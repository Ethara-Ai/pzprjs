"""
ppbench Game Generator Template
================================

Standard template for creating new puzzle generators that conform to the
ppbench benchmarking pipeline.

Usage:
    1. Copy this file and rename to your game: e.g. `puzzle_akari.py`
    2. Replace all TODO markers with your game-specific logic
    3. Run: python your_file.py easy
    4. Add to dataset: python generate_morpheus_dataset.py <your_pid>

Auto-Discovery:
    `generate_morpheus_dataset.py` auto-discovers all Python files in games/**
    that export a function starting with `generate_`. No manual registration
    needed — just follow the naming convention.

    WHY this matters: If your generator function does NOT start with
    `generate_`, the dataset builder will silently skip your file and
    your puzzles will never appear in my_dataset.jsonl.

ppbench Contract:
    - Generator function receives a difficulty string ("easy", "medium", "hard")
    - Returns a single dict with ALL required fields (see below)
    - `generate_morpheus_dataset.py` encrypts `solution` → `solution_enc`
      before writing to my_dataset.jsonl; the harness decrypts at load time
    - Move strings use pzprjs board coordinates: bx = 2*col + 1, by = 2*row + 1

Required JSON Fields (ppbench will break without these):
    Top-level: puzzle_url, puzzlink_url, pid, sort_key, width, height, area,
               number_required_moves, number_total_solution_moves,
               source, metadata, created_at, solution

    source:    site_name, page_url, feed_type, published_at
    metadata:  has_structured_solution, cspuz_is_unique, db_w, db_h, level
    solution:  moves_full, moves_required, moves_hint

Critical Fields (used by ppbench harness at runtime):
    - puzzlink_url: The harness instantiates Puzzle.from_url(record["puzzlink_url"])
                    If missing/malformed, the puzzle won't load → benchmark crash
    - pid:          Used for filtering (--puzzle-types) and puzzle ID construction
                    If missing, dataset builder logs "PID DETECT FAIL" and skips
    - solution:     Contains the move lists. Encrypted before JSONL write.
                    If moves_full is empty, the benchmark has no ground truth

Current Games (7 active):
    - kshitiz/play_tidepool.py    → pid: tidepool     (shading puzzle)
    - kshitiz/play_paritypipes.py → pid: paritypipes  (edge/loop puzzle)
    - rahul/play_radiance.py      → pid: radiance     (mirror placement)
    - shabid/puzzle_gradientwalls.py → pid: gradientwalls (number placement)
    - shabid/puzzle_kageboshi.py  → pid: kageboshi    (shading puzzle)
    - shabid/puzzle_resonance.py  → pid: resonance    (click-cycling)
    - sar/puzzle_pairloop.py      → pid: pairloop     (edge/loop puzzle)
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
# mines, room_grid, solution_grid, bulbs, solution_mirrors, etc.)
#
# WHY _PUZZLES is needed:
#   Each difficulty must map to a pre-generated, SAT-verified puzzle instance.
#   If this is missing, there is nothing to benchmark — the dataset builder
#   calls your generate function once per difficulty and expects valid output.

_PUZZLES = {
    "easy": {
        "rows": 0,       # TODO: grid height in cells
        "cols": 0,       # TODO: grid width in cells
        "url_body": "",  # TODO: pzprjs URL-encoded puzzle body
        # TODO: add game-specific keys (shaded, clue_grid, solution, etc.)
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
# WHY _build_moves is needed:
#   The ppbench harness replays these moves against the pzprjs engine to verify
#   correctness. Without valid moves, the puzzle cannot be auto-checked and the
#   benchmark score is always 0. The harness calls Puzzle.send_move() for each
#   string, then Puzzle.is_complete() to verify the puzzle is solved.
#
#   If moves are wrong (bad coordinates, wrong click type), the puzzle engine
#   will not reach a solved state → benchmark reports FAIL for all models.
#
# Move format (pzprjs conventions):
#   Cell left-click:    "mouse,left,{bx},{by}"       (primary action: shade, place number, etc.)
#   Cell right-click:   "mouse,right,{bx},{by}"      (secondary: mark as empty/safe)
#   Multi-click cycle:  repeat "mouse,left,{bx},{by}" N times to cycle to state N
#   Edge/line segment:  "mouse,left,{bx1},{by1},{bx2},{by2}" (draw line between adjacent cells)
#   Key after click:    "mouse,left,{bx},{by};key,{digit}"
#
# Board coordinates:
#   Cell centers: bx = 2*col + 1, by = 2*row + 1  (odd numbers)
#   Horizontal edges: bx = 2*col + 1, by = 2*row   (between rows)
#   Vertical edges:   bx = 2*col,     by = 2*row + 1  (between cols)
#   Vertices:         bx = 2*col,     by = 2*row  (corners)

def _build_moves(rows, cols, **kwargs):
    """Build move lists from solution data.

    WHY this returns a 3-tuple:
      moves_full     = ALL moves to completely solve the puzzle (ground truth)
      moves_required = essential moves that CHANGE state (left-clicks, line draws)
      moves_hint     = auxiliary moves that CONFIRM state (right-click marks)
      Invariant:     moves_full = moves_required + moves_hint

    The benchmark uses number_required_moves to gauge puzzle difficulty and
    compare model performance. moves_hint are "nice to have" — they mark cells
    as definitively empty/safe but the puzzle is considered solved without them.

    If moves_required is empty but the puzzle has a solution, the benchmark
    will report 0 required moves → misleading difficulty metric.

    Common signatures used by existing games:
        _build_moves(rows, cols, shaded=[(r,c),...])           — shading puzzles (kageboshi, tidepool)
        _build_moves(rows, cols, solution=[(r,c,val),...])     — click-cycling (resonance)
        _build_moves(rows, cols, solution_grid=[[int,...]])    — number grids (gradientwalls)
        _build_moves(rows, cols, h_edges=[[]], v_edges=[[]])   — loop/edge puzzles (paritypipes)
        moves stored directly in _PUZZLES dict                 — pre-computed (pairloop)

    Returns:
        tuple: (moves_full, moves_required, moves_hint)
    """
    moves_required = []
    moves_hint = []

    # TODO: Build moves from your puzzle solution data
    #
    # Example A — shading puzzle (left-click shaded, right-click unshaded):
    #   shaded_set = set(kwargs.get("shaded", []))
    #   for r in range(rows):
    #       for c in range(cols):
    #           bx, by = 2 * c + 1, 2 * r + 1
    #           if (r, c) in shaded_set:
    #               moves_required.append(f"mouse,left,{bx},{by}")
    #           else:
    #               moves_hint.append(f"mouse,right,{bx},{by}")
    #
    # Example B — edge/loop puzzle (draw lines on edges):
    #   h_edges = kwargs.get("h_edges", [])
    #   for r in range(rows + 1):
    #       for c in range(cols):
    #           if h_edges[r][c] == 1:
    #               bx = 1 + c * 2
    #               by = r * 2
    #               moves_required.append(f"mouse,left,{bx},{by}")
    #
    # Example C — number placement (click to cycle to value):
    #   solution_grid = kwargs.get("solution_grid", [])
    #   for r in range(rows):
    #       for c in range(cols):
    #           val = solution_grid[r][c]
    #           if val > 0:
    #               bx, by = 2 * c + 1, 2 * r + 1
    #               for _ in range(val):
    #                   moves_required.append(f"mouse,left,{bx},{by}")

    moves_full = moves_required + moves_hint
    return moves_full, moves_required, moves_hint


# =============================================================================
# SOLUTION VERIFIER (optional but strongly recommended)
# =============================================================================
# Verify that the hardcoded solution data actually satisfies puzzle rules.
#
# WHY _verify_solution is recommended:
#   If puzzle data is entered incorrectly (typo in shaded cells, wrong clue
#   value), the moves will replay on the pzprjs engine but the engine will
#   report "NOT SOLVED" because its internal rules disagree. This produces
#   a confusing situation where your file LOOKS correct but benchmarks always
#   fail. The verifier catches this at generation time with a clear error.
#
#   Without it: silent corruption — the dataset contains unsolvable entries
#   and every benchmark run reports 0% solve rate for your puzzle.
#
#   See play_tidepool.py for a complete verifier example (connectivity check,
#   2x2 block check, BFS depth check against clues).

def _verify_solution(puzzle_data):
    """Verify hardcoded solution satisfies puzzle rules.

    Args:
        puzzle_data: One entry from _PUZZLES dict

    Returns:
        True if solution is valid, False otherwise

    TODO: Implement game-specific constraint checks.
    """
    # Example checks (adapt to your puzzle):
    # - No 2x2 shaded blocks
    # - Connected white cells
    # - Clue numbers match adjacent shaded count
    # - Loop is single connected cycle
    return True


# =============================================================================
# GENERATOR (ppbench entry point)
# =============================================================================
# This is the function auto-discovered by generate_morpheus_dataset.py.
#
# WHY this function exists:
#   It is the SOLE interface between your puzzle and the benchmarking pipeline.
#   generate_morpheus_dataset.py calls this function 3 times (once per
#   difficulty) and writes each returned dict as a line in my_dataset.jsonl.
#
#   If this function:
#     - Doesn't start with "generate_" → file is silently skipped
#     - Returns None → dataset builder logs "GEN FAIL" error
#     - Raises an exception → same, logged as error, puzzle excluded
#     - Returns dict missing "pid" → builder logs "PID DETECT FAIL"
#     - Returns dict missing "puzzlink_url" → harness crashes at runtime
#     - Returns empty moves → benchmark always reports 0% solve rate
#
# NAMING CONVENTION (both work, pick one):
#     generate_puzzle_{name}  — used by: puzzle_pairloop, puzzle_gradientwalls,
#                               puzzle_kageboshi, puzzle_resonance
#     generate_custom_{name}  — used by: play_tidepool, play_paritypipes,
#                               play_radiance
#
# The function MUST:
#   - Accept a single `difficulty` parameter ("easy" / "medium" / "hard")
#   - Return a dict with ALL required ppbench fields
#   - Never return None for number_required_moves or number_total_solution_moves

_PID = "your_pid"  # TODO: must match your puzzle's pzprjs variety name

def generate_puzzle_template(difficulty="easy"):
    """Generate a single puzzle instance for ppbench.

    TODO: Rename this function to match your game:
        generate_puzzle_{name}  OR  generate_custom_{name}

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

    # Verify solution integrity (catches data entry errors early)
    if not _verify_solution(p):
        return {"error": f"hardcoded solution for {level} does not verify"}

    # Build the puzzle URL
    # WHY puzzle_url format matters:
    #   The pzprjs engine parses the URL to determine puzzle type, grid size,
    #   and initial clue state. Format: http://localhost:8000/p.html?{pid}/{cols}/{rows}/{body}
    #   - localhost:8000 is where the local pzprjs player runs during benchmarks
    #   - {pid} must match a registered variety in pzprjs/src/pzpr/variety.js
    #   - {cols}/{rows} define the grid (NOTE: width first, then height)
    #   - {body} is the URL-encoded puzzle data (clues, regions, etc.)
    puzzle_url = f"http://localhost:8000/p.html?{_PID}/{cols}/{rows}/{url_body}"

    # Build move lists from solution data
    # TODO: pass the right kwargs for your _build_moves signature
    moves_full, moves_required, moves_hint = _build_moves(
        rows, cols,
        # shaded=p.get("shaded"),
        # solution_grid=p.get("solution"),
        # solution_mirrors=p.get("solution_mirrors"),
    )

    now = datetime.now(timezone.utc).isoformat()

    return {
        # --- Core identifiers ---
        # WHY puzzle_url: The local URL where pzprjs serves this puzzle. Used by
        # the harness to instantiate the JavaScript puzzle engine.
        "puzzle_url": puzzle_url,

        # WHY puzzlink_url: The URL the benchmark harness passes to Puzzle.from_url().
        # This is THE critical field — if wrong, the puzzle won't load.
        # For local-only puzzles, this equals puzzle_url. For publicly hosted
        # puzzles, this could be a puzz.link or pzprxs.vercel.app URL.
        "puzzlink_url": puzzle_url,

        # WHY pid: Puzzle type identifier. Used by:
        #   - Dataset builder: groups puzzles, detects duplicates
        #   - Benchmark harness: --puzzle-types filter, RunResult.puzzle_id construction
        #   - Puzzle.from_url(): pzprjs uses this to load the correct variety script
        "pid": _PID,

        # sort_key: Optional ordering hint (None = natural order)
        "sort_key": None,

        # --- Dimensions ---
        # WHY width/height: Used by harness for logging and result metadata.
        # Also cross-referenced with puzzle URL dimensions for sanity.
        "width": cols,
        "height": rows,
        "area": rows * cols,

        # --- Move counts (MUST be int, never None) ---
        # WHY these counts: The benchmark uses number_required_moves to:
        #   1. Gauge puzzle difficulty (more moves = harder)
        #   2. Calculate solve efficiency (model_moves / required_moves)
        #   3. Filter puzzles by complexity for different benchmark tiers
        # If these are 0 or None, statistics break silently.
        "number_required_moves": len(moves_required),
        "number_total_solution_moves": len(moves_full),

        # --- Source metadata ---
        # WHY source: Provenance tracking. The harness doesn't use this at runtime
        # but it's required for dataset auditability and publishing.
        "source": {
            "site_name": "ppbench_golden",
            "page_url": None,
            "feed_type": "golden_dataset",
            "published_at": now,
        },

        # --- Puzzle metadata ---
        # WHY metadata: Enriches analysis — level is used for difficulty filtering,
        # cspuz_is_unique confirms the puzzle has exactly one solution (SAT-verified),
        # has_structured_solution flags whether moves_full actually solves the puzzle.
        "metadata": {
            "has_structured_solution": True,
            "cspuz_is_unique": None,  # Set True if SAT-verified, False if not, None if unchecked
            "db_w": cols,
            "db_h": rows,
            "level": level,
            # TODO: add game-specific metadata (num_clues, num_regions, etc.)
            # Examples from existing games:
            #   "num_shaded": len(p["shaded"]),          — kageboshi
            #   "num_clues": len(p["clues"]),            — gradientwalls, resonance
            #   "num_mirror_slots": len(slots),          — radiance
            #   "num_black_vertices": num_black,         — paritypipes
            #   "num_arrows": p["num_arrows"],           — pairloop
        },

        # --- Timestamps ---
        "created_at": now,

        # --- Solution ---
        # WHY solution: This is the ground truth. generate_morpheus_dataset.py
        # encrypts this as solution_enc in the JSONL. The harness decrypts it at
        # load time to access moves for verification and scoring.
        #
        # If moves_full doesn't actually solve the puzzle when replayed, the
        # benchmark treats this puzzle as broken (always FAIL).
        "solution": {
            "moves_full": moves_full,
            "moves_required": moves_required,
            "moves_hint": moves_hint,
        },
    }


# =============================================================================
# CLI (for manual testing)
# =============================================================================
# WHY CLI matters:
#   Before adding your puzzle to the dataset, you MUST test it locally:
#     python your_file.py easy
#   This verifies:
#     1. No import errors or crashes
#     2. JSON output is well-formed
#     3. Move counts look reasonable (not 0)
#     4. URL is well-formed (can paste into browser to check visually)
#
#   If you skip this step and run generate_morpheus_dataset.py directly,
#   errors are silently caught and your puzzle is excluded with a one-line
#   log message that's easy to miss.

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
    print(f"# Play: {data['puzzle_url']}", file=sys.stderr)
