const metadata = {
  game_name: "Sudoku",
  rules: "(1) Fill every empty cell with a digit 1-9. (2) Each row must contain all digits 1-9 exactly once. (3) Each column must contain all digits 1-9 exactly once. (4) Each 3×3 box must contain all digits 1-9 exactly once.",
  how_to_play: "Click a cell then type a digit 1-9. Press 0 or Delete to clear.",
  grid: { rows: 9, cols: 9 },
  cell_type: "number",
  valid_values: [1, 2, 3, 4, 5, 6, 7, 8, 9],
  win_condition: "All cells filled with no row, column, or box duplicates.",
  difficulty: "easy",
  available_difficulties: ["easy", "medium", "hard"]
};
