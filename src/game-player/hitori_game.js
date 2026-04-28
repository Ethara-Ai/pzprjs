const _GRIDS = {
  easy: {
    rows: 5,
    cols: 5,
    grid: [
      [1, 2, 3, 2, 5],
      [3, 1, 2, 5, 4],
      [2, 3, 5, 4, 1],
      [5, 4, 1, 3, 2],
      [4, 5, 4, 1, 3],
    ],
    extra_rules: [],
  },
  medium: {
    rows: 6,
    cols: 6,
    grid: [
      [2, 4, 5, 2, 1, 3],
      [4, 5, 2, 1, 3, 6],
      [5, 2, 3, 3, 2, 4],
      [2, 1, 3, 6, 4, 5],
      [1, 3, 6, 4, 5, 2],
      [3, 6, 4, 4, 2, 1],
    ],
    extra_rules: ["diagonal_ban", "checkerboard_parity", "max_2_per_line"],
  },
  hard: {
    rows: 8,
    cols: 8,
    grid: [
      [1, 5, 8, 3, 2, 6, 4, 7],
      [5, 4, 3, 2, 6, 4, 7, 5],
      [8, 3, 2, 6, 7, 7, 1, 5],
      [3, 2, 6, 4, 7, 1, 5, 8],
      [2, 6, 4, 7, 1, 5, 7, 3],
      [6, 4, 7, 1, 5, 8, 3, 2],
      [7, 7, 3, 5, 8, 3, 2, 6],
      [7, 1, 5, 8, 3, 2, 6, 4],
    ],
    extra_rules: ["diagonal_ban", "checkerboard_parity", "max_2_per_line"],
  },
};

let _ROWS = 6;
let _COLS = 6;
let _GRID = _GRIDS.medium.grid;
let _activeExtraRules = _GRIDS.medium.extra_rules;
let _history = [];

function _checkNoDuplicateUnshaded(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    const seen = {};
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] === 0) {
        const num = _GRID[r][c];
        if (num in seen) {
          errors.push({ row: r, col: c, message: `Duplicate ${num} in row ${r + 1}` });
          errors.push({ row: r, col: seen[num], message: `Duplicate ${num} in row ${r + 1}` });
        } else {
          seen[num] = c;
        }
      }
    }
  }
  for (let c = 0; c < _COLS; c++) {
    const seen = {};
    for (let r = 0; r < _ROWS; r++) {
      if (board[r][c] === 0) {
        const num = _GRID[r][c];
        if (num in seen) {
          errors.push({ row: r, col: c, message: `Duplicate ${num} in col ${c + 1}` });
          errors.push({ row: seen[num], col: c, message: `Duplicate ${num} in col ${c + 1}` });
        } else {
          seen[num] = r;
        }
      }
    }
  }
  return errors;
}

function _checkNoAdjacentShaded(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] === 1) {
        if (c + 1 < _COLS && board[r][c + 1] === 1) {
          errors.push({ row: r, col: c, message: "Adjacent shaded cells" });
          errors.push({ row: r, col: c + 1, message: "Adjacent shaded cells" });
        }
        if (r + 1 < _ROWS && board[r + 1][c] === 1) {
          errors.push({ row: r, col: c, message: "Adjacent shaded cells" });
          errors.push({ row: r + 1, col: c, message: "Adjacent shaded cells" });
        }
      }
    }
  }
  return errors;
}

function _checkUnshadedConnected(board) {
  let start = null;
  let unshadedCount = 0;
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] === 0) {
        unshadedCount++;
        if (start === null) start = [r, c];
      }
    }
  }

  if (start === null || unshadedCount === 0) {
    return [{ row: 0, col: 0, message: "No unshaded cells" }];
  }

  const visited = new Set();
  const queue = [start];
  visited.add(start[0] + "," + start[1]);
  while (queue.length > 0) {
    const [r, c] = queue.shift();
    for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
      const nr = r + dr;
      const nc = c + dc;
      const key = nr + "," + nc;
      if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && !visited.has(key) && board[nr][nc] === 0) {
        visited.add(key);
        queue.push([nr, nc]);
      }
    }
  }

  if (visited.size < unshadedCount) {
    const errors = [];
    for (let r = 0; r < _ROWS; r++) {
      for (let c = 0; c < _COLS; c++) {
        if (board[r][c] === 0 && !visited.has(r + "," + c)) {
          errors.push({ row: r, col: c, message: "Disconnected unshaded cell" });
        }
      }
    }
    return errors;
  }
  return [];
}

function _checkDiagonalBan(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] === 1) {
        for (const [dr, dc] of [[-1, -1], [-1, 1], [1, -1], [1, 1]]) {
          const nr = r + dr;
          const nc = c + dc;
          if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && board[nr][nc] === 1) {
            errors.push({ row: r, col: c, message: "Diagonally adjacent shaded cells" });
            break;
          }
        }
      }
    }
  }
  return errors;
}

function _checkCheckerboardParity(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] === 1 && (r + c) % 2 !== 0) {
        errors.push({ row: r, col: c, message: "Shading not allowed here (parity)" });
      }
    }
  }
  return errors;
}

function _checkMax2PerLine(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    const shadedCols = [];
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] === 1) shadedCols.push(c);
    }
    if (shadedCols.length > 2) {
      for (const c of shadedCols) {
        errors.push({ row: r, col: c, message: `More than 2 shaded in row ${r + 1}` });
      }
    }
  }
  for (let c = 0; c < _COLS; c++) {
    const shadedRows = [];
    for (let r = 0; r < _ROWS; r++) {
      if (board[r][c] === 1) shadedRows.push(r);
    }
    if (shadedRows.length > 2) {
      for (const r of shadedRows) {
        errors.push({ row: r, col: c, message: `More than 2 shaded in col ${c + 1}` });
      }
    }
  }
  return errors;
}

function _getAllErrors(board) {
  const allErrs = [];
  allErrs.push(..._checkNoDuplicateUnshaded(board));
  allErrs.push(..._checkNoAdjacentShaded(board));
  allErrs.push(..._checkUnshadedConnected(board));
  if (_activeExtraRules.includes("diagonal_ban")) {
    allErrs.push(..._checkDiagonalBan(board));
  }
  if (_activeExtraRules.includes("checkerboard_parity")) {
    allErrs.push(..._checkCheckerboardParity(board));
  }
  if (_activeExtraRules.includes("max_2_per_line")) {
    allErrs.push(..._checkMax2PerLine(board));
  }
  const seen = new Set();
  const unique = [];
  for (const e of allErrs) {
    const key = e.row + "," + e.col;
    if (!seen.has(key)) {
      seen.add(key);
      unique.push(e);
    }
  }
  return unique;
}

function _hasAnyShading(board) {
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] === 1) return true;
    }
  }
  return false;
}

function _boardIsSolved(board) {
  if (!_hasAnyShading(board)) return false;
  return _getAllErrors(board).length === 0;
}

function init_game(meta) {
  let difficulty = (meta.difficulty || "medium").toLowerCase();
  if (!(difficulty in _GRIDS)) difficulty = "medium";

  const config = _GRIDS[difficulty];
  _ROWS = config.rows;
  _COLS = config.cols;
  _GRID = config.grid;
  _activeExtraRules = config.extra_rules;

  const board = [];
  const labels = [];
  const givenMask = [];
  for (let r = 0; r < _ROWS; r++) {
    board.push(new Array(_COLS).fill(0));
    labels.push(_GRID[r].slice());
    givenMask.push(new Array(_COLS).fill(false));
  }
  _history = [];

  return {
    board: board,
    labels: labels,
    given_mask: givenMask,
    status: "ready",
  };
}

function make_move(state, row, col, value) {
  const board = state.board;
  const oldValue = board[row][col];
  _history.push({ row: row, col: col, old_value: oldValue });
  board[row][col] = value;

  const conflicts = [];

  if (value === 1) {
    for (const [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
      const nr = row + dr;
      const nc = col + dc;
      if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && board[nr][nc] === 1) {
        conflicts.push({ row: nr, col: nc });
      }
    }

    if (_activeExtraRules.includes("diagonal_ban")) {
      for (const [dr, dc] of [[-1, -1], [-1, 1], [1, -1], [1, 1]]) {
        const nr = row + dr;
        const nc = col + dc;
        if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && board[nr][nc] === 1) {
          conflicts.push({ row: nr, col: nc });
        }
      }
    }

    if (_activeExtraRules.includes("checkerboard_parity") && (row + col) % 2 !== 0) {
      conflicts.push({ row: row, col: col });
    }

    if (_activeExtraRules.includes("max_2_per_line")) {
      let rowShaded = 0;
      for (let c = 0; c < _COLS; c++) {
        if (board[row][c] === 1) rowShaded++;
      }
      if (rowShaded > 2) {
        conflicts.push({ row: row, col: col });
      }

      let colShaded = 0;
      for (let r = 0; r < _ROWS; r++) {
        if (board[r][col] === 1) colShaded++;
      }
      if (colShaded > 2) {
        conflicts.push({ row: row, col: col });
      }
    }
  }

  if (conflicts.length > 0) {
    conflicts.push({ row: row, col: col });
  }

  const seen = new Set();
  const uniqueConflicts = [];
  for (const c of conflicts) {
    const key = c.row + "," + c.col;
    if (!seen.has(key)) {
      seen.add(key);
      uniqueConflicts.push(c);
    }
  }

  let msg = "";
  if (uniqueConflicts.length > 0) {
    msg = "Rule violation detected!";
  }

  const complete = _boardIsSolved(board);
  if (complete) {
    msg = "Congratulations! Puzzle solved!";
  }

  return {
    state: state,
    valid: uniqueConflicts.length === 0,
    conflicts: uniqueConflicts,
    message: msg,
    complete: complete,
  };
}

function undo_move(state) {
  if (_history.length === 0) return state;
  const move = _history.pop();
  state.board[move.row][move.col] = move.old_value;
  return state;
}

function check_solution(state) {
  const board = state.board;

  if (!_hasAnyShading(board)) {
    return {
      solved: false,
      errors: [],
      message: "No cells shaded yet. Shade cells to eliminate duplicates.",
    };
  }

  const errors = _getAllErrors(board);
  const solved = errors.length === 0;

  if (solved) {
    return {
      solved: true,
      errors: [],
      message: "Puzzle solved! All rules satisfied.",
    };
  }

  return {
    solved: false,
    errors: errors,
    message: `${errors.length} rule violation(s) found.`,
  };
}

function get_hint(state, row, col) {
  const board = state.board;

  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] === 0) {
        const num = _GRID[r][c];
        let hasRowDup = false;
        let hasColDup = false;

        for (let c2 = 0; c2 < _COLS; c2++) {
          if (c2 !== c && board[r][c2] === 0 && _GRID[r][c2] === num) {
            hasRowDup = true;
            break;
          }
        }
        for (let r2 = 0; r2 < _ROWS; r2++) {
          if (r2 !== r && board[r2][c] === 0 && _GRID[r2][c] === num) {
            hasColDup = true;
            break;
          }
        }

        if (hasRowDup || hasColDup) {
          if (!_activeExtraRules.includes("checkerboard_parity") || (r + c) % 2 === 0) {
            return {
              value: 1,
              message: `Cell (${r + 1},${c + 1}) has duplicate ${num} — consider shading it.`,
            };
          }
        }
      }
    }
  }

  return { value: null, message: "No obvious hint available. Try looking for duplicates in rows and columns." };
}
