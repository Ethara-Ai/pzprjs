# Game Files Audit — All Differences

> Comprehensive diff across all 20 generator files in `games/{sar,rahul,kshitiz,shabid}/`

---

## 1. Imports

| Pattern | Files | Count |
|---------|-------|-------|
| `import json`, `import sys`, `import time`, `from datetime import datetime, timezone` | All except 2 below | 18/20 |
| MISSING `import sys`, `import time` | `custom_lits2.py`, `custom_yajilin2.py` | 2/20 |
| EXTRA `from collections import deque` | `play_nurikabe.py` | 1/20 |

---

## 2. Puzzle Data Structure

| Pattern | Files | Count |
|---------|-------|-------|
| `_PUZZLES = {"easy": {...}, "medium": {...}, "hard": {...}}` | All except nori_bridge | 19/20 |
| Separate `_EASY`, `_MEDIUM`, `_HARD` vars consolidated inside function | `nori_bridge.py` | 1/20 |

---

## 3. Generator Function Naming

| Author | Convention | Example |
|--------|-----------|---------|
| sar | `generate_puzzle_{name}` | `generate_puzzle_sudoku` |
| rahul | `generate_custom_{name}` | `generate_custom_yajilin` |
| kshitiz | `generate_custom_{name}` | `generate_custom_tapa` |
| shabid | `generate_puzzle_{name}` | `generate_puzzle_nori_bridges2` |

---

## 4. Puzzle Data Keys Per Difficulty

Beyond the common `rows`, `cols`, `url_body`:

| File | Extra Keys |
|------|-----------|
| `puzzle_sudoku.py` | `clue_grid`, `solution_grid` (NO rows/cols — fixed 9×9) |
| `puzzle_sudoku2.py` | `clue_grid`, `solution_grid` (NO rows/cols — fixed 9×9) |
| `puzzle_heyawake.py` | `room_grid`, `clues`, `shaded` |
| `puzzle_heyawake2.py` | `shaded` |
| `puzzle_minesweeper.py` | `num_mines`, `mines` |
| `puzzle_minesweeper2.py` | `num_mines`, `mines` |
| `puzzle_country.py` | `room_grid`, `clues`, `moves_required`, `moves_hint` |
| `puzzle_country2.py` | `moves_required`, `moves_hint` |
| `hitori_game.py` | `shaded` |
| `custom_yajilin.py` | `shaded` |
| `custom_lits.py` | `room_grid`, `shaded` |
| `custom_lits2.py` | *(minimal — only `rows`, `cols`, `url_body`)* |
| `custom_yajilin2.py` | `moves_required`, `moves_hint` |
| `play_lightup.py` | *(minimal — has internal solver)* |
| `play_lightup2.py` | `bulbs` |
| `play_tapa.py` | *(minimal — has internal solver)* |
| `play_tapa2.py` | `shaded` (hard only, fallback) |
| `play_nurikabe.py` | *(minimal — has internal solver)* |
| `play_nurikabe2.py` | *(minimal — has internal solver)* |
| `nori_bridge.py` | `room_grid`, `region_numbers`, `bridges` |

---

## 5. Solution Strategy

| Strategy | Files |
|----------|-------|
| **Pre-computed in `_PUZZLES`** | `puzzle_sudoku.py`, `puzzle_sudoku2.py`, `puzzle_heyawake.py`, `puzzle_heyawake2.py`, `puzzle_minesweeper.py`, `puzzle_minesweeper2.py`, `puzzle_country.py`, `puzzle_country2.py`, `hitori_game.py`, `custom_yajilin.py`, `custom_lits.py`, `custom_yajilin2.py`, `play_lightup2.py` |
| **Internal solver** | `play_lightup.py`, `play_tapa.py`, `play_tapa2.py`, `play_nurikabe.py`, `play_nurikabe2.py` |
| **Verify + build from data** | `nori_bridge.py` |
| **No solution (unsolvable)** | `custom_lits2.py` |

---

## 6. `_build_moves()` Signature Variations

| Signature | Files |
|-----------|-------|
| `(rows, cols, shaded)` | `puzzle_heyawake2.py`, `hitori_game.py`, `custom_yajilin.py` |
| `(clue_grid, solution_grid)` | `puzzle_sudoku.py`, `puzzle_sudoku2.py` |
| `(rows, cols, shaded, room_grid, clues)` | `puzzle_heyawake.py`, `custom_lits.py` |
| `(rows, cols, mines)` | `puzzle_minesweeper.py`, `puzzle_minesweeper2.py` |
| `(border_segments, bridges)` | `nori_bridge.py` |
| `(rows, cols, solution)` | `play_tapa.py`, `play_tapa2.py`, `play_nurikabe.py`, `play_nurikabe2.py` |
| `(rows, cols, grid, bulbs)` | `play_lightup.py` |
| `(rows, cols, bulbs)` | `play_lightup2.py` |
| **No `_build_moves` (pre-computed)** | `puzzle_country.py`, `puzzle_country2.py`, `custom_yajilin2.py`, `custom_lits2.py` |

---

## 7. `source.site_name`

| Value | Files | Count |
|-------|-------|-------|
| `"ppbench_golden"` | All except 4 below | 16/20 |
| `"custom_generated"` | `play_tapa.py`, `play_tapa2.py`, `custom_lits2.py`, `custom_yajilin2.py` | 4/20 |

---

## 8. `source.feed_type`

| Value | Files | Count |
|-------|-------|-------|
| `"golden_dataset"` | All except 4 below | 16/20 |
| `"generated"` | `play_tapa.py`, `play_tapa2.py`, `custom_lits2.py`, `custom_yajilin2.py` | 4/20 |

---

## 9. `metadata.level` vs `metadata.difficulty`

| Pattern | Files |
|---------|-------|
| `"level": level` | sar files, `hitori_game.py`, `custom_yajilin.py`, `nori_bridge.py` |
| `"difficulty": difficulty` | `custom_lits.py`, `custom_lits2.py`, `custom_yajilin2.py` |
| No level/difficulty key | `play_tapa.py`, `play_tapa2.py`, `play_lightup.py`, `play_lightup2.py`, `play_nurikabe.py`, `play_nurikabe2.py` |

---

## 10. Extra Metadata Fields (Game-Specific)

| File | Extra Fields |
|------|-------------|
| `puzzle_sudoku.py` / `puzzle_sudoku2.py` | `clue_count` |
| `puzzle_heyawake.py` | `num_rooms`, `rooms` (2D grid) |
| `puzzle_heyawake2.py` | `num_rooms` |
| `puzzle_minesweeper.py` / `puzzle_minesweeper2.py` | `num_mines` |
| `puzzle_country.py` | `num_rooms`, `rooms` |
| `puzzle_country2.py` | `num_rooms` |
| `hitori_game.py` | `num_shaded`, `extra_rules` |
| `custom_lits.py` | `num_rooms`, `num_shaded` |
| `custom_lits2.py` | `unsolvable: True` |
| `custom_yajilin.py` | `num_shaded` |
| `custom_yajilin2.py` | *(none extra)* |
| `play_lightup.py` / `play_lightup2.py` | `num_walls`, `num_numbered_walls`, `num_bulbs` |
| `play_nurikabe.py` / `play_nurikabe2.py` | `num_clue_cells`, `num_clue_sum` |
| `play_tapa.py` / `play_tapa2.py` | `num_clue_cells` |
| `nori_bridge.py` | `num_regions`, `num_numbered_regions`, `num_bridges`, `custom_rules` |

---

## 11. `__main__` Block Variations

| Pattern | Files | Count |
|---------|-------|-------|
| Single difficulty via `sys.argv[1]`, print JSON + metadata | Most files | 16/20 |
| Iterate all difficulties if no arg specified | `custom_lits2.py`, `custom_yajilin2.py` | 2/20 |
| Supports `"all"` as level arg | `nori_bridge.py` | 1/20 |
| No `__main__` block | *(none)* | 0/20 |

---

## 12. `moves_hint` Always Empty

| Files with empty `moves_hint` for all difficulties |
|-----------------------------------------------------|
| `custom_yajilin2.py`, `custom_lits2.py`, `play_lightup2.py` |

---

## Summary of Non-Conformances (vs Standard Pattern)

| Issue | Affected Files | Severity |
|-------|---------------|----------|
| Missing `import sys`, `import time` | `custom_lits2.py`, `custom_yajilin2.py` | Low (still works) |
| No `level` key in metadata | kshitiz files (6 total) | Medium (inconsistency) |
| Uses `"difficulty"` instead of `"level"` | `custom_lits.py`, `custom_lits2.py`, `custom_yajilin2.py` | Medium (inconsistency) |
| `site_name` = `"custom_generated"` instead of `"ppbench_golden"` | 4 files | Low (intentional) |
| `feed_type` = `"generated"` instead of `"golden_dataset"` | 4 files | Low (intentional) |
| Non-standard puzzle data structure | `nori_bridge.py` | Low (works correctly) |
