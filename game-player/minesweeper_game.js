const _GRIDS = {
  easy: {
    rows: 6, cols: 6,
    clue_grid: [
      [-1, 2, -1, -1, 2, 1],
      [-1, -1, 1, 2, -1, -1],
      [-1, -1, 4, 3, 3, 2],
      [1, 2, -1, -1, 2, -1],
      [-1, -1, 0, 1, 2, 2],
      [2, 1, 0, 0, 0, 0],
    ],
  },
  medium: {
    rows: 9, cols: 9,
    clue_grid: [
      [0, 1, 2, -1, -1, 2, 0, 0, 0],
      [0, 1, -1, -1, 4, -1, -1, 2, 1],
      [1, 1, 2, 4, 3, 3, 1, 1, 1],
      [-1, -1, 1, -1, -1, -1, -1, -1, 1],
      [0, 0, 1, 1, 1, 2, 3, 2, 1],
      [0, 0, 0, 1, 0, 0, 1, -1, -1],
      [-1, 2, 1, 0, 0, 1, 1, 2, 1],
      [2, -1, -1, 2, -1, -1, -1, 2, 0],
      [1, 2, -1, -1, 0, 1, 2, -1, -1],
    ],
  },
  hard: {
    rows: 12, cols: 12,
    clue_grid: [
      [1, -1, 2, 1, 2, -1, 1, 0, 0, 1, -1, 2],
      [2, 3, 3, -1, 2, 1, 1, 0, 0, 1, 2, -1],
      [-1, -1, 3, -1, -1, 4, 3, 1, 0, 0, 0, 0],
      [1, -1, 3, -1, -1, -1, 1, -1, 1, 1, 1, 1],
      [-1, 1, 1, 1, 1, 1, 1, -1, -1, 2, 2, 2],
      [1, 2, -1, -1, 3, 3, -1, -1, 3, 1, -1, -1],
      [0, 0, 2, -1, -1, 4, -1, -1, 0, 1, 2, 4],
      [-1, -1, 3, 2, 1, 2, -1, -1, -1, 3, 3, -1],
      [-1, -1, 2, -1, -1, -1, -1, 2, -1, -1, 0, -1],
      [-1, 2, 1, 2, -1, -1, 2, 1, 1, 0, 0, 1],
      [1, -1, -1, 1, 0, 2, 2, 2, 1, 0, -1, 1],
      [0, 1, -1, 1, 0, 0, 0, 0, 0, 0, 1, -1],
    ],
  },
};

let _ROWS = 0, _COLS = 0, _clueGrid = null;
let _history = [];

function _countAdjacentMines(board, r, c) {
  let count = 0;
  for (let dr = -1; dr <= 1; dr++)
    for (let dc = -1; dc <= 1; dc++) {
      if (dr === 0 && dc === 0) continue;
      const nr = r + dr, nc = c + dc;
      if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && board[nr][nc] === 1)
        count++;
    }
  return count;
}

function _checkClueConstraints(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      const clue = _clueGrid[r][c];
      if (clue < 0) continue;
      const actual = _countAdjacentMines(board, r, c);
      if (actual !== clue) {
        errors.push({ row: r, col: c, message: `Clue ${clue} but ${actual} adjacent mines` });
      }
    }
  }
  return errors;
}

function _checkNoMineOnClue(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      if (_clueGrid[r][c] >= 0 && board[r][c] === 1)
        errors.push({ row: r, col: c, message: 'Cannot place mine on a clue cell' });
  return errors;
}

function _getAllErrors(board) {
  const allErrs = [..._checkNoMineOnClue(board), ..._checkClueConstraints(board)];
  const seen = new Set();
  return allErrs.filter(e => {
    const k = `${e.row},${e.col}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

function _hasAnyMines(board) {
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      if (board[r][c] === 1) return true;
  return false;
}

function init_game(meta) {
  const diff = (meta && meta.difficulty) || 'easy';
  const g = _GRIDS[diff] || _GRIDS.easy;
  _ROWS = g.rows;
  _COLS = g.cols;
  _clueGrid = g.clue_grid;
  _history = [];

  const board = [];
  const labels = [];
  const given_mask = [];
  for (let r = 0; r < _ROWS; r++) {
    const boardRow = [], labelRow = [], givenRow = [];
    for (let c = 0; c < _COLS; c++) {
      const v = _clueGrid[r][c];
      boardRow.push(0);
      if (v >= 0) {
        labelRow.push(v);
        givenRow.push(true);
      } else {
        labelRow.push(null);
        givenRow.push(false);
      }
    }
    board.push(boardRow);
    labels.push(labelRow);
    given_mask.push(givenRow);
  }
  return { board, labels, given_mask, status: 'ready' };
}

function make_move(state, row, col, value) {
  if (row < 0 || row >= _ROWS || col < 0 || col >= _COLS) {
    return { state, valid: false, conflicts: [], message: 'Out of bounds', complete: false };
  }
  if (_clueGrid[row][col] >= 0) {
    return { state, valid: false, conflicts: [], message: 'Cannot place mine on clue cell', complete: false };
  }
  const prev = state.board[row][col];
  const next = prev === 1 ? 0 : 1;
  _history.push({ row, col, prev });
  state.board[row][col] = next;

  const conflicts = [];
  if (next === 1) {
    for (let dr = -1; dr <= 1; dr++)
      for (let dc = -1; dc <= 1; dc++) {
        if (dr === 0 && dc === 0) continue;
        const nr = row + dr, nc = col + dc;
        if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS) {
          const clue = _clueGrid[nr][nc];
          if (clue >= 0 && _countAdjacentMines(state.board, nr, nc) > clue) {
            conflicts.push({ row: nr, col: nc });
          }
        }
      }
  }

  const complete = _hasAnyMines(state.board) && _getAllErrors(state.board).length === 0;
  return {
    state, valid: true, conflicts,
    message: complete ? 'Puzzle solved!' : (conflicts.length ? 'Clue exceeded' : ''),
    complete,
  };
}

function undo_move(state) {
  if (!_history.length) return state;
  const { row, col, prev } = _history.pop();
  state.board[row][col] = prev;
  return state;
}

function check_solution(state) {
  const errors = _getAllErrors(state.board);
  if (errors.length === 0 && _hasAnyMines(state.board)) {
    return { solved: true, errors: [], message: 'Congratulations! Puzzle solved!' };
  }
  return {
    solved: false, errors,
    message: errors.length ? `${errors.length} rule violation(s) found.` : 'Place more mines.',
  };
}

function get_hint(state, row, col) {
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      const clue = _clueGrid[r][c];
      if (clue < 0) continue;
      const unknowns = [], mines = [];
      for (let dr = -1; dr <= 1; dr++)
        for (let dc = -1; dc <= 1; dc++) {
          if (dr === 0 && dc === 0) continue;
          const nr = r + dr, nc = c + dc;
          if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && _clueGrid[nr][nc] < 0) {
            if (state.board[nr][nc] === 1) mines.push([nr, nc]);
            else unknowns.push([nr, nc]);
          }
        }
      if (mines.length === clue && unknowns.length > 0) {
        return { value: 0, message: `All mines around clue at (${r+1},${c+1}) found. Remaining neighbors are safe.` };
      }
      if (unknowns.length === clue - mines.length && unknowns.length > 0) {
        return { value: 1, message: `Clue at (${r+1},${c+1}) needs ${clue - mines.length} more mine(s). All unknown neighbors must be mines.` };
      }
    }
  }
  return { value: null, message: 'No obvious hint available.' };
}
