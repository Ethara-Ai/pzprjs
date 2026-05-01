# cspuz Solver Solutions — All 21 Puzzles (Localhost)

**Solver**: `/Users/apple/Desktop/morpheus/cspuz_core/target/release/run_solver --json`
**URL Host**: `http://localhost:8000/p.html?` (all URLs use localhost, matching game file output)
**Date**: May 2026
**Last Updated**: May 1, 2026 (v4) — Codebase cleanup: removed all `*2` and `*_custom` variants. 7 active games remain, all 21 puzzles verified unique.

---

## Table of Contents

1. [Overview & Summary Table](#overview--summary-table)
2. [Solver Support Matrix](#solver-support-matrix)
3. [Cleanup Summary (v4)](#cleanup-summary-v4)
4. [Key Findings](#key-findings)

---

## Overview & Summary Table

All URLs below use `http://localhost:8000/p.html?{pid}/{w}/{h}/{body}` format.

| # | Game File | PID | Level | Size | Solver Module | hasAnswer | isUnique |
|---|-----------|-----|-------|------|---------------|-----------|----------|
| 1 | kshitiz/play_tidepool.py | tidepool | easy | 6×6 | tidepool.rs | ✅ | ✅ |
| 2 | kshitiz/play_tidepool.py | tidepool | medium | 8×8 | tidepool.rs | ✅ | ✅ |
| 3 | kshitiz/play_tidepool.py | tidepool | hard | 10×10 | tidepool.rs | ✅ | ✅ |
| 4 | kshitiz/play_paritypipes.py | paritypipes | easy | 6×6 | paritypipes.rs | ✅ | ✅ |
| 5 | kshitiz/play_paritypipes.py | paritypipes | medium | 8×8 | paritypipes.rs | ✅ | ✅ |
| 6 | kshitiz/play_paritypipes.py | paritypipes | hard | 10×10 | paritypipes.rs | ✅ | ✅ |
| 7 | rahul/play_radiance.py | radiance | easy | 6×6 | radiance.rs | ✅ | ✅ |
| 8 | rahul/play_radiance.py | radiance | medium | 8×8 | radiance.rs | ✅ | ✅ |
| 9 | rahul/play_radiance.py | radiance | hard | 10×10 | radiance.rs | ✅ | ✅ |
| 10 | shabid/puzzle_gradientwalls.py | gradientwalls | easy | 6×6 | gradientwalls.rs | ✅ | ✅ |
| 11 | shabid/puzzle_gradientwalls.py | gradientwalls | medium | 8×8 | gradientwalls.rs | ✅ | ✅ |
| 12 | shabid/puzzle_gradientwalls.py | gradientwalls | hard | 10×10 | gradientwalls.rs | ✅ | ✅ |
| 13 | shabid/puzzle_kageboshi.py | kageboshi | easy | 6×6 | kageboshi.rs | ✅ | ✅ |
| 14 | shabid/puzzle_kageboshi.py | kageboshi | medium | 8×8 | kageboshi.rs | ✅ | ✅ |
| 15 | shabid/puzzle_kageboshi.py | kageboshi | hard | 10×10 | kageboshi.rs | ✅ | ✅ |
| 16 | shabid/puzzle_resonance.py | resonance | easy | 6×6 | resonance.rs | ✅ | ✅ |
| 17 | shabid/puzzle_resonance.py | resonance | medium | 8×8 | resonance.rs | ✅ | ✅ |
| 18 | shabid/puzzle_resonance.py | resonance | hard | 10×10 | resonance.rs | ✅ | ✅ |
| 19 | sar/puzzle_pairloop.py | pairloop | easy | 6×6 | pairloop.rs | ✅ | ✅ |
| 20 | sar/puzzle_pairloop.py | pairloop | medium | 7×7 | pairloop.rs | ✅ | ✅ |
| 21 | sar/puzzle_pairloop.py | pairloop | hard | 8×8 | pairloop.rs | ✅ | ✅ |

**Legend**: ✅ = True

**Statistics** (tested May 1, 2026):
- **21 of 21** puzzles: Unique ✅
- **0 of 21** puzzles: Not unique ⚠️
- **0 of 21** puzzles: No Answer ❌
- **0 of 21** puzzles: Solver URL parsing errors

---

## Solver Support Matrix

| PID (in URL) | Solver Module | Puzzle Type | Move Count Range | Status |
|-------------|---------------|-------------|-----------------|--------|
| tidepool | tidepool.rs | Shading (BFS depth clues) | 3–4 req / 36–100 total | 3/3 Unique |
| paritypipes | paritypipes.rs | Edge/loop (parity vertices) | 22–54 req / 22–54 total | 3/3 Unique |
| radiance | radiance.rs | Mirror placement (beam tracing) | 3–8 req / 3–8 total | 3/3 Unique |
| gradientwalls | gradientwalls.rs | Number placement (wall constraints) | 59–333 req / 59–333 total | 3/3 Unique |
| kageboshi | kageboshi.rs | Shading (shadow casting) | 11–20 req / 36–100 total | 3/3 Unique |
| resonance | resonance.rs | Click-cycling (emitter placement) | 14–21 req / 14–21 total | 3/3 Unique |
| pairloop | pairloop.rs | Edge/loop (paired arrows) | 26–48 req / 84–144 total | 3/3 Unique |

**PID Routing** (cspuz_solver_backend/src/puzzle/mod.rs, `puzzle_list!(puzz_link, ...)`):
- `"tidepool"` → tidepool.rs (L217)
- `"paritypipes"` → paritypipes.rs (L182)
- `"radiance"` → radiance.rs (L186)
- `"gradientwalls"` → gradientwalls.rs (L134)
- `"kageboshi"` → kageboshi.rs (L146)
- `"resonance"` → resonance.rs (L188)
- `"pairloop"` → pairloop.rs (L181)

---

## Cleanup Summary (v4)

### What Was Removed (May 1, 2026)

**Phase 1: `*2` variants removed (9 puzzle types)**
- Deleted: tapa2, lightup2, nurikabe2, yajilin2, lits2, sudoku2, country2, heyawake2, minesweeper2
- Files removed: 9 Python games, 5 standalone JS files, 9 Rust solver modules, 9 Rust backend wrappers
- Edits: variety.js (9 registry entries), failcode.en.json (10 error entries), rules.en.yaml (5 rule entries), custom_rules.yaml (9 sections), 7 base JS files (pidlist + @variant cleanup), both Rust mod.rs files

**Phase 2: `*_custom` variants removed (10 solver modules)**
- Deleted: sudoku_custom, heyawake_custom, hitori_custom, lightup_custom, minesweeper_custom, noribridge_custom, nurikabe_custom, tapa_custom, yajilin_custom, country_custom
- Files removed: 10 Rust solver modules, 10 Rust backend wrappers
- Edits: both Rust mod.rs files (rewired puzzle_list! to base solver entries)
- Note: These _custom modules were SHADOWING base solvers (same alias, first-match wins)

**Phase 3: Corresponding Python game files removed (13)**
- Deleted: All Python files whose puzzles depended on removed *2 or *_custom solvers
- Kept: 7 games with their own dedicated solver modules (tidepool, paritypipes, radiance, gradientwalls, kageboshi, resonance, pairloop)

### Impact Assessment

- **Remaining games (7)**: All function correctly — independent solver modules, no dependency on removed code
- **Base puzzle types (~139)**: Fully intact in cspuz_solver_backend. No functionality lost.
- **pzprjs base types**: All JS source files still support their base puzzle types (tapa, lightup, nurikabe, yajilin, lits, country, kurotto/mines, sudoku, heyawake). Only *2 variant code removed.
- **Cargo build**: SUCCESS with only 4 pre-existing dead_code warnings (unused `enumerate` helpers in heyawake, nurikabe, pairloop)

---

## Key Findings

### 1. Current State (May 1, 2026)
- **21 of 21 puzzles** (100%): Unique solution confirmed by SAT solver ✅
- **7 active game types** with dedicated Rust solver modules
- **Zero** dangling references to removed `*2` or `*_custom` modules
- **Binary**: `target/release/run_solver` (5.7MB, built May 1, 2026)

### 2. Pipeline Verification
- `generate_morpheus_dataset.py` successfully discovers and generates all 21 puzzle records
- All 21 URLs parse and solve correctly via `run_solver --json`
- All games produce valid `puzzlink_url` fields for ppbench harness

### 3. Complete Test Run Log (May 1, 2026)
```
#   Game File                              PID            Level    Size    hasAnswer  isUnique
-------------------------------------------------------------------------------------------------
1   kshitiz/play_tidepool.py               tidepool       easy     6×6    True       True
2   kshitiz/play_tidepool.py               tidepool       medium   8×8    True       True
3   kshitiz/play_tidepool.py               tidepool       hard     10×10  True       True
4   kshitiz/play_paritypipes.py            paritypipes    easy     6×6    True       True
5   kshitiz/play_paritypipes.py            paritypipes    medium   8×8    True       True
6   kshitiz/play_paritypipes.py            paritypipes    hard     10×10  True       True
7   rahul/play_radiance.py                 radiance       easy     6×6    True       True
8   rahul/play_radiance.py                 radiance       medium   8×8    True       True
9   rahul/play_radiance.py                 radiance       hard     10×10  True       True
10  shabid/puzzle_gradientwalls.py         gradientwalls  easy     6×6    True       True
11  shabid/puzzle_gradientwalls.py         gradientwalls  medium   8×8    True       True
12  shabid/puzzle_gradientwalls.py         gradientwalls  hard     10×10  True       True
13  shabid/puzzle_kageboshi.py             kageboshi      easy     6×6    True       True
14  shabid/puzzle_kageboshi.py             kageboshi      medium   8×8    True       True
15  shabid/puzzle_kageboshi.py             kageboshi      hard     10×10  True       True
16  shabid/puzzle_resonance.py             resonance      easy     6×6    True       True
17  shabid/puzzle_resonance.py             resonance      medium   8×8    True       True
18  shabid/puzzle_resonance.py             resonance      hard     10×10  True       True
19  sar/puzzle_pairloop.py                 pairloop       easy     6×6    True       True
20  sar/puzzle_pairloop.py                 pairloop       medium   7×7    True       True
21  sar/puzzle_pairloop.py                 pairloop       hard     8×8    True       True
```
