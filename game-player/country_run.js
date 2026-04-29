const metadata = {
  game_name: "Country Road",
  rules: "(1) Each room with a number clue must contain exactly that many shaded cells. (2) Shaded cells within a room must be contiguous. (3) Shaded cells in different rooms cannot be adjacent (horizontally or vertically).",
  how_to_play: "Click a cell to shade it, click again to unshade. Labels show room ID or room:clue.",
  grid: { rows: 5, cols: 5 },
  cell_type: "shade_number",
  valid_values: [0, 1],
  win_condition: "All room clues satisfied, shaded contiguous in rooms, no cross-room adjacency.",
  difficulty: "easy",
  available_difficulties: ["easy", "medium", "hard"]
};
