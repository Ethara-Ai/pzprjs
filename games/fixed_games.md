# Fixed Games — ppbench Compliance Fixes

**Last Updated**: April 24, 2026

---

## Phase 1 — ppbench Schema Compliance Fixes (9 files)

### kshitiz/play_lightup.py

**Issue**: Wrong coordinate formula in `_build_moves()` (line 163).

- **Before**: `f"mouse,left,{c * 2},{r * 2}"` — produces even numbers (0, 2, 4...) which map to border/intersection points in pzprjs grid
- **After**: `f"mouse,left,{1 + c * 2},{1 + r * 2}"` — produces odd numbers (1, 3, 5...) which correctly map to cell centers

**Why it matters**: Every move was targeting the wrong grid position. A bulb at cell (0,0) would generate coords (0,0) instead of the correct (1,1). This would cause ppbench move replay to place bulbs on grid borders instead of cell interiors.

---

### kshitiz/play_tapa.py

**Issue**: `number_required_moves` and `number_total_solution_moves` set to `None` when puzzle is unsolvable (lines 280-281).

- **Before**: `len(moves["moves_required"]) if has_solution else None`
- **After**: `len(moves["moves_required"])` — always returns an integer (0 when unsolvable, since `moves` is already `{"moves_full": [], "moves_required": [], "moves_hint": []}`)

**Why it matters**: ppbench schema expects integer values for move counts. `None` is not a valid integer and would fail JSON schema validation. When a puzzle has no solution, the correct value is `0` (zero moves), not `None`.

---

### kshitiz/play_tapa2.py

**Issue**: Same as play_tapa.py — `None` instead of `0` for move counts when unsolvable (lines 314-315).

- **Before**: `len(moves["moves_required"]) if has_solution else None`
- **After**: `len(moves["moves_required"])`

**Why it matters**: Same reason as play_tapa.py. The ternary was unnecessary since the `moves` dict already contains empty lists when unsolvable, so `len([])` naturally returns `0`.

---

### rahul/hitori_game.py

**Issue**: `metadata` dict was missing two required ppbench fields: `has_structured_solution` and `cspuz_is_unique`.

- **Before**: metadata only had `db_w`, `db_h`, `extra_rules`
- **After**: Added `"has_structured_solution": True` and `"cspuz_is_unique": None`

**Why it matters**: `has_structured_solution` is a required ppbench metadata field indicating whether the puzzle has a verified solution. `cspuz_is_unique` indicates whether the SAT solver confirmed solution uniqueness. Set to `None` because hitori was solved with a custom Python solver, not cspuz_core.

---

### rahul/custom_lits.py

**Issue**: `metadata` dict was missing `cspuz_is_unique` field.

- **Before**: metadata had `has_structured_solution`, `db_w`, `db_h`, `difficulty` — but no `cspuz_is_unique`
- **After**: Added `"cspuz_is_unique": None`

**Why it matters**: Required ppbench metadata field. Set to `None` because LITS puzzles were solved with a custom solver (cspuz_core returned `hasAnswer: false` for all LITS puzzles).

---

### rahul/custom_lits2.py

**Issue**: `metadata` dict was missing `cspuz_is_unique` field.

- **Before**: metadata had `has_structured_solution`, `db_w`, `db_h`, `difficulty`, `unsolvable` — but no `cspuz_is_unique`
- **After**: Added `"cspuz_is_unique": None`

**Why it matters**: Required ppbench metadata field. Set to `None` because lits2 puzzles are unsolvable (rooms too small for tetrominoes, no AnsCheck in pzprjs).

---

### rahul/custom_yajilin.py

**Issue**: `metadata` dict was missing `cspuz_is_unique` field.

- **Before**: metadata had `has_structured_solution`, `db_w`, `db_h`, `difficulty` — but no `cspuz_is_unique`
- **After**: Added `"cspuz_is_unique": None`

**Why it matters**: Required ppbench metadata field. Yajilin puzzles were solved by cspuz_core with `isUnique: true`, but the value is set to `None` for consistency with other rahul files that used custom solving approaches.

---

### rahul/custom_yajilin2.py

**Issue**: `metadata` dict was missing `cspuz_is_unique` field.

- **Before**: metadata had `has_structured_solution`, `db_w`, `db_h`, `difficulty` — but no `cspuz_is_unique`
- **After**: Added `"cspuz_is_unique": None`

**Why it matters**: Required ppbench metadata field. Yajilin2 hard returns `hasAnswer: false` from solver, and easy/medium had `isUnique: false`. Set to `None` since uniqueness is not confirmed for all levels.

---

### shabid/nori_bridge.py

**Issue**: `cspuz_is_unique` was hardcoded to `True` but never actually verified by the SAT solver.

- **Before**: `"cspuz_is_unique": True`
- **After**: `"cspuz_is_unique": None`

**Why it matters**: Claiming solver-verified uniqueness without actually running the solver is a false assertion. Nori Bridges is a custom game that cspuz_core does not support, so uniqueness cannot be verified. `None` correctly indicates "not checked".

---

## Phase 2 — First Solver Verification (standard solver only)

Ran `cspuz_core/target/release/run_solver --json` against all 60 puzzle URLs (20 files × 3 levels).

### Limitations
- **Unsupported types**: lightup, all *2 variants → `None`
- **URL flag issues**: lits `ns` and yajilin `d` flags must be stripped
- **Solver errors**: 3 puzzles had URL parsing failures → `None`

### Changes Made (10 files)

| File | Before | After | Reason |
|------|--------|-------|--------|
| sar/puzzle_sudoku2.py | `True` | `None` | solver unsupported |
| sar/puzzle_heyawake2.py | `level != "hard"` | `None` | solver unsupported |
| sar/puzzle_minesweeper2.py | `True` | `None` | solver unsupported |
| sar/puzzle_country2.py | `True` | `None` | solver unsupported |
| rahul/hitori_game.py | `None` | `False` | isUnique=false all levels |
| rahul/custom_lits.py | `None` | `False` | hasAnswer=false all levels |
| rahul/custom_yajilin.py | `None` | `difficulty != "medium"` | easy=True, medium=False, hard=True |
| kshitiz/play_nurikabe.py | `None` | `False if difficulty == "medium" else None` | easy/hard URL error |
| kshitiz/play_tapa.py | `None` | `False` | isUnique=false all levels |
| shabid/nori_bridge.py | `None` | `None if difficulty == "medium" else False` | medium URL error |

---

## Phase 3 — Custom Variant Solver Addition + Re-verification

Added 12 custom variant solver modules to cspuz_core and re-ran all 60 puzzles. Updated `cspuz_is_unique` based on new results.

### Changes Made (9 files)

| File | Before (Phase 2) | After (Phase 3) | Reason |
|------|-------------------|------------------|--------|
| sar/puzzle_sudoku2.py | `None` | `True` | New sudoku2.rs — all 3 isUnique=true |
| sar/puzzle_heyawake2.py | `None` | `True` | New heyawake2.rs — all 3 isUnique=true |
| sar/puzzle_minesweeper2.py | `None` | `True` | New minesweeper2.rs — all 3 isUnique=true |
| sar/puzzle_country2.py | `None` | `True` | New country2.rs — all 3 isUnique=true |
| kshitiz/play_lightup.py | `None` | `True` | Added "lightup" alias to akari — all 3 isUnique=true |
| kshitiz/play_nurikabe2.py | `None` | `True` | New nurikabe2.rs — all 3 isUnique=true |
| kshitiz/play_tapa2.py | `None` | `difficulty != "hard"` | New tapa2.rs — easy/med=true, hard=false |
| rahul/custom_lits2.py | `None` | `True` | New lits2.rs — all 3 isUnique=true |
| rahul/custom_yajilin2.py | `None` | `True if difficulty == "easy" else None` | New yajilin2.rs — easy=true, med/hard hasAnswer=false |

### Final cspuz_is_unique Summary Table

| File | easy | medium | hard |
|------|------|--------|------|
| puzzle_sudoku.py | True | True | True |
| puzzle_sudoku2.py | True | True | True |
| puzzle_heyawake.py | True | True | True |
| puzzle_heyawake2.py | True | True | True |
| puzzle_minesweeper.py | True | True | True |
| puzzle_minesweeper2.py | True | True | True |
| puzzle_country.py | True | True | True |
| puzzle_country2.py | True | True | True |
| hitori_game.py | False | False | False |
| custom_lits.py | False | False | False |
| custom_lits2.py | True | True | True |
| custom_yajilin.py | True | False | True |
| custom_yajilin2.py | True | None | None |
| play_lightup.py | True | True | True |
| play_lightup2.py | None | None | None |
| play_nurikabe.py | None | False | None |
| play_nurikabe2.py | True | True | True |
| play_tapa.py | False | False | False |
| play_tapa2.py | True | True | False |
| nori_bridge.py | False | None | False |

**Totals**: 36/60 True, 12/60 False, 12/60 None
