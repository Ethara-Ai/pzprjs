#!/usr/bin/env python3
"""
Play modified Nurikabe puzzles in the browser using puzz.link.

Modified rules (vs standard Nurikabe):
  1. Shaded groups have at most 3 cells (no shade component larger than 3)
  2. Islands must be straight lines (horizontal or vertical only)
  Standard 2x2 restriction and connected-shade requirement are removed.

Usage:
    python3 play_nurikabe.py              # show menu
    python3 play_nurikabe.py easy         # open easy puzzle
    python3 play_nurikabe.py all          # open all puzzles
    python3 play_nurikabe.py benchmark    # open 15 nurikabe puzzles from ppbench
"""

import sys
import webbrowser

PUZZLES = {
    "easy": {
        "name": "Easy (5×4)",
        "url": "https://puzz.link/p?nurikabe/5/4/2l3i1i1g3h",
    },
    "medium": {
        "name": "Medium (7×6)",
        "url": "https://puzz.link/p?nurikabe/7/6/g1i1i3j2j2i3j2j2i3j",
    },
    "hard": {
        "name": "Hard (9×6)",
        "url": "https://puzz.link/p?nurikabe/9/6/g1i1k3i3h2j1k3i3h2j1k3i3h",
    },
}


def show_menu():
    print("🧩 Modified Nurikabe — Play in Browser")
    print("  Rules: shade max 3 cells, straight-line islands")
    print()
    print("Puzzles:")
    for key, p in PUZZLES.items():
        print(f"  {key:10s}  {p['name']:20s}  {p['url']}")
    print()
    print("Usage:")
    print("  python3 play_nurikabe.py <name>      Open a specific puzzle")
    print("  python3 play_nurikabe.py all          Open all puzzles")
    print("  python3 play_nurikabe.py benchmark    Open nurikabe from ppbench dataset")
    print()
    print("How to play on puzz.link:")
    print("  Left-click   → shade cell (sea/black)")
    print("  Right-click  → mark cell (island/white)")
    print("  Click again  → clear cell")
    print("  Check button → verify your solution")


def open_puzzle(key):
    p = PUZZLES[key]
    print(f"Opening {p['name']} in browser...")
    print(f"  URL: {p['url']}")
    webbrowser.open(p["url"])


def open_benchmark():
    try:
        from ppbench import load_dataset

        records = load_dataset("golden")
        nurikabe = [r for r in records if r["pid"] == "nurikabe"]
        print(f"Opening {len(nurikabe)} nurikabe puzzles from ppbench benchmark:")
        for i, r in enumerate(nurikabe):
            print(f"  [{i+1:2d}] {r['puzzlink_url']}")
            webbrowser.open(r["puzzlink_url"])
    except ImportError:
        print("ppbench not installed. Install with: pip install ppbench")
        print("Or activate the venv: source /Users/apple/morpheus/venv/bin/activate")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        show_menu()
        return

    choice = sys.argv[1].lower()

    if choice in PUZZLES:
        open_puzzle(choice)
    elif choice == "all":
        for key in PUZZLES:
            open_puzzle(key)
    elif choice == "benchmark":
        open_benchmark()
    else:
        print(f"Unknown option: {choice}")
        show_menu()
        sys.exit(1)


if __name__ == "__main__":
    main()
