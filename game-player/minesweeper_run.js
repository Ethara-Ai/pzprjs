const metadata = {
  game_name: "Minesweeper",
  rules: "(1) Place mines on cells without number clues. (2) Each number clue indicates exactly how many mines are in its 8 adjacent cells. (3) Mines cannot be placed on clue cells.",
  how_to_play: "Click an empty cell (no number) to place a mine, click again to remove it.",
  grid: { rows: 6, cols: 6 },
  cell_type: "shade_number",
  valid_values: [0, 1],
  win_condition: "All number clues satisfied with correct mine placement.",
  difficulty: "easy",
  available_difficulties: ["easy", "medium", "hard"]
};
