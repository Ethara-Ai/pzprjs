# Morpheus

A custom puzzle game platform built on [pzprjs](https://github.com/sabo2/pzprjs) (browser puzzle editor/player) and [cspuz_core](https://github.com/semiexp/cspuz_core) (Rust constraint solver compiled to WASM). Morpheus adds variant puzzle types with custom gameplay rules, Python-based puzzle generators, and an in-browser rules panel.

## Architecture

```
morpheus/
├── pzprjs/           # Forked puzzle editor/player (JavaScript, runs in browser)
│   ├── src/          # Core puzzle engine + 177 puzzle type implementations
│   ├── src-ui/       # Browser UI (HTML/CSS/JS)
│   ├── games/        # Python puzzle generators (20 scripts)
│   └── dist/         # Built output (generated)
├── cspuz_core/       # Constraint solver (Rust, compiles to WASM)
│   ├── cspuz_core/           # Core CSP-to-SAT engine
│   ├── cspuz_rs/             # Puzzle modeling layer
│   ├── cspuz_rs_puzzles/     # 173 puzzle solver implementations (160 upstream + 13 custom)
│   └── cspuz_solver_backend/ # WASM-targeted solver backend
└── data/             # Rules documentation, verification scripts, golden datasets
```

**How they connect**: pzprjs is the browser-side editor/player. cspuz_core compiles to WASM and exposes `solve_problem(url)` via C ABI. Both share the [puzz.link URL format](https://puzz.link) as their integration contract. The Python generators produce puzz.link URLs that load directly in the pzprjs player. The solver also accepts `localhost:8000` URLs for local development with custom rules.

## Supported Puzzle Types

### Standard (from upstream pzprjs)

322 puzzle types from the pzprjs ecosystem. See `src/pzpr/variety.js` for the full registry.

### Custom Variants (added by Morpheus)

| Base Game | Variant | Custom Rules |
|-----------|---------|-------------|
| Sudoku | `sudoku` | No consecutive same digit, digit parity alternation, killer cage |
| Sudoku 2 | `sudoku2` | Row alternation, box alternation, even-digit balance |
| Heyawake | `heyawake` | No consecutive same-room shading, row shade balance |
| Heyawake 2 | `heyawake2` | Half-grid alternation, column shade balance, density 10-50% |
| Country Road | `country` | No consecutive same-room lines, min 50% coverage, max 1 empty row |
| Country Road 2 | `country2` | Turn balance, max 85% coverage, max 1 empty row |
| Minesweeper | `mines` | No consecutive same-row reveals, no 2x2 mine block, density <= 25% |
| Minesweeper 2 | `mines2` | Lucky streak (every 3rd safe reveal triggers bonus), row mine cap, no 2x2 block |
| Akari 2 | `lightup2` | Diagonal illumination, diagonal wall counting, no ortho-adjacent bulbs |
| Nurikabe | `nurikabe` | Shaded groups max 3 cells, straight-line islands |
| Nurikabe 2 | `nurikabe2` | No 2x2 unshaded, domino shaded groups, no connected-shade requirement |
| Tapa | `tapa` | Unshaded connectivity (flipped), no 2x2 unshaded, row shaded majority |
| Tapa 2 | `tapa2` | No 2x2 shaded, connected shaded cells, column shaded majority |
| Hitori | `hitori` | King adjacency (diagonal), checkerboard parity, max 2 shaded per line |
| LITS 2 | `lits2` | Triomino variant (3 cells per room instead of 4), no same-shape check |
| Nori Bridge | `noribridge` | Bridge placement, connected graph, degree match, single bridge per border |
| Yajilin 2 | `yajilin2` | Shaded cells must be on grid perimeter only |

Custom rules enforce real-time input constraints (flash red + revert on violation) and answer-check-time validation.

## Custom SAT Solver (cspuz_core)

The solver has been extended with **13 custom Rust modules** that encode Morpheus-specific rules as SAT constraints, enabling uniqueness verification for all custom variants.

### Custom Solver Modules

| Module | Custom Rules Encoded |
|--------|---------------------|
| `hitori_custom.rs` | King adjacency, checkerboard parity, max 2 per line |
| `sudoku2.rs` | Even-digit balance (4 even per row) |
| `minesweeper2.rs` | Row mine cap, no 2x2 mine block |
| `heyawake2.rs` | Strict adjacency, column shade balance, density 10-50% |
| `tapa_custom.rs` | Flipped: unshaded connected, no 2x2 unshaded, row majority |
| `tapa2.rs` | Standard + column shaded majority |
| `country2.rs` | Turn balance, max 85% coverage, max 1 empty row |
| `yajilin2.rs` | Shaded on border only |
| `lits2.rs` | Triominoes (3 cells/room), no same-shape check |
| `nurikabe_custom.rs` | Shade groups max 3, straight-line islands |
| `nurikabe2.rs` | Shaded dominoes, no 2x2 unshaded, no global connectivity |
| `lightup2.rs` | Diagonal illumination, diagonal wall counting, no ortho-adjacent |
| `noribridge.rs` | Bridge connectivity on region graph, degree constraints |

Additionally, the solver now accepts localhost:8000 URLs for local development with custom pzprjs rules.

### Solver Verification Results (60 puzzles)

| Metric | Count |
|--------|-------|
| Unique solution verified | 60/60 |
| Solved (not unique) | 0/60 |
| No solution found | 0/60 |
| URL parse error | 0/60 |

See [`cspuz_core/changes_log.md`](cspuz_core/changes_log.md) for full per-module results and build notes.

## Puzzle Generators

20 Python scripts in `pzprjs/games/` generate puzzles at three difficulty levels:

| Directory | Games | Generator Pattern | Notes |
|-----------|-------|------------------|-------|
| `sar/` | sudoku, sudoku2, heyawake, heyawake2, minesweeper, minesweeper2, country, country2 | `generate_puzzle_*(level="easy")` | Golden dataset with solutions |
| `kshitiz/` | nurikabe, nurikabe2, tapa, tapa2, lightup, lightup2 | `generate_custom_*(difficulty="easy")` | Includes constraint solvers |
| `rahul/` | hitori, lits, lits2, yajilin, yajilin2 | `generate_custom_*(difficulty="easy")` | URL-only output |
| `shabid/` | nori_bridge | `generate_puzzle(difficulty)` | Bridge puzzle variant (custom `noribridge` pid) |

### Usage

```bash
cd pzprjs/games/sar
python puzzle_sudoku.py easy      # Returns dict with puzzle_url, solution, metadata
python puzzle_heyawake.py medium

cd pzprjs/games/kshitiz
python play_lightup.py hard
```

All generators return a dict containing:
- `puzzle_url` / `puzzlink_url` — puzz.link URL to load in the player
- `pid` — puzzle type identifier
- `width`, `height`, `area` — grid dimensions
- `sort_key` — difficulty ordering key
- `number_required_moves`, `number_total_solution_moves` — move counts
- `metadata` — includes `has_structured_solution`, `cspuz_is_unique`, `db_w`, `db_h`
- `created_at`, `source`
- `solution` — `moves_full`, `moves_required`, `moves_hint` (ppbench-compliant move lists)

## Quick Start

### Prerequisites

- Node.js >= 24.0
- Python 3.x
- Rust toolchain (for cspuz_core, optional)

### Build & Run pzprjs

```bash
cd pzprjs
npm install
echo '{"hash": "local"}' > git.json    # Workaround for non-git directory
npm run build                            # ESLint + Grunt concat/uglify -> dist/
make serve                               # python3 -m http.server on localhost:8000
```

Open `http://localhost:8000/p.html?sudoku/9/9/<encoded_body>` in a browser.

Or generate a puzzle URL and open it:

```bash
cd games/sar
python -c "from puzzle_sudoku import generate_puzzle_sudoku; print(generate_puzzle_sudoku('easy')['puzzle_url'])"
# Copy the URL path after puzz.link/p? and append to http://localhost:8000/p.html?
```

### Build cspuz_core (WASM solver, optional)

```bash
cd cspuz_core
# Requires: Rust toolchain, Emscripten SDK, C++ compiler
./build_cspuz_solver_backend.sh release
# Outputs: build/cspuz_solver_backend/*.js + *.wasm
```

Or use the Rust CLI solver directly:

```bash
cd cspuz_core
cargo build --release
```

### Using the Solver

The solver accepts URLs from multiple hosts:

```bash
# Standard puzz.link URLs
./target/release/run_solver --json "https://puzz.link/p?sudoku/9/9/k8g1g7..."

# Local development URLs (for testing with custom pzprjs rules)
./target/release/run_solver --json "http://localhost:8000/p.html?sudoku/9/9/k8g1g7..."

# Custom variant types (registered aliases)
./target/release/run_solver --json "http://localhost:8000/p.html?sudoku2/9/9/..."
./target/release/run_solver --json "http://localhost:8000/p.html?heyawake2/6/6/..."
./target/release/run_solver --json "http://localhost:8000/p.html?mines2/6/6/..."
```

**Supported URL hosts**: `puzz.link/p?`, `pzv.jp/p.html?`, `pzprxs.vercel.app/p?`, `localhost:8000/p.html?`, `localhost:8000/p?`

**Supported URL flags**: `o/` / `ob/` (Yajilin outside), `e/` (Country Road empty)

**Output format**: JSON with `hasAnswer`, `isUnique`, grid data (cell values, shading, lines), and `boldWall` borders.

### Run Tests

```bash
cd pzprjs
npm test          # Mocha — 8956 assertions across 323 puzzle test scripts
npm run coverage  # nyc coverage report
npm run lint      # ESLint
```

## Adding a New Custom Puzzle Type

### 1. Register in `src/pzpr/variety.js`

```js
newpuzzle2: [0, 0, "Japanese Name", "English Name 2", "base_script_file"],
```

### 2. Add pid to the variety file's pidlist

In `src/variety/<base_script_file>.js`, add the new pid to the IIFE's `makeCustom` pidlist array. If the variety file uses `@pid` selectors on class blocks, add the new pid to each relevant selector.

### 3. Add custom rules to Board

```js
"Board@newpuzzle2": {
    customRules: [
        "Your first custom rule description.",
        "Your second custom rule description."
    ]
},
```

The rules panel automatically picks up `customRules` from `puzzle.board` at runtime -- no other registration needed.

### 4. Add standard rules to `rules.en.yaml`

```yaml
newpuzzle2: "1. First rule\n2. Second rule\n3. Third rule"
```

### 5. Build and verify

```bash
npm run build
make serve
# Open http://localhost:8000/p.html?newpuzzle2/...
```

### 6. Add a generator (optional)

Create `games/<your_dir>/play_newpuzzle2.py` following the existing generator pattern.

### 7. Add a custom solver (optional)

To enable SAT-based uniqueness verification for your variant:

1. Create `cspuz_rs_puzzles/src/puzzles/newpuzzle2.rs` with `solve_newpuzzle2()` + `deserialize_problem()`
2. Add `pub mod newpuzzle2;` in `cspuz_rs_puzzles/src/puzzles/mod.rs`
3. Create `cspuz_solver_backend/src/puzzle/newpuzzle2.rs` with `pub fn solve(url) -> Result<Board>`
4. Add `(newpuzzle2, ["newpuzzle2"], "Name", "JP Name")` in `puzzle_list!` macro in `cspuz_solver_backend/src/puzzle/mod.rs`
5. Rebuild: `cargo build --release`

See existing custom modules (e.g. `sudoku2.rs`, `heyawake2.rs`) for the pattern.

## Difficulty Levels

All generators support three difficulty levels that control grid size and constraint density:

| Game | Easy | Medium | Hard |
|------|------|--------|------|
| Sudoku | 9x9, 31 clues | 9x9, 22 clues | 9x9, 20 clues |
| Heyawake | 7x7, 12 rooms | 10x8, 16 rooms | 24x14, 52 rooms |
| Minesweeper | 6x6, 6 mines | 9x9, 15 mines | 12x12, 30 mines |
| Country Road | 5x5, 6 rooms | 10x10, 20 rooms | 15x15, 49 rooms |

Variant 2 types have adjusted parameters -- see `data/22-23 april/rules.md` for full tables.

## Project Structure Details

### pzprjs (Browser Puzzle Engine)

- **Core** (`src/pzpr/`): Variety registry, class manager, URL parser, event system
- **Puzzle engine** (`src/puzzle/`): Board, Piece, Graphic, MouseInput, KeyInput, Encode, Answer checking, Undo/redo
- **Varieties** (`src/variety/`): 173 implementation files covering 334 puzzle IDs
- **UI** (`src-ui/`): HTML pages, CSS, menu system, toolbar, rules panel, timer
- **Build**: Grunt (concat -> uglify -> copy to `dist/`)

### cspuz_core (Constraint Solver)

- **CSP engine** (`cspuz_core/`): CSP representation -> normalization -> SAT encoding (order/direct/log/mixed) -> CDCL solver (Glucose/CaDiCaL)
- **Puzzle layer** (`cspuz_rs/`): Grid/graph modeling, serializer (puzz.link + localhost URL codec), constraint combinators
- **Solvers** (`cspuz_rs_puzzles/`): 173 individual puzzle solvers (160 upstream + 13 custom Morpheus variants)
- **WASM backend** (`cspuz_solver_backend/`): Emscripten target, C ABI exports, JSON output
- **Key algorithm**: `decide_irrefutable_facts` -- finds values forced in ALL valid solutions via iterative SAT solving

### Documentation Files

| File | Description |
|------|-------------|
| `pzprjs/games/fixed_games.md` | Changelog for all game file fixes (12 phases) |
| `pzprjs/games/cspuz_solutions.md` | Full solver output for all 60 puzzles + custom rules compliance |
| `cspuz_core/changes_log.md` | All 24 new Rust files, upstream patches (localhost URLs), build fixes, test results, SAT encoding reference |
| `data/22-23 april/rules.md` | Complete custom rule specifications for all game types |

## Custom Rules Reference

See [`data/22-23 april/rules.md`](data/22-23%20april/rules.md) for the complete rule specification for all standard and variant puzzle types, including controls and edge cases.

## License

- pzprjs: MIT (fork of [sabo2/pzprjs](https://github.com/sabo2/pzprjs))
- cspuz_core: See cspuz_core/LICENSE (from [semiexp/cspuz_core](https://github.com/semiexp/cspuz_core))
