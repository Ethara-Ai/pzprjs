#!/usr/bin/env python3
"""
Play modified Light Up (Akari) puzzles in the browser using puzz.link.

Modified rules (vs standard Light Up):
  1. Bulb illumination is 3x3 box centered on bulb (not row/column rays)
  2. Multiple bulbs may illuminate each other (no duplicate-light restriction)
  Kept: numbered wall = exactly that many adjacent bulbs, all empty cells must be lit.

Usage:
    python3 play_lightup.py              # show menu
    python3 play_lightup.py easy         # open easy puzzle
    python3 play_lightup.py all          # open all puzzles
"""

import sys
import webbrowser

PUZZLES = {
    "easy": {
        "name": "Easy (4x4)",
        "url": "https://puzz.link/p?lightup/4/4/i01..0..i.c",
    },
    "medium": {
        "name": "Medium (5x5)",
        "url": "https://puzz.link/p?lightup/5/5/1..g5.g.hbg071.h.ga",
    },
    "hard": {
        "name": "Hard (6x6)",
        "url": "https://puzz.link/p?lightup/6/6/.g.bg7.g07...g.1..h.b0.b..a",
    },
}


def show_menu():
    print("Light Up (Akari) -- Modified Rules -- Play in Browser")
    print("  Rules: 3x3 box illumination, no duplicate-light restriction")
    print()
    print("Puzzles:")
    for key, p in PUZZLES.items():
        print(f"  {key:10s}  {p['name']:20s}  {p['url']}")
    print()
    print("Usage:")
    print("  python3 play_lightup.py <name>      Open a specific puzzle")
    print("  python3 play_lightup.py all          Open all puzzles")
    print()
    print("How to play on puzz.link:")
    print("  Left-click   -> place/remove bulb")
    print("  Right-click  -> mark cell as empty (dot)")
    print("  Check button -> verify your solution")


def open_puzzle(key):
    p = PUZZLES[key]
    print(f"Opening {p['name']} in browser...")
    print(f"  URL: {p['url']}")
    webbrowser.open(p["url"])


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
    else:
        print(f"Unknown option: {choice}")
        show_menu()
        sys.exit(1)


if __name__ == "__main__":
    main()
