const metadata = {
  game_name: "Nurikabe",
  rules: "(1) Shade cells to form a connected 'sea'. (2) Each numbered cell is an island — the number indicates the island's size. (3) Each island must contain exactly one numbered cell. (4) Islands may not touch each other orthogonally. (5) No 2x2 block of shaded cells is allowed. (6) All shaded cells must be connected.",
  how_to_play: "Click an empty cell to shade it, click again to unshade.",
  grid: { rows: 6, cols: 6 },
  cell_type: "shade_number",
  valid_values: [0, 1],
  win_condition: "All rules satisfied with correct island sizes and connected sea.",
  difficulty: "medium",
  available_difficulties: ["easy", "medium", "hard"]
};
