const _GRIDS = {
  easy: {
    rows: 7, cols: 7,
    room_grid: [
      [0, 0, 0, 0, 1, 1, 2],
      [0, 0, 0, 0, 1, 1, 3],
      [4, 4, 5, 6, 1, 1, 3],
      [7, 7, 5, 6, 8, 8, 8],
      [7, 7, 5, 6, 8, 8, 8],
      [7, 7, 5, 9, 9, 9, 9],
      [10, 11, 11, 9, 9, 9, 9],
    ],
    clues: {},
  },
  medium: {
    rows: 8, cols: 10,
    room_grid: [
      [0, 0, 1, 1, 1, 2, 2, 3, 3, 3],
      [4, 4, 1, 1, 1, 5, 5, 3, 3, 3],
      [4, 4, 6, 6, 6, 5, 5, 7, 7, 7],
      [4, 4, 6, 6, 6, 5, 5, 7, 7, 7],
      [8, 8, 8, 9, 9, 10, 10, 10, 11, 11],
      [8, 8, 8, 9, 9, 10, 10, 10, 11, 11],
      [12, 12, 12, 9, 9, 13, 13, 13, 11, 11],
      [12, 12, 12, 14, 14, 13, 13, 13, 15, 15],
    ],
    clues: {},
  },
  hard: {
    rows: 8, cols: 10,
    room_grid: [
      [0, 0, 1, 1, 1, 2, 2, 3, 3, 3],
      [4, 4, 1, 1, 1, 5, 5, 3, 3, 3],
      [4, 4, 6, 6, 6, 5, 5, 7, 7, 7],
      [4, 4, 6, 6, 6, 5, 5, 7, 7, 7],
      [8, 8, 8, 9, 9, 10, 10, 10, 11, 11],
      [8, 8, 8, 9, 9, 10, 10, 10, 11, 11],
      [12, 12, 12, 9, 9, 13, 13, 13, 11, 11],
      [12, 12, 12, 14, 14, 13, 13, 13, 15, 15],
    ],
    clues: {},
  },
};

let _ROWS = 0, _COLS = 0, _roomGrid = null, _clues = null;
let _history = [];

function _getRoomIds() {
  const ids = new Set();
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      ids.add(_roomGrid[r][c]);
  return [...ids];
}

function _checkNo2x2(board) {
  const errors = [];
  for (let r = 0; r < _ROWS - 1; r++) {
    for (let c = 0; c < _COLS - 1; c++) {
      if (board[r][c] === 1 && board[r][c+1] === 1 &&
          board[r+1][c] === 1 && board[r+1][c+1] === 1) {
        errors.push({ row: r, col: c, message: 'No 2×2 shaded area allowed' });
      }
    }
  }
  return errors;
}

function _checkUnshadedConnected(board) {
  const unshaded = [];
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      if (board[r][c] === 0) unshaded.push([r, c]);
  if (unshaded.length <= 1) return [];
  const set = new Set(unshaded.map(([r, c]) => `${r},${c}`));
  const visited = new Set();
  const queue = [unshaded[0]];
  visited.add(`${unshaded[0][0]},${unshaded[0][1]}`);
  while (queue.length) {
    const [r, c] = queue.shift();
    for (const [dr, dc] of [[0,1],[0,-1],[1,0],[-1,0]]) {
      const key = `${r+dr},${c+dc}`;
      if (set.has(key) && !visited.has(key)) {
        visited.add(key);
        queue.push([r+dr, c+dc]);
      }
    }
  }
  if (visited.size !== unshaded.length) {
    return [{ row: unshaded[0][0], col: unshaded[0][1], message: 'All unshaded cells must be connected' }];
  }
  return [];
}

function _checkNoUnshadedLineSpansRooms(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    let start = -1;
    let rooms = new Set();
    for (let c = 0; c <= _COLS; c++) {
      if (c < _COLS && board[r][c] === 0) {
        if (start === -1) start = c;
        rooms.add(_roomGrid[r][c]);
      } else {
        if (rooms.size > 2) {
          errors.push({ row: r, col: start, message: `Horizontal unshaded line spans ${rooms.size} rooms (max 2)` });
        }
        start = -1;
        rooms = new Set();
      }
    }
  }
  for (let c = 0; c < _COLS; c++) {
    let start = -1;
    let rooms = new Set();
    for (let r = 0; r <= _ROWS; r++) {
      if (r < _ROWS && board[r][c] === 0) {
        if (start === -1) start = r;
        rooms.add(_roomGrid[r][c]);
      } else {
        if (rooms.size > 2) {
          errors.push({ row: start, col: c, message: `Vertical unshaded line spans ${rooms.size} rooms (max 2)` });
        }
        start = -1;
        rooms = new Set();
      }
    }
  }
  return errors;
}

function _checkRoomClues(board) {
  const errors = [];
  for (const [roomIdStr, expected] of Object.entries(_clues)) {
    const roomId = parseInt(roomIdStr);
    let count = 0;
    for (let r = 0; r < _ROWS; r++)
      for (let c = 0; c < _COLS; c++)
        if (_roomGrid[r][c] === roomId && board[r][c] === 1) count++;
    if (count !== expected) {
      for (let r = 0; r < _ROWS; r++)
        for (let c = 0; c < _COLS; c++)
          if (_roomGrid[r][c] === roomId) {
            errors.push({ row: r, col: c, message: `Room needs ${expected} shaded (has ${count})` });
            break;
          }
    }
  }
  return errors;
}

function _getAllErrors(board) {
  const allErrs = [
    ..._checkNo2x2(board),
    ..._checkUnshadedConnected(board),
    ..._checkNoUnshadedLineSpansRooms(board),
    ..._checkRoomClues(board),
  ];
  const seen = new Set();
  return allErrs.filter(e => {
    const k = `${e.row},${e.col}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

function _hasAnyShading(board) {
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
  _roomGrid = g.room_grid;
  _clues = g.clues || {};
  _history = [];

  const board = [];
  const labels = [];
  const given_mask = [];
  for (let r = 0; r < _ROWS; r++) {
    board.push(new Array(_COLS).fill(0));
    labels.push(_roomGrid[r].slice());
    given_mask.push(new Array(_COLS).fill(false));
  }
  return { board, labels, given_mask, status: 'ready' };
}

function make_move(state, row, col, value) {
  if (row < 0 || row >= _ROWS || col < 0 || col >= _COLS) {
    return { state, valid: false, conflicts: [], message: 'Out of bounds', complete: false };
  }
  const prev = state.board[row][col];
  const next = prev === 1 ? 0 : 1;
  _history.push({ row, col, prev });
  state.board[row][col] = next;

  const conflicts = [];
  if (next === 1) {
    for (let dr = -1; dr <= 0; dr++) {
      for (let dc = -1; dc <= 0; dc++) {
        const r0 = row + dr, c0 = col + dc;
        if (r0 >= 0 && r0 + 1 < _ROWS && c0 >= 0 && c0 + 1 < _COLS) {
          if (state.board[r0][c0] === 1 && state.board[r0][c0+1] === 1 &&
              state.board[r0+1][c0] === 1 && state.board[r0+1][c0+1] === 1) {
            conflicts.push({ row: r0, col: c0 });
          }
        }
      }
    }
  }

  const complete = _hasAnyShading(state.board) && _getAllErrors(state.board).length === 0;
  return {
    state, valid: true, conflicts,
    message: complete ? 'Puzzle solved!' : (conflicts.length ? '2×2 violation' : ''),
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
  if (errors.length === 0 && _hasAnyShading(state.board)) {
    return { solved: true, errors: [], message: 'Congratulations! Puzzle solved!' };
  }
  return {
    solved: false, errors,
    message: errors.length ? `${errors.length} rule violation(s) found.` : 'No shading placed yet.',
  };
}

function get_hint(state, row, col) {
  return { value: null, message: 'No obvious hint available. Try using Check to find violations.' };
}
