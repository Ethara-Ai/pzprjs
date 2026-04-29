const metadata = {
  game_name: "Yajilin",
  rules: "(1) Shade some cells so that no two shaded cells are adjacent (horizontally or vertically). (2) Each arrow-number clue indicates exactly how many shaded cells lie in that direction. (3) Clue cells cannot be shaded.",
  how_to_play: "Click a cell to shade it, click again to unshade. Arrow clues show direction and count.",
  grid: { rows: 4, cols: 4 },
  cell_type: "shade_number",
  valid_values: [0, 1],
  win_condition: "All clue constraints satisfied with no adjacent shaded cells.",
  difficulty: "easy",
  available_difficulties: ["easy", "medium", "hard"]
};
