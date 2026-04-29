// Light Up (Akari) - Rule-based game logic
// Place bulbs on empty cells to illuminate the entire grid.

const _GRIDS = {
  easy: {
    rows: 4, cols: 4,
    // -1=empty, -2=black wall (unnumbered), 0-4=numbered wall
    grid: [
      [-1, -1, -1, -1],
      [-1, -1, -1,  2],
      [-1, -1, -1,  0],
      [-1, -1, -1, -1]
    ]
  },
  medium: {
    rows: 5, cols: 5,
    grid: [
      [-1, -1, -1, -1, -1],
      [-1, -1, -1,  2, -1],
      [-1, -1, -1, -1, -1],
      [-1, -1, -1,  2, -1],
      [-1, -1, -1, -1, -1]
    ]
  },
  hard: {
    rows: 6, cols: 6,
    grid: [
      [-1, -1, -1,  0, -1, -1],
      [-1, -1, -1, -1, -1, -1],
      [-1, -1,  0, -1,  1, -1],
      [-1, -1, -1, -1, -1, -1],
      [-1, -1, -1, -1, -1, -1],
      [-1, -1, -1, -1, -1, -1]
    ]
  }
};

let _ROWS = 0, _COLS = 0, _GRID = null, _history = [];

// Get cells illuminated by a bulb at (r,c) - orthogonal rays until wall/edge
function _rayCells(r, c) {
  const cells = [];
  const dirs = [[-1,0],[1,0],[0,-1],[0,1]];
  for (const [dr, dc] of dirs) {
    let nr = r + dr, nc = c + dc;
    while (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && _GRID[nr][nc] === -1) {
      cells.push([nr, nc]);
      nr += dr;
      nc += dc;
    }
  }
  return cells;
}

// Get all cells lit by current bulb placement
function _getLitCells(board) {
  const lit = new Set();
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] === 1) {
        lit.add(`${r},${c}`);
        for (const [nr, nc] of _rayCells(r, c)) {
          lit.add(`${nr},${nc}`);
        }
      }
    }
  }
  return lit;
}

// Check: no two bulbs see each other
function _checkNoConflictingBulbs(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (board[r][c] !== 1) continue;
      // Check rays for other bulbs
      const dirs = [[-1,0],[1,0],[0,-1],[0,1]];
      for (const [dr, dc] of dirs) {
        let nr = r + dr, nc = c + dc;
        while (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && _GRID[nr][nc] === -1) {
          if (board[nr][nc] === 1) {
            errors.push({row: r, col: c, message: `Bulb at (${r+1},${c+1}) sees another bulb`});
            break;
          }
          nr += dr;
          nc += dc;
        }
      }
    }
  }
  return errors;
}

// Check: numbered walls have exactly N adjacent bulbs
function _checkNumberedWalls(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (_GRID[r][c] < 0) continue; // not a numbered wall
      const num = _GRID[r][c];
      let count = 0;
      const dirs = [[-1,0],[1,0],[0,-1],[0,1]];
      for (const [dr, dc] of dirs) {
        const nr = r + dr, nc = c + dc;
        if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && board[nr][nc] === 1) {
          count++;
        }
      }
      if (count > num) {
        errors.push({row: r, col: c, message: `Wall (${r+1},${c+1}) has too many bulbs (${count}/${num})`});
      }
    }
  }
  return errors;
}

// Check: numbered walls satisfied exactly (for solution check)
function _checkNumberedWallsExact(board) {
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (_GRID[r][c] < 0) continue;
      const num = _GRID[r][c];
      let count = 0;
      const dirs = [[-1,0],[1,0],[0,-1],[0,1]];
      for (const [dr, dc] of dirs) {
        const nr = r + dr, nc = c + dc;
        if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && board[nr][nc] === 1) {
          count++;
        }
      }
      if (count !== num) {
        errors.push({row: r, col: c, message: `Wall (${r+1},${c+1}) needs exactly ${num} bulbs, has ${count}`});
      }
    }
  }
  return errors;
}

// Check: all empty cells are illuminated
function _checkAllLit(board) {
  const lit = _getLitCells(board);
  const errors = [];
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (_GRID[r][c] === -1 && board[r][c] !== 1 && !lit.has(`${r},${c}`)) {
        errors.push({row: r, col: c, message: `Cell (${r+1},${c+1}) is not illuminated`});
      }
    }
  }
  return errors;
}

function _getAllErrors(board) {
  const errors = [];
  errors.push(..._checkNoConflictingBulbs(board));
  errors.push(..._checkNumberedWallsExact(board));
  errors.push(..._checkAllLit(board));
  // Deduplicate by row,col
  const seen = new Set();
  return errors.filter(e => {
    const key = `${e.row},${e.col}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function _hasBulbs(board) {
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      if (board[r][c] === 1) return true;
  return false;
}

function _boardIsSolved(board) {
  return _hasBulbs(board) && _getAllErrors(board).length === 0;
}

function init_game(meta) {
  const difficulty = meta.difficulty || 'medium';
  const data = _GRIDS[difficulty] || _GRIDS.medium;
  _ROWS = data.rows;
  _COLS = data.cols;
  _GRID = data.grid.map(row => [...row]);
  _history = [];

  const board = [];
  const labels = [];
  const given_mask = [];
  for (let r = 0; r < _ROWS; r++) {
    board.push(new Array(_COLS).fill(0));
    const labelRow = [];
    const givenRow = [];
    for (let c = 0; c < _COLS; c++) {
      if (_GRID[r][c] === -2) {
        labelRow.push('■'); // black wall
        givenRow.push(true);
      } else if (_GRID[r][c] >= 0) {
        labelRow.push(String(_GRID[r][c])); // numbered wall
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
  // Can't place on walls
  if (_GRID[row][col] !== -1) {
    return { state, valid: false, conflicts: [], message: "Can't place on a wall", complete: false };
  }

  _history.push({ row, col, prev: state.board[row][col] });
  // Toggle bulb
  state.board[row][col] = state.board[row][col] === 1 ? 0 : 1;

  // Quick conflict check: does this bulb see another?
  const conflicts = [];
  if (state.board[row][col] === 1) {
    const dirs = [[-1,0],[1,0],[0,-1],[0,1]];
    for (const [dr, dc] of dirs) {
      let nr = row + dr, nc = col + dc;
      while (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && _GRID[nr][nc] === -1) {
        if (state.board[nr][nc] === 1) {
          conflicts.push({row: nr, col: nc});
        }
        nr += dr;
        nc += dc;
      }
    }
    // Check adjacent numbered walls
    for (const [dr, dc] of dirs) {
      const nr = row + dr, nc = col + dc;
      if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && _GRID[nr][nc] >= 0) {
        const num = _GRID[nr][nc];
        let count = 0;
        for (const [dr2, dc2] of dirs) {
          const nnr = nr + dr2, nnc = nc + dc2;
          if (nnr >= 0 && nnr < _ROWS && nnc >= 0 && nnc < _COLS && state.board[nnr][nnc] === 1) count++;
        }
        if (count > num) conflicts.push({row: nr, col: nc});
      }
    }
  }

  const complete = _boardIsSolved(state.board);
  const message = conflicts.length > 0 ? 'Conflict detected!' :
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
  if (errors.length === 0 && _hasBulbs(state.board)) {
    return { solved: true, errors: [], message: 'Congratulations! Puzzle solved!' };
  }
  return { solved: false, errors, message: `${errors.length} issue(s) found.` };
}

function get_hint(state, row, col) {
  // Find a numbered wall that has only one possible remaining bulb placement
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      if (_GRID[r][c] < 0) continue;
      const num = _GRID[r][c];
      const dirs = [[-1,0],[1,0],[0,-1],[0,1]];
      let placed = 0;
      const available = [];
      for (const [dr, dc] of dirs) {
        const nr = r + dr, nc = c + dc;
        if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS && _GRID[nr][nc] === -1) {
          if (state.board[nr][nc] === 1) placed++;
          else available.push([nr, nc]);
        }
      }
      const needed = num - placed;
      if (needed > 0 && needed === available.length) {
        // All remaining positions must have bulbs
        const [hr, hc] = available[0];
        return { value: 1, message: `Wall at (${r+1},${c+1}) forces a bulb at (${hr+1},${hc+1})` };
      }
    }
  }
  return { value: null, message: 'No obvious hint available.' };
}
