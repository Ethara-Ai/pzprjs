"""
Generate my_dataset.jsonl for pencil-puzzle-bench (ppbench bundled format).

Usage:
    python generate_morpheus_dataset.py                      # all games in games/
    python generate_morpheus_dataset.py pairloop radiance    # specific games only
    python generate_morpheus_dataset.py --check              # dry-run summary
    python generate_morpheus_dataset.py pairloop --check     # dry-run specific game
"""

import base64
import glob
import inspect
import json
import os
import re
import sys
import importlib.util

GAMES_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(
    os.path.dirname(GAMES_DIR), "..",
    "pencil-puzzle-bench", "ppbench", "bundled", "my_dataset.jsonl"
)
OUTPUT_PATH = os.path.normpath(OUTPUT_PATH)

_XOR_KEY = b"ppbench"
DIFFICULTIES = ["easy", "medium", "hard"]
_SKIP_FILES = {"game_template.py", "generate_morpheus_dataset.py", "__init__.py"}


def _encrypt_solution(solution: dict) -> str:
    raw = json.dumps(solution, default=str).encode()
    encrypted = bytes(b ^ _XOR_KEY[i % len(_XOR_KEY)] for i, b in enumerate(raw))
    return base64.b64encode(encrypted).decode()


def _discover_games():
    games = []
    for filepath in sorted(glob.glob(os.path.join(GAMES_DIR, "**", "*.py"), recursive=True)):
        filename = os.path.basename(filepath)
        if filename in _SKIP_FILES:
            continue

        rel_path = os.path.relpath(filepath, GAMES_DIR)
        mod_name = filename.replace(".py", "")

        try:
            spec = importlib.util.spec_from_file_location(mod_name, filepath)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception:
            continue

        gen_funcs = [
            (name, func) for name, func in inspect.getmembers(mod, inspect.isfunction)
            if name.startswith("generate_")
        ]
        if not gen_funcs:
            continue

        func_name, func = gen_funcs[0]
        params = inspect.signature(func).parameters
        takes_difficulty = len(params) > 0

        games.append((rel_path, mod_name, func_name, func, takes_difficulty))

    return games


def _get_pid_from_game(func, takes_difficulty):
    try:
        result = func("easy") if takes_difficulty else func()
        return result.get("pid", None)
    except Exception:
        return None


def generate_all(filter_pids=None):
    records = []
    errors = []

    games = _discover_games()
    available_pids = []

    for rel_path, mod_name, func_name, func, takes_difficulty in games:
        pid = _get_pid_from_game(func, takes_difficulty)
        if pid is None:
            errors.append(f"PID DETECT FAIL: {rel_path}")
            continue

        available_pids.append(pid)

        if filter_pids and pid not in filter_pids:
            continue

        for diff in DIFFICULTIES:
            try:
                puzzle = func(diff) if takes_difficulty else func()
                if "solution" in puzzle:
                    puzzle["solution_enc"] = _encrypt_solution(puzzle.pop("solution"))
                records.append(puzzle)
            except Exception as e:
                errors.append(f"GEN FAIL: {pid}/{diff} -> {e}")

    if filter_pids:
        unknown = filter_pids - set(available_pids)
        for pid in sorted(unknown):
            errors.append(f"UNKNOWN PID: {pid} (available: {', '.join(sorted(available_pids))})")

    return records, errors


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check_only = "--check" in sys.argv
    filter_pids = set(args) if args else None

    records, errors = generate_all(filter_pids)

    if check_only:
        print(f"Generated {len(records)} puzzle records")
        for r in records:
            print(f"  {r['pid']:15s} {r.get('metadata', {}).get('level', '?'):8s} "
                  f"{r['width']}x{r['height']}  moves={r['number_required_moves']}")
        if errors:
            print(f"\n{len(errors)} errors:")
            for e in errors:
                print(f"  {e}")
        return

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        for record in records:
            f.write(json.dumps(record, default=str) + "\n")

    print(f"Wrote {len(records)} records to {OUTPUT_PATH}")
    if errors:
        print(f"\n{len(errors)} errors:")
        for e in errors:
            print(f"  {e}")
    else:
        print("No errors.")


if __name__ == "__main__":
    main()
