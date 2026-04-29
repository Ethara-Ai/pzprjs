const metadata = {
  game_name: "Light Up",
  rules: "(1) Place bulbs on empty cells. (2) Bulbs illuminate all cells in their row and column until blocked by a wall. (3) No two bulbs may illuminate each other. (4) Numbered walls must have exactly that many adjacent bulbs. (5) All empty cells must be illuminated.",
  how_to_play: "Click an empty cell to place or remove a bulb.",
  grid: { rows: 5, cols: 5 },
  cell_type: "shade_number",
  valid_values: [0, 1],
  win_condition: "All cells illuminated with no conflicts and all numbered wall constraints satisfied.",
  difficulty: "medium",
  available_difficulties: ["easy", "medium", "hard"]
};
