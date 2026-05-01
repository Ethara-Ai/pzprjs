# Morpheus

A custom puzzle game platform built on [pzprjs](https://github.com/sabo2/pzprjs) (browser puzzle editor/player) and [cspuz_core](https://github.com/semiexp/cspuz_core) (Rust constraint solver). Morpheus adds variant puzzle types with custom gameplay rules, Python-based puzzle generators, and an in-browser rules panel.

## Architecture

```
morpheus/
├── pzprjs/           # Forked puzzle editor/player (JavaScript, runs in browser)
│   ├── src/          # Core puzzle engine + ~320 puzzle type implementations
│   ├── src-ui/       # Browser UI (HTML/CSS/JS)
│   ├── games/        # Python puzzle generators (7 scripts)
│   └── dist/         # Built output (generated)
├── cspuz_core/       # Constraint solver (Rust)
│   ├── cspuz_core/           # Core CSP-to-SAT engine
│   ├── cspuz_rs/             # Puzzle modeling layer
│   ├── cspuz_rs_puzzles/     # ~166 puzzle solver implementations (159 upstream + 7 custom)
│   └── cspuz_solver_backend/ # CLI solver backend
└── pencil-puzzle-bench/      # ppbench benchmarking framework
```

**How they connect**: pzprjs is the browser-side editor/player. cspuz_core provides a CLI solver binary. Both share the [puzz.link URL format](https://puzz.link) as their integration contract. The Python generators produce puzzle URLs that load directly in the pzprjs player. The solver accepts those same URLs for uniqueness verification.

## Supported Puzzle Types

### Standard (from upstream pzprjs)

~320 puzzle types from the pzprjs ecosystem. See `src/pzpr/variety.js` for the full registry.

### Custom Variants (added by Morpheus)

| PID | Name | Type |
|-----|------|------|
| `tidepool` | Tidepool | Shading puzzle with BFS depth clues |
| `paritypipes` | Parity Pipes | Edge/loop puzzle with parity vertices |
| `radiance` | Radiance | Mirror placement with beam tracing |
| `gradientwalls` | Gradient Walls | Number placement with wall constraints |
| `kageboshi` | Kageboshi | Shading puzzle with shadow casting |
| `resonance` | Resonance | Click-cycling emitter placement |
| `pairloop` | Pair Loop | Edge/loop puzzle with paired arrows |

## Custom SAT Solver (cspuz_core)

The solver has been extended with **7 custom Rust modules** that encode Morpheus-specific puzzle logic as SAT constraints, enabling uniqueness verification for all custom variants.

### Custom Solver Modules

| Module | Puzzle Type |
|--------|-------------|
| `tidepool.rs` | BFS depth shading constraints |
| `paritypipes.rs` | Parity vertex edge constraints |
| `radiance.rs` | Mirror/beam path constraints |
| `gradientwalls.rs` | Wall gradient number constraints |
| `kageboshi.rs` | Shadow casting constraints |
| `resonance.rs` | Emitter resonance constraints |
| `pairloop.rs` | Paired arrow loop constraints |

The solver accepts localhost:8000 URLs for local development with custom pzprjs rules.

### Solver Verification Results (21 puzzles)

| Metric | Count |
|--------|-------|
| Unique solution verified | 21/21 |
| Solved (not unique) | 0/21 |
| No solution found | 0/21 |
| URL parse error | 0/21 |

## Puzzle Generators

7 Python scripts in `pzprjs/games/` generate puzzles at three difficulty levels:

| Directory | Games | Generator Pattern |
|-----------|-------|------------------|
| `kshitiz/` | tidepool, paritypipes | `generate_custom_*(difficulty="easy")` |
| `rahul/` | radiance | `generate_custom_*(difficulty="easy")` |
| `shabid/` | gradientwalls, kageboshi, resonance | `generate_puzzle_*(difficulty="easy")` |
| `sar/` | pairloop | `generate_puzzle_*(difficulty="easy")` |

### Usage

```bash
cd pzprjs/games
python -c "from kshitiz.play_tidepool import generate_custom_tidepool; print(generate_custom_tidepool('easy'))"
python -c "from shabid.puzzle_resonance import generate_puzzle_resonance; print(generate_puzzle_resonance('hard'))"
```

All generators return a dict containing:
- `puzzle_url` / `puzzlink_url` — puzzle URL to load in the player
- `pid` — puzzle type identifier
- `width`, `height`, `area` — grid dimensions
- `number_required_moves`, `number_total_solution_moves` — move counts
- `metadata` — includes `has_structured_solution`, `cspuz_is_unique`, `level`
- `created_at`, `source`
- `solution` — `moves_full`, `moves_required`, `moves_hint` (ppbench-compliant move lists)

### Dataset Generation

```bash
cd pzprjs/games
python generate_morpheus_dataset.py
# Auto-discovers game files via glob, generates 21 puzzle records
# Outputs: pencil-puzzle-bench/ppbench/bundled/my_dataset.jsonl
```

## Quick Start

### Prerequisites

- Node.js >= 24.0
- Python 3.x
- Rust toolchain (for cspuz_core)

### Build & Run pzprjs

```bash
cd pzprjs
npm install
echo '{"hash": "local"}' > git.json    # Workaround for non-git directory
npm run build                            # ESLint + Grunt concat/uglify -> dist/
make serve                               # python3 -m http.server on localhost:8000
```

Open `http://localhost:8000/p.html?tidepool/6/6/<encoded_body>` in a browser.

### Build cspuz_core

```bash
cd cspuz_core
cargo build --release
# Binary: target/release/run_solver
```

### Using the Solver

```bash
# Local development URLs
./target/release/run_solver --json "http://localhost:8000/p.html?tidepool/6/6/..."

# Standard puzz.link URLs
./target/release/run_solver --json "https://puzz.link/p?radiance/6/6/..."
```

**Supported URL hosts**: `puzz.link/p?`, `pzv.jp/p.html?`, `pzprxs.vercel.app/p?`, `localhost:8000/p.html?`, `localhost:8000/p?`

**Output format**: JSON with `hasAnswer`, `isUnique`, grid data.

### Run Tests

```bash
cd pzprjs
npm test          # Mocha tests
npm run lint      # ESLint
```

## Adding a New Custom Puzzle Type

### 1. Register in `src/pzpr/variety.js`

```js
newpuzzle: [0, 0, "Japanese Name", "English Name", "newpuzzle"],
```

### 2. Create variety file

Create `src/variety/newpuzzle.js` with MouseEvent, Board, Graphic, Encode, and AnsCheck sections.

### 3. Create solver module

```bash
# 1. Solver: cspuz_rs_puzzles/src/puzzles/newpuzzle.rs
# 2. Register: pub mod newpuzzle; in mod.rs
# 3. Backend: cspuz_solver_backend/src/puzzle/newpuzzle.rs
# 4. Register: (newpuzzle, ["newpuzzle"], "Name", "JP") in puzzle_list!
# 5. Rebuild: cargo build --release
```

### 4. Create game file

Create `games/<dir>/play_newpuzzle.py` following `game_template.py`.

### 5. Build and verify

```bash
npm run build
make serve
# Open http://localhost:8000/p.html?newpuzzle/...
```

## Project Structure Details

### pzprjs (Browser Puzzle Engine)

- **Core** (`src/pzpr/`): Variety registry, class manager, URL parser, event system
- **Puzzle engine** (`src/puzzle/`): Board, Piece, Graphic, MouseInput, KeyInput, Encode, Answer checking
- **Varieties** (`src/variety/`): ~320 puzzle IDs across implementation files
- **UI** (`src-ui/`): HTML pages, CSS, menu system, toolbar, rules panel
- **Build**: Grunt (concat -> uglify -> copy to `dist/`)

### cspuz_core (Constraint Solver)

- **CSP engine** (`cspuz_core/`): CSP -> normalization -> SAT encoding -> CDCL solver (Glucose/CaDiCaL)
- **Puzzle layer** (`cspuz_rs/`): Grid/graph modeling, serializer (puzz.link + localhost URL codec)
- **Solvers** (`cspuz_rs_puzzles/`): ~166 individual puzzle solvers (159 upstream + 7 custom)
- **Backend** (`cspuz_solver_backend/`): CLI target, JSON output
- **Key algorithm**: `decide_irrefutable_facts` — finds values forced in ALL valid solutions

### Documentation Files

| File | Description |
|------|-------------|
| `pzprjs/games/cspuz_solutions.md` | Full solver output for all 21 puzzles |
| `pzprjs/games/fixed_games.md` | Historical: changelog for removed game file fixes |
| `pzprjs/games/custom_rules.yaml` | Custom rules for all 7 active games |
| `cspuz_core/changes_log.md` | Historical: development of removed custom solver modules |

## License

- pzprjs: MIT (fork of [sabo2/pzprjs](https://github.com/sabo2/pzprjs))
- cspuz_core: See cspuz_core/LICENSE (from [semiexp/cspuz_core](https://github.com/semiexp/cspuz_core))

# From your pzprjs directory (after npm run build):
cp -r dist/* /Users/apple/Desktop/morpheus/pencil-puzzle-bench/ppbench/vendor/pzprjs/dist/