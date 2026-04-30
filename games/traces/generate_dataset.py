"""Generate dataset.jsonl from all 20 game types x 3 difficulty levels = 60 puzzles."""

import json
import sys
import os
import importlib.util

GAMES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (relative_path, module_name, generate_function_name, pid)
GAME_REGISTRY = [
    ("sar/puzzle_sudoku.py", "puzzle_sudoku", "generate_puzzle_sudoku", "sudoku"),
    ("sar/puzzle_sudoku2.py", "puzzle_sudoku2", "generate_puzzle_sudoku2", "sudoku2"),
    ("sar/puzzle_heyawake.py", "puzzle_heyawake", "generate_puzzle_heyawake", "heyawake"),
    ("sar/puzzle_heyawake2.py", "puzzle_heyawake2", "generate_puzzle_heyawake2", "heyawake2"),
    ("sar/puzzle_minesweeper.py", "puzzle_minesweeper", "generate_puzzle_minesweeper", "mines"),
    ("sar/puzzle_minesweeper2.py", "puzzle_minesweeper2", "generate_puzzle_minesweeper2", "mines2"),
    ("sar/puzzle_country.py", "puzzle_country", "generate_puzzle_country", "country"),
    ("sar/puzzle_country2.py", "puzzle_country2", "generate_puzzle_country2", "country2"),
    ("rahul/hitori_game.py", "hitori_game", "generate_custom_hitori", "hitori"),
    ("rahul/custom_lits.py", "custom_lits", "generate_custom_lits", "lits"),
    ("rahul/custom_lits2.py", "custom_lits2", "generate_custom_lits2", "lits2"),
    ("rahul/custom_yajilin.py", "custom_yajilin", "generate_custom_yajilin", "yajilin"),
    ("rahul/custom_yajilin2.py", "custom_yajilin2", "generate_custom_yajilin2", "yajilin2"),
    ("kshitiz/play_lightup.py", "play_lightup", "generate_custom_lightup", "lightup"),
    ("kshitiz/play_lightup2.py", "play_lightup2", "generate_custom_lightup2", "lightup2"),
    ("kshitiz/play_tapa.py", "play_tapa", "generate_custom_tapa", "tapa"),
    ("kshitiz/play_tapa2.py", "play_tapa2", "generate_custom_tapa2", "tapa2"),
    ("kshitiz/play_nurikabe.py", "play_nurikabe", "generate_custom_nurikabe", "nurikabe"),
    ("kshitiz/play_nurikabe2.py", "play_nurikabe2", "generate_custom_nurikabe2", "nurikabe2"),
    ("shabid/nori_bridge.py", "nori_bridge", "generate_puzzle_nori_bridges2", "noribridge"),
]

DIFFICULTIES = ["easy", "medium", "hard"]


def load_module(relative_path, module_name):
    filepath = os.path.join(GAMES_DIR, relative_path)
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def generate_all():
    records = []
    errors = []

    for rel_path, mod_name, func_name, pid in GAME_REGISTRY:
        try:
            mod = load_module(rel_path, mod_name)
            gen_func = getattr(mod, func_name)
        except Exception as e:
            errors.append(f"LOAD FAIL: {rel_path} -> {e}")
            continue

        for diff in DIFFICULTIES:
            try:
                puzzle = gen_func(diff)
                puzzle["puzzle_id"] = f"{pid}_{diff}"
                records.append(puzzle)
            except Exception as e:
                errors.append(f"GEN FAIL: {pid}/{diff} -> {e}")

    return records, errors


def main():
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset.jsonl")

    if "--check" in sys.argv:
        records, errors = generate_all()
        print(f"Generated {len(records)} puzzle records")
        for r in records:
            print(f"  {r['puzzle_id']:25s}  {r['width']}x{r['height']}  moves={r['number_required_moves']}")
        if errors:
            print(f"\n{len(errors)} errors:")
            for e in errors:
                print(f"  {e}")
        return

    records, errors = generate_all()

    with open(output_path, "w") as f:
        for record in records:
            f.write(json.dumps(record, default=str) + "\n")

    print(f"Wrote {len(records)} records to {output_path}")
    if errors:
        print(f"\n{len(errors)} errors:")
        for e in errors:
            print(f"  {e}")


if __name__ == "__main__":
    main()
