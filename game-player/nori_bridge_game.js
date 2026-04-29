const _GRIDS = {
  easy: {
    rows: 6, cols: 6,
    room_grid: [
      [0, 0, 1, 1, 2, 2],
      [0, 0, 1, 1, 2, 2],
      [3, 3, 4, 4, 5, 5],
      [3, 3, 4, 4, 5, 5],
      [3, 3, 4, 4, 5, 5],
      [3, 3, 4, 4, 5, 5],
    ],
    region_numbers: { 0: 2, 1: 3, 2: 2, 3: 1, 4: 1, 5: 1 },
  },
  medium: {
    rows: 8, cols: 8,
    room_grid: [
      [0, 0, 1, 1, 2, 2, 3, 3],
      [0, 0, 1, 1, 2, 2, 3, 3],
      [0, 0, 1, 1, 2, 2, 3, 3],
      [0, 0, 1, 1, 2, 2, 3, 3],
      [4, 4, 5, 5, 6, 6, 7, 7],
      [4, 4, 5, 5, 6, 6, 7, 7],
      [4, 4, 5, 5, 6, 6, 7, 7],
      [4, 4, 5, 5, 6, 6, 7, 7],
    ],
    region_numbers: { 0: null, 1: 3, 2: 3, 3: null, 4: 1, 5: 1, 6: 1, 7: 1 },
  },
  hard: {
    rows: 10, cols: 10,
    room_grid: [
      [0, 0, 1, 1, 2, 2, 3, 3, 3, 3],
      [0, 0, 1, 1, 2, 2, 3, 3, 3, 3],
      [4, 4, 5, 5, 6, 6, 7, 7, 7, 7],
      [4, 4, 5, 5, 6, 6, 7, 7, 7, 7],
      [8, 8, 9, 9, 10, 10, 11, 11, 11, 11],
      [8, 8, 9, 9, 10, 10, 11, 11, 11, 11],
      [12, 12, 13, 13, 14, 14, 15, 15, 15, 15],
      [12, 12, 13, 13, 14, 14, 15, 15, 15, 15],
      [12, 12, 13, 13, 14, 14, 15, 15, 15, 15],
      [12, 12, 13, 13, 14, 14, 15, 15, 15, 15],
    ],
    region_numbers: {
      0: 2, 1: 3, 2: 3, 3: 2,
      4: 2, 5: 2, 6: 2, 7: 2,
      8: 2, 9: 2, 10: 2, 11: 2,
      12: 1, 13: 1, 14: 1, 15: 1,
    },
  },
};

let _ROWS = 0, _COLS = 0, _roomGrid = null, _regionNumbers = null;
let _history = [];
let _bridges = new Set();

function _findBorderCells() {
  const borders = [];
  for (let r = 0; r < _ROWS; r++) {
    for (let c = 0; c < _COLS; c++) {
      let isBorder = false;
      for (const [dr, dc] of [[0,1],[0,-1],[1,0],[-1,0]]) {
        const nr = r + dr, nc = c + dc;
        if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS) {
          if (_roomGrid[nr][nc] !== _roomGrid[r][c]) {
            isBorder = true;
            break;
          }
        }
      }
      if (isBorder) borders.push([r, c]);
    }
  }
  return borders;
}

function _getPairForCell(r, c) {
  const myRoom = _roomGrid[r][c];
  const neighbors = new Set();
  for (const [dr, dc] of [[0,1],[0,-1],[1,0],[-1,0]]) {
    const nr = r + dr, nc = c + dc;
    if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS) {
      const adjRoom = _roomGrid[nr][nc];
      if (adjRoom !== myRoom) neighbors.add(adjRoom);
    }
  }
  if (neighbors.size === 1) {
    const adj = [...neighbors][0];
    return `${Math.min(myRoom, adj)},${Math.max(myRoom, adj)}`;
  }
  return null;
}

function _isBorderCell(r, c) {
  for (const [dr, dc] of [[0,1],[0,-1],[1,0],[-1,0]]) {
    const nr = r + dr, nc = c + dc;
    if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS) {
      if (_roomGrid[nr][nc] !== _roomGrid[r][c]) return true;
    }
  }
  return false;
}

function _buildBoardFromBridges() {
  const board = [];
  for (let r = 0; r < _ROWS; r++) board.push(new Array(_COLS).fill(0));
  for (const pairKey of _bridges) {
    for (let r = 0; r < _ROWS; r++) {
      for (let c = 0; c < _COLS; c++) {
        if (_isBorderCell(r, c) && _getPairForCell(r, c) === pairKey) {
          board[r][c] = 1;
        }
      }
    }
  }
  return board;
}

function _getRegionDegree(regionId) {
  let count = 0;
  for (const pairKey of _bridges) {
    const [a, b] = pairKey.split(',').map(Number);
    if (a === regionId || b === regionId) count++;
  }
  return count;
}

function _checkDegreeConstraints() {
  const errors = [];
  for (const [regStr, expected] of Object.entries(_regionNumbers)) {
    if (expected === null) continue;
    const reg = parseInt(regStr);
    const actual = _getRegionDegree(reg);
    if (actual > expected) {
      for (let r = 0; r < _ROWS; r++)
        for (let c = 0; c < _COLS; c++)
          if (_roomGrid[r][c] === reg) {
            errors.push({ row: r, col: c, message: `Region ${reg}: has ${actual} bridges, needs ${expected}` });
            break;
          }
    }
  }
  return errors;
}

function _checkDegreeExact() {
  const errors = [];
  for (const [regStr, expected] of Object.entries(_regionNumbers)) {
    if (expected === null) continue;
    const reg = parseInt(regStr);
    const actual = _getRegionDegree(reg);
    if (actual !== expected) {
      for (let r = 0; r < _ROWS; r++)
        for (let c = 0; c < _COLS; c++)
          if (_roomGrid[r][c] === reg) {
            errors.push({ row: r, col: c, message: `Region ${reg}: has ${actual} bridge(s), needs ${expected}` });
            break;
          }
    }
  }
  return errors;
}

function _checkConnected() {
  const allRegions = new Set();
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++)
      allRegions.add(_roomGrid[r][c]);

  if (_bridges.size === 0) return [];

  const adj = {};
  for (const reg of allRegions) adj[reg] = new Set();
  for (const pairKey of _bridges) {
    const [a, b] = pairKey.split(',').map(Number);
    adj[a].add(b);
    adj[b].add(a);
  }

  const start = [...allRegions][0];
  const visited = new Set();
  const queue = [start];
  visited.add(start);
  while (queue.length) {
    const node = queue.shift();
    for (const nb of adj[node]) {
      if (!visited.has(nb)) {
        visited.add(nb);
        queue.push(nb);
      }
    }
  }

  if (visited.size !== allRegions.size) {
    return [{ row: 0, col: 0, message: 'Not all regions connected by bridges' }];
  }
  return [];
}

function _getAllErrors() {
  const board = _buildBoardFromBridges();
  const allErrs = [
    ..._checkDegreeExact(),
    ..._checkConnected(),
  ];
  const seen = new Set();
  return allErrs.filter(e => {
    const k = `${e.row},${e.col}`;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });
}

function init_game(meta) {
  const diff = (meta && meta.difficulty) || 'easy';
  const g = _GRIDS[diff] || _GRIDS.easy;
  _ROWS = g.rows;
  _COLS = g.cols;
  _roomGrid = g.room_grid;
  _regionNumbers = g.region_numbers;
  _bridges = new Set();
  _history = [];

  const board = [];
  const labels = [];
  const given_mask = [];

  const regionCenters = {};
  for (let r = 0; r < _ROWS; r++)
    for (let c = 0; c < _COLS; c++) {
      const room = _roomGrid[r][c];
      if (!regionCenters[room]) regionCenters[room] = [r, c];
    }

  for (let r = 0; r < _ROWS; r++) {
    board.push(new Array(_COLS).fill(0));
    const labelRow = [];
    const givenRow = [];
    for (let c = 0; c < _COLS; c++) {
      const room = _roomGrid[r][c];
      const center = regionCenters[room];
      if (center[0] === r && center[1] === c && _regionNumbers[room] !== null && _regionNumbers[room] !== undefined) {
        labelRow.push(_regionNumbers[room]);
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
  if (!_isBorderCell(row, col)) {
    return { state, valid: true, conflicts: [], message: 'Not a border cell', complete: false };
  }

  const pairKey = _getPairForCell(row, col);
  if (!pairKey) {
    return { state, valid: true, conflicts: [], message: 'Ambiguous border cell', complete: false };
  }

  const wasBridged = _bridges.has(pairKey);
  _history.push({ pairKey, wasBridged });

  if (wasBridged) {
    _bridges.delete(pairKey);
  } else {
    _bridges.add(pairKey);
  }

  state.board = _buildBoardFromBridges();

  const conflicts = [];
  if (!wasBridged) {
    const [a, b] = pairKey.split(',').map(Number);
    for (const reg of [a, b]) {
      const expected = _regionNumbers[reg];
      if (expected !== null && expected !== undefined) {
        const actual = _getRegionDegree(reg);
        if (actual > expected) {
          for (let r = 0; r < _ROWS; r++)
            for (let c = 0; c < _COLS; c++)
              if (_roomGrid[r][c] === reg) { conflicts.push({ row: r, col: c }); break; }
        }
      }
    }
  }

  const errs = _getAllErrors();
  const complete = _bridges.size > 0 && errs.length === 0;
  return {
    state, valid: true, conflicts,
    message: complete ? 'Puzzle solved!' : (conflicts.length ? 'Degree constraint exceeded' : ''),
    complete,
  };
}

function undo_move(state) {
  if (!_history.length) return state;
  const { pairKey, wasBridged } = _history.pop();
  if (wasBridged) _bridges.add(pairKey);
  else _bridges.delete(pairKey);
  state.board = _buildBoardFromBridges();
  return state;
}

function check_solution(state) {
  const errors = _getAllErrors();
  if (errors.length === 0 && _bridges.size > 0) {
    return { solved: true, errors: [], message: 'Congratulations! Puzzle solved!' };
  }
  return {
    solved: false, errors,
    message: errors.length ? `${errors.length} rule violation(s) found.` : 'Place more bridges.',
  };
}

function get_hint(state, row, col) {
  for (const [regStr, expected] of Object.entries(_regionNumbers)) {
    if (expected === null) continue;
    const reg = parseInt(regStr);
    const actual = _getRegionDegree(reg);
    if (actual < expected) {
      const adjacentRegs = new Set();
      for (let r = 0; r < _ROWS; r++)
        for (let c = 0; c < _COLS; c++)
          if (_roomGrid[r][c] === reg) {
            for (const [dr, dc] of [[0,1],[0,-1],[1,0],[-1,0]]) {
              const nr = r + dr, nc = c + dc;
              if (nr >= 0 && nr < _ROWS && nc >= 0 && nc < _COLS) {
                const adj = _roomGrid[nr][nc];
                if (adj !== reg) {
                  const key = `${Math.min(reg, adj)},${Math.max(reg, adj)}`;
                  if (!_bridges.has(key)) adjacentRegs.add(key);
                }
              }
            }
          }
      const remaining = expected - actual;
      if (adjacentRegs.size === remaining) {
        return { value: 1, message: `Region ${reg} needs ${remaining} more bridge(s) and has exactly ${adjacentRegs.size} possible. All must be bridges.` };
      }
    }
  }
  return { value: null, message: 'No obvious hint available.' };
}
