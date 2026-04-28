const metadata = {
  game_name: "Hitori",
  rules: "Shade cells so that: (1) No number appears more than once in any row or column among unshaded cells. (2) Shaded cells cannot touch horizontally or vertically. (3) All unshaded cells must form one connected group. Extra rules for Medium and Hard: (4) No diagonal shading adjacency. (5) Shading only on even-parity cells. (6) Max 2 shaded per row or column.",
  how_to_play: "Click a cell to shade it, click again to unshade.",
  grid: { rows: 6, cols: 6 },
  cell_type: "shade_number",
  valid_values: [0, 1],
  win_condition: "All rules satisfied with no duplicate numbers in any row or column",
  difficulty: "medium",
  available_difficulties: ["easy", "medium", "hard"]
};
