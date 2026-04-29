const metadata = {
  game_name: "Nori Bridge",
  rules: "(1) Place bridges on border cells between adjacent regions. (2) All regions must be connected via bridges. (3) Numbered regions must have exactly that many bridges. (4) At most 1 bridge per shared border between two regions.",
  how_to_play: "Click a cell on the border between two regions to toggle a bridge.",
  grid: { rows: 6, cols: 6 },
  cell_type: "shade_number",
  valid_values: [0, 1],
  win_condition: "All regions connected, all number constraints satisfied.",
  difficulty: "easy",
  available_difficulties: ["easy", "medium", "hard"]
};
