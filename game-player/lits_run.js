const metadata = {
  game_name: "LITS",
  rules: "(1) Each room must contain exactly 4 shaded cells forming an L, I, T, or S tetromino. (2) No 2×2 area may be fully shaded. (3) No two adjacent rooms may contain the same tetromino shape. (4) All shaded cells must be connected.",
  how_to_play: "Click a cell to shade it, click again to unshade.",
  grid: { rows: 5, cols: 5 },
  cell_type: "shade_number",
  valid_values: [0, 1],
  win_condition: "Every room has a valid tetromino, no 2×2, no adjacent same shapes, all shaded connected.",
  difficulty: "easy",
  available_difficulties: ["easy", "medium", "hard"]
};
