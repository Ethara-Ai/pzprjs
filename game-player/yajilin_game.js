const _GRIDS = {
  easy: {
    rows: 4, cols: 4,
    clues: [
      [null, null, null, null],
      [null, null, null, {dir:'down', num:1}],
      [null, null, null, null],
      [null, {dir:'right', num:2}, null, null],
    ],
  },
  medium: {
    rows: 6, cols: 6,
    clues: [
      [null, null, null, null, null, null],
      [null, {dir:'down', num:2}, null, null, null, null],
      [null, null, null, {dir:'down', num:2}, null, null],
      [null, null, null, null, null, {dir:'left', num:1}],
      [null, null, null, null, null, null],
      [null, null, null, null, {dir:'down', num:3}, {dir:'left', num:1}],
    ],
  },
  hard: {
    rows: 7, cols: 7,
    clues: [
      [null, null, null, {dir:'down', num:2}, null, null, null],
      [null, null, null, null, null, null, null],
      [null, null, null, null, null, null, null],
      [{dir:'down', num:3}, null, null, null, null, null, null],
      [null, null, null, {dir:'down', num:1}, null, null, null],
      [null, null, null, null, null, null, null],
      [null, null, null, {dir:'down', num:3}, null, null, {dir:'down', num:0}],
    ],
  },
};

let _ROWS = 0, _COLS = 0, _clues = null;
let _history = [];

function _isClueCell(r, c) {
  return _clues[r][c] !== null;
}

function _countShadedInDirection(board, row, col, dir) {
  let count = 0;
  let r = row, c = col;
  const deltas = { down: [1, 0], up: [-1, 0], right: [0, 1], left: [0, -1] };
  const [dr, dc] = deltas[dir];
  r += dr; c += dc;
  while (r >= 0 && r < _ROWS && c >= 0 && c < _COLS) {
    if (board[r][c] === 1) count++;
    r += dr; c += dc;
  }
  return count;
}

function _checkClueConstraints(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      const clue = _clues[r][c];
      if (!clue) continue;
      const actual = _countShadedInDirection(board, r, c, clue.dir);
      if (actual > clue.num) {
        errors.push({ row: r, col: c, message: `Clue says ${clue.num} shaded ${clue.dir}, but found ${actual}` });
      }
    }
  }
  return errors;
}

function _checkClueExact(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      const clue = _clues[r][c];
      if (!clue) continue;
      const actual = _countShadedInDirection(board, r, c, clue.dir);
      if (actual !== clue.num) {
        errors.push({ row: r, col: c, message: `Clue says ${clue.num} shaded ${clue.dir}, but found ${actual}` });
      }
    }
  }
  return errors;
}

function _checkNoAdjacentShaded(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] !== 1) continue;
      for (const [dr, dc] of [[0,1],[1,0]]) {
        const nr = r + dr, nc = c + dc;
        if (nr < _ROWS && nc < _COLS && board[nr][nc] === 1) {
          errors.push({ row: r, col: c, message: 'No adjacent shaded cells allowed' });
          errors.push({ row: nr, col: nc, message: 'No adjacent shaded cells allowed' });
        }
      }
    }
  }
  return errors;
}

function _getAllErrors(board) {
  const allErrs = [
    ..._checkNoAdjacentShaded(board),
    ..._checkClueExact(board),
  ];
  const seen = new Set();
  return allErrs.filter(e => {
    const k = `${e.row},${e.col}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

function _boardIsSolved(board) {
  let hasShading = false;
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      if (board[r][c] === 1) { hasShading = true; break; }
  if (!hasShading) return false;
  return _getAllErrors(board).length === 0;
}

function init_game(meta) {
  const diff = (meta && meta.difficulty) || 'easy';
  const g = _GRIDS[diff] || _GRIDS.easy;
  _ROWS = g.rows;
  _COLS = g.cols;
  _clues = g.clues;
  _history = [];

  const board = [];
  const labels = [];
  const given_mask = [];
  for (let r = 0; r < _ROWS; r++) {
    board.push(new Array(_COLS).fill(0));
    const labelRow = [];
    const givenRow = [];
    for (let c = 0; c < _COLS; c++) {
      const clue = _clues[r][c];
      if (clue) {
        const arrows = { down: '↓', up: '↑', right: '→', left: '←' };
        labelRow.push(`${arrows[clue.dir]}${clue.num}`);
        givenRow.push(true);
      } else {
        labelRow.push(null);
        givenRow.push(false);
      }
    }
    labels.push(labelRow);
    given_mask.push(givenRow);
  }
  return { board, labels, given_mask, status: 'ready' };
}

function make_move(state, row, col, value) {
  if (row < 0 || row >= _ROWS || col < 0 || col >= _COLS) {
    return { state, valid: false, conflicts: [], message: 'Out of bounds', complete: false };
  }
  if (_isClueCell(row, col)) {
    return { state, valid: false, conflicts: [], message: 'Cannot shade clue cells', complete: false };
  }
  const prev = state.board[row][col];
  const next = prev === 1 ? 0 : 1;
  _history.push({ row, col, prev });
  state.board[row][col] = next;

  const conflicts = [];
  if (next === 1) {
    for (const [dr, dc] of [[0,1],[0,-1],[1,0],[-1,0]]) {
      const nr = row + dr, nc = col + dc;
      if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && state.board[nr][nc] === 1) {
        conflicts.push({ row: nr, col: nc });
      }
    }
  }

  const complete = _boardIsSolved(state.board);
  return {
    state, valid: true, conflicts,
    message: complete ? 'Puzzle solved!' : (conflicts.length ? 'Adjacent shaded cells' : ''),
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
  if (errors.length === 0 && _boardIsSolved(state.board)) {
    return { solved: true, errors: [], message: 'Congratulations! Puzzle solved!' };
  }
  return {
    solved: false, errors,
    message: errors.length ? `${errors.length} rule violation(s) found.` : 'Puzzle not yet complete.',
  };
}

function get_hint(state, row, col) {
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      const clue = _clues[r][c];
      if (!clue) continue;
      if (clue.num === 0) {
        const deltas = { down: [1, 0], up: [-1, 0], right: [0, 1], left: [0, -1] };
        const [dr, dc] = deltas[clue.dir];
        let cr = r + dr, cc = c + dc;
        while (cr >= 0 && cr < _ROWS && cc >= 0 && cc < _COLS) {
          if (state.board[cr][cc] === 1) {
            return { value: 0, message: `Cell (${cr},${cc}) must be unshaded — clue at (${r},${c}) says 0 ${clue.dir}.` };
          }
          cr += dr; cc += dc;
        }
      }
    }
  }
  return { value: null, message: 'No obvious hint available.' };
}
