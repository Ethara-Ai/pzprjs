/* ================================================================
 *  LITS – rule-based game logic (no hardcoded solutions)
 *  Interface: init_game, make_move, undo_move, check_solution, get_hint
 * ================================================================ */

const _GRIDS = {
  easy: {
    rows: 5, cols: 5,
    room_grid: [
      [3, 3, 3, 3, 3],
      [0, 0, 0, 3, 3],
      [1, 1, 0, 0, 0],
      [1, 1, 2, 0, 0],
      [1, 1, 2, 2, 2],
    ],
  },
  medium: {
    rows: 6, cols: 6,
    room_grid: [
      [4, 4, 4, 3, 3, 3],
      [1, 4, 3, 3, 3, 5],
      [1, 4, 0, 3, 3, 5],
      [1, 0, 0, 0, 5, 5],
      [1, 2, 0, 2, 5, 5],
      [1, 2, 2, 2, 2, 5],
    ],
  },
  hard: {
    rows: 7, cols: 7,
    room_grid: [
      [6, 6, 6, 6, 6, 3, 3],
      [1, 1, 1, 1, 1, 3, 3],
      [4, 4, 4, 4, 1, 3, 3],
      [4, 4, 2, 2, 1, 3, 3],
      [2, 2, 2, 2, 1, 5, 5],
      [0, 2, 2, 2, 5, 5, 5],
      [0, 0, 0, 5, 5, 5, 5],
    ],
  },
};

let _ROWS = 0, _COLS = 0, _roomGrid = null;
let _history = [];

/* ---------- tetromino shape classification ---------- */
const _TETROMINOS = { L: 'L', I: 'I', T: 'T', S: 'S' };

function _classifyTetromino(cells) {
  if (cells.length !== 4) return null;
  // Normalize to origin
  const minR = Math.min(...cells.map(c => c[0]));
  const minC = Math.min(...cells.map(c => c[1]));
  const norm = cells.map(([r, c]) => [r - minR, c - minC]);
  norm.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const key = norm.map(([r, c]) => `${r},${c}`).join('|');

  const shapes = {
    // I (4 rotations → 2 unique)
    '0,0|0,1|0,2|0,3': 'I', '0,0|1,0|2,0|3,0': 'I',
    // T (4 rotations)
    '0,0|0,1|0,2|1,1': 'T', '0,0|1,0|1,1|2,0': 'T',
    '0,1|1,0|1,1|1,2': 'T', '0,0|0,1|1,0|2,0': 'T',  // correction
    '0,1|1,0|1,1|2,1': 'T', '0,0|0,1|1,1|2,1': 'T',
    // L (4 rotations × 2 mirrors = 8 → 4 L + 4 J, all count as L)
    '0,0|1,0|2,0|2,1': 'L', '0,0|0,1|0,2|1,0': 'L',
    '0,0|0,1|1,1|2,1': 'L', '0,2|1,0|1,1|1,2': 'L',
    '0,1|1,1|2,0|2,1': 'L', '0,0|0,1|0,2|1,2': 'L',
    '0,0|0,1|1,0|2,0': 'L', '0,0|1,0|1,1|1,2': 'L',
    // S (2 rotations × 2 mirrors = 4 → S + Z, all count as S)
    '0,0|0,1|1,1|1,2': 'S', '0,1|1,0|1,1|2,0': 'S',
    '0,1|0,2|1,0|1,1': 'S', '0,0|1,0|1,1|2,1': 'S',
  };
  return shapes[key] || null;
}

/* ---------- rule checks ---------- */
function _getRoomCells(board, roomId) {
  const cells = [];
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      if (_roomGrid[r][c] === roomId && board[r][c] === 1)
        cells.push([r, c]);
  return cells;
}

function _getAllRoomIds() {
  const ids = new Set();
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      ids.add(_roomGrid[r][c]);
  return [...ids];
}

function _areCellsContiguous(cells) {
  if (cells.length <= 1) return true;
  const set = new Set(cells.map(([r, c]) => `${r},${c}`));
  const visited = new Set();
  const queue = [cells[0]];
  visited.add(`${cells[0][0]},${cells[0][1]}`);
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
  return visited.size === cells.length;
}

function _checkExactly4PerRoom(board) {
  const errors = [];
  for (const roomId of _getAllRoomIds()) {
    const cells = _getRoomCells(board, roomId);
    if (cells.length !== 4) {
      for (const [r, c] of cells)
        errors.push({ row: r, col: c, message: `Room ${roomId}: need exactly 4 shaded cells (has ${cells.length})` });
    }
  }
  return errors;
}

function _checkContiguousInRoom(board) {
  const errors = [];
  for (const roomId of _getAllRoomIds()) {
    const cells = _getRoomCells(board, roomId);
    if (cells.length > 1 && !_areCellsContiguous(cells)) {
      for (const [r, c] of cells)
        errors.push({ row: r, col: c, message: `Room ${roomId}: shaded cells not contiguous` });
    }
  }
  return errors;
}

function _checkValidTetrominoes(board) {
  const errors = [];
  for (const roomId of _getAllRoomIds()) {
    const cells = _getRoomCells(board, roomId);
    if (cells.length === 4) {
      const shape = _classifyTetromino(cells);
      if (!shape) {
        for (const [r, c] of cells)
          errors.push({ row: r, col: c, message: `Room ${roomId}: shaded cells don't form a valid LITS tetromino` });
      }
    }
  }
  return errors;
}

function _checkNo2x2(board) {
  const errors = [];
  for (let r = 0; r < _ROWS - 1; r++) {
    for (let c = 0; c < _COLS - 1; c++) {
      if (board[r][c] === 1 && board[r][c+1] === 1 &&
          board[r+1][c] === 1 && board[r+1][c+1] === 1) {
        errors.push({ row: r, col: c, message: 'No 2×2 fully shaded area allowed' });
        errors.push({ row: r, col: c+1, message: 'No 2×2 fully shaded area allowed' });
        errors.push({ row: r+1, col: c, message: 'No 2×2 fully shaded area allowed' });
        errors.push({ row: r+1, col: c+1, message: 'No 2×2 fully shaded area allowed' });
      }
    }
  }
  return errors;
}

function _checkNoAdjacentSameShape(board) {
  const errors = [];
  const roomShapes = {};
  for (const roomId of _getAllRoomIds()) {
    const cells = _getRoomCells(board, roomId);
    if (cells.length === 4) {
      roomShapes[roomId] = _classifyTetromino(cells);
    }
  }

  // Find adjacent rooms that share a border and have same shape
  const checkedPairs = new Set();
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] !== 1) continue;
      const myRoom = _roomGrid[r][c];
      for (const [dr, dc] of [[0,1],[0,-1],[1,0],[-1,0]]) {
        const nr = r + dr, nc = c + dc;
        if (nr < 0 || nr >= _ROWS || nc < 0 || nc >= _COLS) continue;
        if (board[nr][nc] !== 1) continue;
        const adjRoom = _roomGrid[nr][nc];
        if (adjRoom === myRoom) continue;
        const pairKey = Math.min(myRoom, adjRoom) + ',' + Math.max(myRoom, adjRoom);
        if (checkedPairs.has(pairKey)) continue;
        checkedPairs.add(pairKey);
        if (roomShapes[myRoom] && roomShapes[adjRoom] &&
            roomShapes[myRoom] === roomShapes[adjRoom]) {
          errors.push({ row: r, col: c, message: `Adjacent rooms ${myRoom} & ${adjRoom} have same shape (${roomShapes[myRoom]})` });
          errors.push({ row: nr, col: nc, message: `Adjacent rooms ${myRoom} & ${adjRoom} have same shape (${roomShapes[myRoom]})` });
        }
      }
    }
  }
  return errors;
}

function _checkAllShadedConnected(board) {
  const shaded = [];
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      if (board[r][c] === 1) shaded.push([r, c]);
  if (shaded.length <= 1) return [];
  if (!_areCellsContiguous(shaded)) {
    return [{ row: shaded[0][0], col: shaded[0][1], message: 'All shaded cells must be connected' }];
  }
  return [];
}

/* ---------- aggregate ---------- */
function _getAllErrors(board) {
  const allErrs = [
    ..._checkExactly4PerRoom(board),
    ..._checkContiguousInRoom(board),
    ..._checkValidTetrominoes(board),
    ..._checkNo2x2(board),
    ..._checkNoAdjacentSameShape(board),
    ..._checkAllShadedConnected(board),
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

function _boardIsSolved(board) {
  if (!_hasAnyShading(board)) return false;
  // Each room needs exactly 4 shaded
  for (const roomId of _getAllRoomIds()) {
    if (_getRoomCells(board, roomId).length !== 4) return false;
  }
  return _getAllErrors(board).length === 0;
}

/* ---------- interface ---------- */
function init_game(meta) {
  const diff = (meta && meta.difficulty) || 'easy';
  const g = _GRIDS[diff] || _GRIDS.easy;
  _ROWS = g.rows;
  _COLS = g.cols;
  _roomGrid = g.room_grid;
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

  // Quick conflict check
  const conflicts = [];
  // 2×2 check around cell
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

  const complete = _boardIsSolved(state.board);
  return {
    state,
    valid: true,
    conflicts,
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
    // Verify all rooms have 4
    let allFull = true;
    for (const roomId of _getAllRoomIds()) {
      if (_getRoomCells(state.board, roomId).length !== 4) { allFull = false; break; }
    }
    if (allFull) return { solved: true, errors: [], message: 'Congratulations! Puzzle solved!' };
  }
  return {
    solved: false,
    errors,
    message: errors.length ? `${errors.length} rule violation(s) found.` : 'Not all rooms have 4 shaded cells yet.',
  };
}

function get_hint(state, row, col) {
  // Find a room with < 4 shaded that has forced placements
  for (const roomId of _getAllRoomIds()) {
    const shaded = _getRoomCells(state.board, roomId);
    if (shaded.length >= 4) continue;
    // Find empty cells in this room
    const emptyCells = [];
    for (let r = 0; r < _ROWS; r++)
      for (let c = 0; c < _COLS; c++)
        if (_roomGrid[r][c] === roomId && state.board[r][c] === 0)
          emptyCells.push([r, c]);
    // If room needs exactly as many cells as available → all must be shaded
    const needed = 4 - shaded.length;
    if (emptyCells.length === needed && emptyCells.length > 0) {
      return { value: 1, message: `Room ${roomId} has exactly ${needed} empty cell(s) left — shade them all.` };
    }
  }
  return { value: null, message: 'No obvious hint available. Try checking rule violations.' };
}
