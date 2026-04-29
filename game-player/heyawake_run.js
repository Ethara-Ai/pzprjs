const metadata = {
  game_name: "Heyawake",
  rules: "(1) No 2×2 area may be fully shaded. (2) All unshaded cells must be connected. (3) A contiguous horizontal or vertical line of unshaded cells cannot span more than 2 rooms. (4) If a room has a number clue, it must contain exactly that many shaded cells.",
  how_to_play: "Click a cell to shade it, click again to unshade. Numbers on cells show their room ID.",
  grid: { rows: 7, cols: 7 },
  cell_type: "shade_number",
  valid_values: [0, 1],
  win_condition: "All rules satisfied with unshaded cells connected.",
  difficulty: "easy",
  available_difficulties: ["easy", "medium", "hard"]
};
