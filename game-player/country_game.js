const _GRIDS = {
  easy: {
    rows: 5, cols: 5,
    room_grid: [
      [0, 0, 0, 0, 0],
      [0, 0, 0, 0, 0],
      [1, 1, 2, 2, 2],
      [3, 3, 4, 5, 2],
      [3, 3, 4, 5, 2],
    ],
    clues: { 0: 3, 1: 1, 2: 5, 3: 4, 5: 2 },
  },
  medium: {
    rows: 10, cols: 10,
    room_grid: [
      [0, 0, 0, 0, 1, 1, 1, 1, 2, 2],
      [0, 0, 3, 3, 3, 3, 3, 3, 2, 4],
      [0, 3, 3, 5, 5, 6, 6, 3, 4, 4],
      [7, 3, 8, 5, 9, 9, 6, 3, 4, 10],
      [7, 3, 8, 11, 12, 12, 6, 3, 10, 10],
      [7, 8, 8, 11, 3, 3, 3, 3, 13, 10],
      [7, 14, 8, 11, 3, 13, 13, 13, 13, 10],
      [7, 14, 14, 11, 3, 15, 13, 15, 15, 16],
      [7, 17, 17, 11, 11, 15, 15, 15, 16, 16],
      [7, 17, 17, 11, 18, 19, 19, 19, 19, 19],
    ],
    clues: { 1: 4, 2: 3, 7: 6, 10: 1, 16: 2, 19: 5 },
  },
  hard: {
    rows: 15, cols: 15,
    room_grid: [
      [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 6, 6],
      [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 6, 6],
      [7, 7, 1, 1, 8, 8, 9, 9, 10, 10, 11, 11, 12, 13, 13],
      [7, 7, 14, 14, 8, 8, 9, 9, 10, 10, 11, 11, 12, 13, 13],
      [7, 7, 14, 14, 8, 8, 15, 15, 15, 16, 17, 17, 12, 18, 18],
      [19, 19, 20, 20, 20, 21, 21, 22, 22, 16, 17, 17, 12, 18, 18],
      [19, 19, 20, 20, 20, 21, 21, 22, 22, 16, 17, 17, 23, 23, 23],
      [24, 24, 24, 25, 25, 25, 26, 26, 26, 16, 16, 16, 23, 23, 23],
      [24, 24, 24, 27, 27, 25, 28, 28, 29, 29, 30, 30, 30, 31, 31],
      [32, 32, 33, 27, 27, 25, 28, 28, 29, 29, 30, 30, 30, 31, 31],
      [32, 32, 33, 27, 27, 25, 34, 34, 34, 35, 35, 36, 36, 37, 37],
      [38, 38, 33, 39, 39, 40, 40, 41, 41, 35, 35, 36, 36, 37, 37],
      [38, 38, 33, 39, 39, 40, 40, 41, 41, 35, 35, 42, 42, 37, 37],
      [43, 43, 44, 44, 44, 45, 45, 46, 46, 47, 47, 42, 42, 48, 48],
      [43, 43, 44, 44, 44, 45, 45, 46, 46, 47, 47, 42, 42, 48, 48],
    ],
    clues: {
      0: 3, 1: 2, 2: 2, 3: 3, 4: 4, 5: 4, 6: 1, 7: 3, 9: 2, 11: 2,
      13: 4, 14: 4, 18: 2, 20: 4, 22: 4, 23: 4, 24: 3, 25: 6, 26: 2,
      28: 3, 29: 3, 31: 1, 32: 4, 33: 4, 37: 4, 38: 2, 41: 1, 42: 3,
      44: 3, 48: 4,
    },
  },
};

let _ROWS = 0, _COLS = 0, _roomGrid = null, _clues = null;
let _history = [];

function _checkRoomClues(board) {
  const errors = [];
  const roomCounts = {};
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      if (board[r][c] === 1) {
        const room = _roomGrid[r][c];
        roomCounts[room] = (roomCounts[room] || 0) + 1;
      }

  for (const [roomStr, expected] of Object.entries(_clues)) {
    const room = parseInt(roomStr);
    const actual = roomCounts[room] || 0;
    if (actual > expected) {
      for (let r = 0; r < _ROWS; r++)
        for (let c = 0; c < _COLS; c++)
          if (_roomGrid[r][c] === room && board[r][c] === 1) {
            errors.push({ row: r, col: c, message: `Room ${room}: ${actual} shaded but clue says ${expected}` });
            break;
          }
    }
  }
  return errors;
}

function _checkRoomCluesExact(board) {
  const errors = [];
  const roomCounts = {};
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      if (board[r][c] === 1) {
        const room = _roomGrid[r][c];
        roomCounts[room] = (roomCounts[room] || 0) + 1;
      }

  for (const [roomStr, expected] of Object.entries(_clues)) {
    const room = parseInt(roomStr);
    const actual = roomCounts[room] || 0;
    if (actual !== expected) {
      for (let r = 0; r < _ROWS; r++)
        for (let c = 0; c < _COLS; c++)
          if (_roomGrid[r][c] === room) {
            errors.push({ row: r, col: c, message: `Room ${room}: has ${actual} shaded, needs ${expected}` });
            break;
          }
    }
  }
  return errors;
}

function _checkShadedContiguousInRoom(board) {
  const errors = [];
  const roomIds = new Set();
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      roomIds.add(_roomGrid[r][c]);

  for (const roomId of roomIds) {
    const shaded = [];
    for (let r = 0; r < _ROWS; r++)
      for (let c = 0; c < _COLS; c++)
        if (_roomGrid[r][c] === roomId && board[r][c] === 1)
          shaded.push([r, c]);
    if (shaded.length <= 1) continue;
    const set = new Set(shaded.map(([r, c]) => `${r},${c}`));
    const visited = new Set();
    const queue = [shaded[0]];
    visited.add(`${shaded[0][0]},${shaded[0][1]}`);
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
    if (visited.size !== shaded.length) {
      errors.push({ row: shaded[0][0], col: shaded[0][1], message: `Room ${roomId}: shaded cells not contiguous` });
    }
  }
  return errors;
}

function _checkNoAdjacentShadedAcrossRooms(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] !== 1) continue;
      for (const [dr, dc] of [[0,1],[1,0]]) {
        const nr = r + dr, nc = c + dc;
        if (nr < _ROWS && nc < _COLS && board[nr][nc] === 1) {
          if (_roomGrid[r][c] !== _roomGrid[nr][nc]) {
            errors.push({ row: r, col: c, message: 'Adjacent shaded cells in different rooms not allowed' });
          }
        }
      }
    }
  }
  return errors;
}

function _getAllErrors(board) {
  const allErrs = [
    ..._checkRoomCluesExact(board),
    ..._checkShadedContiguousInRoom(board),
    ..._checkNoAdjacentShadedAcrossRooms(board),
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
    const labelRow = [];
    for (let c = 0; c < _COLS; c++) {
      const room = _roomGrid[r][c];
      if (_clues[room] !== undefined) {
        labelRow.push(`${room}:${_clues[room]}`);
      } else {
        labelRow.push(room);
      }
    }
    labels.push(labelRow);
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
    const room = _roomGrid[row][col];
    const clue = _clues[room];
    if (clue !== undefined) {
      let count = 0;
      for (let r = 0; r < _ROWS; r++)
        for (let c = 0; c < _COLS; c++)
          if (_roomGrid[r][c] === room && state.board[r][c] === 1) count++;
      if (count > clue) conflicts.push({ row, col });
    }
    for (const [dr, dc] of [[0,1],[0,-1],[1,0],[-1,0]]) {
      const nr = row + dr, nc = col + dc;
      if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS &&
          state.board[nr][nc] === 1 && _roomGrid[nr][nc] !== room) {
        conflicts.push({ row: nr, col: nc });
      }
    }
  }

  const complete = _hasAnyShading(state.board) && _getAllErrors(state.board).length === 0;
  return {
    state, valid: true, conflicts,
    message: complete ? 'Puzzle solved!' : (conflicts.length ? 'Rule violation detected' : ''),
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
    message: errors.length ? `${errors.length} rule violation(s) found.` : 'Not complete yet.',
  };
}

function get_hint(state, row, col) {
  for (const [roomStr, expected] of Object.entries(_clues)) {
    const room = parseInt(roomStr);
    let count = 0, emptyCells = [];
    for (let r = 0; r < _ROWS; r++)
      for (let c = 0; c < _COLS; c++)
        if (_roomGrid[r][c] === room) {
          if (state.board[r][c] === 1) count++;
          else emptyCells.push([r, c]);
        }
    if (count === expected && emptyCells.length > 0) {
      return { value: 0, message: `Room ${room} already has ${expected} shaded cells. Don't shade more.` };
    }
    if (emptyCells.length === expected - count && emptyCells.length > 0) {
      return { value: 1, message: `Room ${room} needs ${expected - count} more shaded cell(s) and has exactly that many empty.` };
    }
  }
  return { value: null, message: 'No obvious hint available.' };
}
