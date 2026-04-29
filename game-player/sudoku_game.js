const _GRIDS = {
  easy: {
    clue_grid: [
      [0, 0, 0, 0, 8, 0, 0, 0, 0],
      [0, 0, 0, 9, 5, 2, 0, 0, 0],
      [0, 0, 0, 6, 1, 4, 0, 0, 0],
      [0, 0, 4, 0, 0, 0, 2, 0, 0],
      [0, 0, 5, 0, 0, 0, 7, 0, 0],
      [0, 1, 2, 0, 0, 0, 5, 8, 0],
      [7, 6, 1, 0, 0, 0, 9, 3, 5],
      [9, 4, 3, 0, 0, 0, 8, 2, 6],
      [0, 2, 8, 0, 0, 0, 1, 4, 0],
    ],
  },
  medium: {
    clue_grid: [
      [1, 0, 0, 0, 0, 0, 0, 0, 0],
      [0, 6, 0, 0, 8, 4, 0, 0, 0],
      [0, 0, 7, 6, 0, 0, 9, 0, 0],
      [0, 0, 6, 4, 0, 0, 0, 7, 0],
      [0, 4, 0, 0, 0, 0, 0, 8, 0],
      [0, 8, 0, 0, 0, 5, 3, 0, 0],
      [0, 0, 5, 0, 0, 7, 1, 0, 0],
      [0, 0, 0, 1, 4, 0, 0, 6, 0],
      [0, 0, 0, 0, 0, 0, 0, 0, 2],
    ],
  },
  hard: {
    clue_grid: [
      [0, 0, 7, 5, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 0, 2, 3, 0],
      [8, 0, 0, 1, 0, 0, 0, 0, 0],
      [9, 0, 0, 2, 0, 0, 0, 7, 0],
      [0, 3, 0, 0, 0, 0, 0, 6, 0],
      [0, 2, 0, 0, 0, 3, 0, 0, 4],
      [0, 0, 0, 0, 0, 4, 0, 0, 3],
      [0, 4, 5, 0, 0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0, 7, 8, 0, 0],
    ],
  },
};

let _ROWS = 9, _COLS = 9, _clueGrid = null;
let _history = [];

function _checkRowConflicts(board, row) {
  const errors = [];
  const seen = {};
  for (let c = 0; c < 9; c++) {
    const v = board[row][c];
    if (v === 0) continue;
    if (seen[v] !== undefined) {
      errors.push({ row, col: c, message: `Duplicate ${v} in row ${row + 1}` });
      errors.push({ row, col: seen[v], message: `Duplicate ${v} in row ${row + 1}` });
    } else {
      seen[v] = c;
    }
  }
  return errors;
}

function _checkColConflicts(board, col) {
  const errors = [];
  const seen = {};
  for (let r = 0; r < 9; r++) {
    const v = board[r][col];
    if (v === 0) continue;
    if (seen[v] !== undefined) {
      errors.push({ row: r, col, message: `Duplicate ${v} in column ${col + 1}` });
      errors.push({ row: seen[v], col, message: `Duplicate ${v} in column ${col + 1}` });
    } else {
      seen[v] = r;
    }
  }
  return errors;
}

function _checkBoxConflicts(board, boxRow, boxCol) {
  const errors = [];
  const seen = {};
  const r0 = boxRow * 3, c0 = boxCol * 3;
  for (let dr = 0; dr < 3; dr++) {
    for (let dc = 0; dc < 3; dc++) {
      const r = r0 + dr, c = c0 + dc;
      const v = board[r][c];
      if (v === 0) continue;
      const key = `${v}`;
      if (seen[key]) {
        errors.push({ row: r, col: c, message: `Duplicate ${v} in 3×3 box` });
        errors.push({ row: seen[key][0], col: seen[key][1], message: `Duplicate ${v} in 3×3 box` });
      } else {
        seen[key] = [r, c];
      }
    }
  }
  return errors;
}

function _getAllErrors(board) {
  const allErrs = [];
  for (let r = 0; r < 9; r++) allErrs.push(..._checkRowConflicts(board, r));
  for (let c = 0; c < 9; c++) allErrs.push(..._checkColConflicts(board, c));
  for (let br = 0; br < 3; br++)
    for (let bc = 0; bc < 3; bc++)
      allErrs.push(..._checkBoxConflicts(board, br, bc));

  const seen = new Set();
  return allErrs.filter(e => {
    const k = `${e.row},${e.col}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

function _isBoardFull(board) {
  for (let r = 0; r < 9; r++)
    for (let c = 0; c < 9; c++)
      if (board[r][c] === 0) return false;
  return true;
}

function init_game(meta) {
  const diff = (meta && meta.difficulty) || 'easy';
  const g = _GRIDS[diff] || _GRIDS.easy;
  _clueGrid = g.clue_grid;
  _history = [];

  const board = [];
  const labels = [];
  const given_mask = [];
  for (let r = 0; r < 9; r++) {
    const boardRow = [], labelRow = [], givenRow = [];
    for (let c = 0; c < 9; c++) {
      const v = _clueGrid[r][c];
      boardRow.push(v);
      labelRow.push(v || null);
      givenRow.push(v !== 0);
    }
    board.push(boardRow);
    labels.push(labelRow);
    given_mask.push(givenRow);
  }
  return { board, labels, given_mask, status: 'ready' };
}

function make_move(state, row, col, value) {
  if (row < 0 || row >= 9 || col < 0 || col >= 9) {
    return { state, valid: false, conflicts: [], message: 'Out of bounds', complete: false };
  }
  if (_clueGrid[row][col] !== 0) {
    return { state, valid: false, conflicts: [], message: 'Cannot change given cells', complete: false };
  }

  const prev = state.board[row][col];
  _history.push({ row, col, prev });
  state.board[row][col] = value;
  state.labels[row][col] = value || null;

  const conflicts = [];
  if (value) {
    for (let c = 0; c < 9; c++)
      if (c !== col && state.board[row][c] === value) conflicts.push({ row, col: c });
    for (let r = 0; r < 9; r++)
      if (r !== row && state.board[r][col] === value) conflicts.push({ row: r, col });
    const br = Math.floor(row / 3) * 3, bc = Math.floor(col / 3) * 3;
    for (let dr = 0; dr < 3; dr++)
      for (let dc = 0; dc < 3; dc++) {
        const r = br + dr, c = bc + dc;
        if (r !== row || c !== col)
          if (state.board[r][c] === value) conflicts.push({ row: r, col: c });
      }
  }

  const complete = _isBoardFull(state.board) && _getAllErrors(state.board).length === 0;
  return {
    state, valid: true, conflicts,
    message: complete ? 'Puzzle solved!' : (conflicts.length ? 'Duplicate number found' : ''),
    complete,
  };
}

function undo_move(state) {
  if (!_history.length) return state;
  const { row, col, prev } = _history.pop();
  state.board[row][col] = prev;
  state.labels[row][col] = prev || null;
  return state;
}

function check_solution(state) {
  const errors = _getAllErrors(state.board);
  if (!_isBoardFull(state.board)) {
    return { solved: false, errors, message: 'Board is not complete yet.' };
  }
  if (errors.length === 0) {
    return { solved: true, errors: [], message: 'Congratulations! Puzzle solved!' };
  }
  return { solved: false, errors, message: `${errors.length} conflict(s) found.` };
}

function get_hint(state, row, col) {
  if (row >= 0 && row < 9 && col >= 0 && col < 9 && state.board[row][col] === 0) {
    const possible = [];
    for (let v = 1; v <= 9; v++) {
      let ok = true;
      for (let c = 0; c < 9 && ok; c++) if (state.board[row][c] === v) ok = false;
      for (let r = 0; r < 9 && ok; r++) if (state.board[r][col] === v) ok = false;
      const br = Math.floor(row / 3) * 3, bc = Math.floor(col / 3) * 3;
      for (let dr = 0; dr < 3 && ok; dr++)
        for (let dc = 0; dc < 3 && ok; dc++)
          if (state.board[br + dr][bc + dc] === v) ok = false;
      if (ok) possible.push(v);
    }
    if (possible.length === 1) {
      return { value: possible[0], message: `Only ${possible[0]} is possible here.` };
    }
    if (possible.length > 1) {
      return { value: null, message: `Possible values: ${possible.join(', ')}` };
    }
  }
  for (let r = 0; r < 9; r++) {
    for (let c = 0; c < 9; c++) {
      if (state.board[r][c] !== 0) continue;
      const possible = [];
      for (let v = 1; v <= 9; v++) {
        let ok = true;
        for (let cc = 0; cc < 9 && ok; cc++) if (state.board[r][cc] === v) ok = false;
        for (let rr = 0; rr < 9 && ok; rr++) if (state.board[rr][c] === v) ok = false;
        const br = Math.floor(r / 3) * 3, bc = Math.floor(c / 3) * 3;
        for (let dr = 0; dr < 3 && ok; dr++)
          for (let dc = 0; dc < 3 && ok; dc++)
            if (state.board[br + dr][bc + dc] === v) ok = false;
        if (ok) possible.push(v);
      }
      if (possible.length === 1) {
        return { value: possible[0], message: `Cell (${r + 1},${c + 1}) can only be ${possible[0]}.` };
      }
    }
  }
  return { value: null, message: 'No obvious hint available.' };
}
