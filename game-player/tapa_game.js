// Tapa - Rule-based game logic
// Shade cells following tapa clue constraints.

const _GRIDS = {
  easy: {
    rows: 5, cols: 5,
    // null = empty, array = clue values (e.g. [1,3] means two groups of 1 and 3)
    grid: [
      [[2], null, null, null, null],
      [null, null, null, null, null],
      [null, null, [1,1,2], [1,3], null],
      [null, [7], null, null, null],
      [null, null, null, null, null]
    ]
  },
  medium: {
    rows: 5, cols: 6,
    grid: [
      [null, null, null, [3], null, null],
      [[5], null, null, null, null, null],
      [null, null, null, null, [1,4], [1,2]],
      [null, [6], null, null, null, null],
      [[1], null, null, null, null, null]
    ]
  },
  hard: {
    rows: 6, cols: 6,
    grid: [
      [null, null, null, null, [1], [1]],
      [null, null, [1,3], null, null, null],
      [null, null, null, null, null, null],
      [null, null, null, null, null, null],
      [null, null, null, null, null, [5]],
      [null, null, [1,3], null, null, null]
    ]
  }
};

let _ROWS = 0, _COLS = 0, _GRID = null, _history = [];

const _DIRS8 = [[-1,-1],[-1,0],[-1,1],[0,1],[1,1],[1,0],[1,-1],[0,-1]];
const _DIRS4 = [[-1,0],[1,0],[0,-1],[0,1]];

// Get the 8 neighbors in clockwise ring order around (r,c)
function _getRing(r, c) {
  const ring = [];
  for (const [dr, dc] of _DIRS8) {
    const nr = r + dr, nc = c + dc;
    if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS) {
      ring.push([nr, nc, true]);
    } else {
      ring.push([nr, nc, false]);
    }
  }
  return ring;
}

// Check if a clue at (r,c) is satisfied by the current board state
// Returns: true (satisfied), false (violated), null (incomplete/can't determine yet)
function _checkClue(board, r, c) {
  const clue = _GRID[r][c];
  if (!clue) return true;

  const ring = _getRing(r, c);
  const validRing = ring.filter(([,,v]) => v);

  // Check if all ring cells are decided
  let allDecided = true;
  for (const [nr, nc, valid] of ring) {
    if (valid && board[nr][nc] === -1) { allDecided = false; break; }
  }

  if (!allDecided) return null;

  // Count consecutive shaded groups in the ring
  const groups = [];
  let currentGroup = 0;
  const n = ring.length;

  // Find first unshaded or out-of-bounds to start
  let startIdx = -1;
  for (let i = 0; i < n; i++) {
    const [nr, nc, valid] = ring[i];
    if (!valid || board[nr][nc] !== 1) { startIdx = i; break; }
  }

  if (startIdx === -1) {
    // All cells in ring are shaded
    groups.push(validRing.length);
  } else {
    currentGroup = 0;
    for (let offset = 0; offset < n; offset++) {
      const idx = (startIdx + offset) % n;
      const [nr, nc, valid] = ring[idx];
      if (valid && board[nr][nc] === 1) {
        currentGroup++;
      } else {
        if (currentGroup > 0) { groups.push(currentGroup); currentGroup = 0; }
      }
    }
    if (currentGroup > 0) groups.push(currentGroup);
  }

  // Sort both and compare
  const sortedGroups = [...groups].sort((a, b) => a - b);
  const sortedClue = [...clue].sort((a, b) => a - b);

  if (sortedGroups.length !== sortedClue.length) return false;
  for (let i = 0; i < sortedGroups.length; i++) {
    if (sortedGroups[i] !== sortedClue[i]) return false;
  }
  return true;
}

// No 2x2 fully shaded
function _checkNo2x2Shaded(board) {
  const errors = [];
  for (let r = 0; r < _ROWS - 1; r++) {
    for (let c = 0; c < _COLS - 1; c++) {
      if (board[r][c] === 1 && board[r][c+1] === 1 &&
          board[r+1][c] === 1 && board[r+1][c+1] === 1) {
        errors.push({row: r, col: c, message: `2x2 shaded block at (${r+1},${c+1})`});
      }
    }
  }
  return errors;
}

// Shaded cells must be connected
function _checkShadedConnected(board) {
  let firstShaded = null, totalShaded = 0;
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      if (board[r][c] === 1) { totalShaded++; if (!firstShaded) firstShaded = [r,c]; }

  if (totalShaded <= 1) return [];

  const visited = new Set();
  const queue = [firstShaded];
  visited.add(`${firstShaded[0]},${firstShaded[1]}`);
  while (queue.length > 0) {
    const [r, c] = queue.shift();
    for (const [dr, dc] of _DIRS4) {
      const nr = r + dr, nc = c + dc;
      const key = `${nr},${nc}`;
      if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && board[nr][nc] === 1 && !visited.has(key)) {
        visited.add(key);
        queue.push([nr, nc]);
      }
    }
  }
  if (visited.size === totalShaded) return [];
  return [{row: firstShaded[0], col: firstShaded[1], message: 'Shaded cells are not all connected'}];
}

// Column majority: each column must have more shaded than unshaded
function _checkColumnMajority(board) {
  const errors = [];
  for (let c = 0; c < _COLS; c++) {
    let shaded = 0, unshaded = 0;
    for (let r = 0; r < _ROWS; r++) {
      if (_GRID[r][c] !== null) continue;
      if (board[r][c] === 1) shaded++;
      else unshaded++;
    }
    if (shaded <= unshaded && shaded + unshaded > 0) {
      errors.push({row: 0, col: c, message: `Column ${c+1}: shaded (${shaded}) must exceed unshaded (${unshaded})`});
    }
  }
  return errors;
}

// Check all clues
function _checkAllClues(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (_GRID[r][c] === null) continue;
      const result = _checkClue(board, r, c);
      if (result === false) {
        errors.push({row: r, col: c, message: `Clue at (${r+1},${c+1}) not satisfied`});
      }
    }
  }
  return errors;
}

function _getAllErrors(board) {
  // Convert -1 (undecided) to 0 for checking purposes
  const checkBoard = board.map(row => row.map(v => v === -1 ? 0 : v));
  const errors = [];
  errors.push(..._checkAllClues(checkBoard));
  errors.push(..._checkNo2x2Shaded(checkBoard));
  errors.push(..._checkShadedConnected(checkBoard));
  errors.push(..._checkColumnMajority(checkBoard));
  const seen = new Set();
  return errors.filter(e => {
    const key = `${e.row},${e.col}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function _hasShading(board) {
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      if (board[r][c] === 1) return true;
  return false;
}

function _boardIsSolved(board) {
  if (!_hasShading(board)) return false;
  // Check no undecided cells remain (except clue cells)
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      if (_GRID[r][c] === null && board[r][c] === -1) return false;
  return _getAllErrors(board).length === 0;
}

function init_game(meta) {
  const difficulty = meta.difficulty || 'medium';
  const data = _GRIDS[difficulty] || _GRIDS.medium;
  _ROWS = data.rows;
  _COLS = data.cols;
  _GRID = data.grid.map(row => [...row]);
  _history = [];

  const board = [], labels = [], given_mask = [];
  for (let r = 0; r < _ROWS; r++) {
    const br = [], lr = [], gr = [];
    for (let c = 0; c < _COLS; c++) {
      if (_GRID[r][c] !== null) {
        br.push(0);
        lr.push(_GRID[r][c].join(','));
        gr.push(true);
      } else {
        br.push(0);
        lr.push(null);
        gr.push(false);
      }
    }
    board.push(br);
    labels.push(lr);
    given_mask.push(gr);
  }
  return { board, labels, given_mask, status: 'ready' };
}

function make_move(state, row, col, value) {
  if (_GRID[row][col] !== null) {
    return { state, valid: false, conflicts: [], message: "Can't shade a clue cell", complete: false };
  }

  _history.push({ row, col, prev: state.board[row][col] });
  state.board[row][col] = state.board[row][col] === 1 ? 0 : 1;

  const conflicts = [];
  if (state.board[row][col] === 1) {
    for (let dr = 0; dr >= -1; dr--) {
      for (let dc = 0; dc >= -1; dc--) {
        const tr = row + dr, tc = col + dc;
        if (tr >= 0 && tr < _ROWS - 1 && tc >= 0 && tc < _COLS - 1) {
          if (state.board[tr][tc] === 1 && state.board[tr][tc+1] === 1 &&
              state.board[tr+1][tc] === 1 && state.board[tr+1][tc+1] === 1) {
            conflicts.push({row: tr, col: tc});
          }
        }
      }
    }
  }

  const complete = _boardIsSolved(state.board);
  const message = conflicts.length > 0 ? '2x2 shaded block!' :
                  complete ? 'Puzzle solved!' : '';
  return { state, valid: true, conflicts, message, complete };
}

function undo_move(state) {
  if (_history.length === 0) return state;
  const last = _history.pop();
  state.board[last.row][last.col] = last.prev;
  return state;
}

function check_solution(state) {
  const errors = _getAllErrors(state.board);
  if (errors.length === 0 && _hasShading(state.board)) {
    return { solved: true, errors: [], message: 'Congratulations! Puzzle solved!' };
  }
  return { solved: false, errors, message: `${errors.length} issue(s) found.` };
}

function get_hint(state, row, col) {
  // Find clue cells where the remaining ring cells are forced
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (_GRID[r][c] === null) continue;
      const clue = _GRID[r][c];
      const totalNeeded = clue.reduce((a, b) => a + b, 0);
      const ring = _getRing(r, c).filter(([,,v]) => v);
      let placed = 0, empty = [];
      for (const [nr, nc] of ring) {
        if (state.board[nr][nc] === 1) placed++;
        else if (_GRID[nr][nc] === null && state.board[nr][nc] !== 1) empty.push([nr, nc]);
      }
      if (placed < totalNeeded && totalNeeded - placed === empty.length && empty.length > 0) {
        const [hr, hc] = empty[0];
        return { value: 1, message: `Clue at (${r+1},${c+1}) forces shading at (${hr+1},${hc+1})` };
      }
    }
  }
  return { value: null, message: 'No obvious hint available.' };
}
