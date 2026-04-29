// Nurikabe - Rule-based game logic
// Shade cells to create a "sea" of connected shaded cells.

const _GRIDS = {
  easy: {
    rows: 4, cols: 4,
    // >0 = island size clue, -1 = empty
    grid: [
      [ 2, -1,  2, -1],
      [-1, -1, -1, -1],
      [-1,  2, -1,  2],
      [-1, -1, -1, -1]
    ]
  },
  medium: {
    rows: 6, cols: 6,
    grid: [
      [ 2, -1,  2, -1,  2, -1],
      [-1, -1, -1, -1, -1, -1],
      [-1,  2, -1,  2, -1,  2],
      [-1, -1, -1, -1, -1, -1],
      [ 2, -1,  2, -1,  2, -1],
      [-1, -1, -1, -1, -1, -1]
    ]
  },
  hard: {
    rows: 8, cols: 8,
    grid: [
      [ 2, -1,  2, -1,  2, -1,  2, -1],
      [-1, -1, -1, -1, -1, -1, -1, -1],
      [-1,  2, -1,  2, -1,  2, -1,  2],
      [-1, -1, -1, -1, -1, -1, -1, -1],
      [ 2, -1,  2, -1,  2, -1,  2, -1],
      [-1, -1, -1, -1, -1, -1, -1, -1],
      [-1,  2, -1,  2, -1,  2, -1,  2],
      [-1, -1, -1, -1, -1, -1, -1, -1]
    ]
  }
};

let _ROWS = 0, _COLS = 0, _GRID = null, _history = [];
const _DIRS = [[-1,0],[1,0],[0,-1],[0,1]];

function _floodFill(board, startR, startC, targetVal) {
  const visited = new Set();
  const queue = [[startR, startC]];
  visited.add(`${startR},${startC}`);
  while (queue.length > 0) {
    const [r, c] = queue.shift();
    for (const [dr, dc] of _DIRS) {
      const nr = r + dr, nc = c + dc;
      const key = `${nr},${nc}`;
      if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && !visited.has(key) && board[nr][nc] === targetVal) {
        visited.add(key);
        queue.push([nr, nc]);
      }
    }
  }
  return visited;
}

// Each island (connected unshaded region) must contain exactly one clue and match its size
function _checkIslands(board) {
  const errors = [];
  const visited = new Set();
  const cluePositions = new Set();
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      if (_GRID[r][c] > 0) cluePositions.add(`${r},${c}`);

  const usedClues = new Set();

  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] === 1 || visited.has(`${r},${c}`)) continue;
      const island = _floodFill(board, r, c, 0);
      for (const key of island) visited.add(key);

      let clueCount = 0, clueVal = 0, clueR = -1, clueC = -1;
      for (const key of island) {
        if (cluePositions.has(key)) {
          clueCount++;
          const [cr, cc] = key.split(',').map(Number);
          clueVal = _GRID[cr][cc];
          clueR = cr; clueC = cc;
          usedClues.add(key);
        }
      }

      if (clueCount === 0) {
        const [fr, fc] = [...island][0].split(',').map(Number);
        errors.push({row: fr, col: fc, message: 'Unshaded region has no island clue'});
      } else if (clueCount > 1) {
        errors.push({row: clueR, col: clueC, message: 'Two island clues in the same region'});
      } else if (island.size !== clueVal) {
        errors.push({row: clueR, col: clueC, message: `Island size ${island.size}, expected ${clueVal}`});
      }
    }
  }
  return errors;
}

// No 2x2 shaded square
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

// All shaded cells must be connected
function _checkShadedConnected(board) {
  let firstShaded = null;
  let totalShaded = 0;
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] === 1) {
        totalShaded++;
        if (!firstShaded) firstShaded = [r, c];
      }
    }
  }
  if (totalShaded <= 1) return [];
  const connected = _floodFill(board, firstShaded[0], firstShaded[1], 1);
  if (connected.size === totalShaded) return [];
  return [{row: firstShaded[0], col: firstShaded[1], message: 'Shaded cells are not all connected'}];
}

function _getAllErrors(board) {
  const errors = [];
  errors.push(..._checkIslands(board));
  errors.push(..._checkNo2x2Shaded(board));
  errors.push(..._checkShadedConnected(board));
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
  return _hasShading(board) && _getAllErrors(board).length === 0;
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
    board.push(new Array(_COLS).fill(0));
    const lr = [], gr = [];
    for (let c = 0; c < _COLS; c++) {
      if (_GRID[r][c] > 0) {
        lr.push(String(_GRID[r][c]));
        gr.push(true);
      } else {
        lr.push(null);
        gr.push(false);
      }
    }
    labels.push(lr);
    given_mask.push(gr);
  }
  return { board, labels, given_mask, status: 'ready' };
}

function make_move(state, row, col, value) {
  // Can't shade clue cells
  if (_GRID[row][col] > 0) {
    return { state, valid: false, conflicts: [], message: "Can't shade a clue cell", complete: false };
  }

  _history.push({ row, col, prev: state.board[row][col] });
  state.board[row][col] = state.board[row][col] === 1 ? 0 : 1;

  const conflicts = [];
  if (state.board[row][col] === 1) {
    // Quick 2x2 check
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
  // Find cells that must be shaded: between two different islands
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (_GRID[r][c] > 0 || state.board[r][c] === 1) continue;
      // Check if cell is adjacent to two different clue cells
      const adjClues = new Set();
      for (const [dr, dc] of _DIRS) {
        const nr = r + dr, nc = c + dc;
        if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && _GRID[nr][nc] > 0) {
          adjClues.add(`${nr},${nc}`);
        }
      }
      if (adjClues.size >= 2) {
        return { value: 1, message: `Cell (${r+1},${c+1}) is between two islands and must be shaded` };
      }
    }
  }
  return { value: null, message: 'No obvious hint available.' };
}
