const metadata = {
  game_name: "Tapa",
  rules: "(1) Shade cells according to clue constraints. (2) Each clue shows the lengths of consecutive shaded groups among its 8 neighbors. (3) No 2x2 block of shaded cells allowed. (4) All shaded cells must be connected. (5) Each column must have more shaded cells than unshaded cells.",
  how_to_play: "Click an empty cell to shade it, click again to unshade.",
  grid: { rows: 5, cols: 6 },
  cell_type: "shade_number",
  valid_values: [0, 1],
  win_condition: "All clues satisfied, shaded cells connected, no 2x2 blocks, column majority met.",
  difficulty: "medium",
  available_difficulties: ["easy", "medium", "hard"]
};
