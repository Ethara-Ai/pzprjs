//
// パズル固有スクリプト部 数独版 sudoku.js
//

/* ---- shared helpers ---- */
function sudoku_rejectInput(cell, prevNum) {
	cell.setNum(prevNum);
	cell.draw();
	cell.seterr(1);
	cell.draw();
	setTimeout(function() {
		cell.seterr(0);
		cell.draw();
	}, 600);
}

/* ---- sudoku1 helpers ---- */
function sudoku_canPlace(bd, cell, digit) {
	var bx = cell.bx, by = cell.by;
	var cols = bd.cols, rows = bd.rows;

	for (var c = 0; c < cols; c++) {
		var cx = 2 * c + 1;
		if (cx === bx) { continue; }
		var rc = bd.getc(cx, by);
		if (!rc.isnull && (rc.getNum() === digit || rc.qnum === digit)) { return false; }
	}

	for (var r = 0; r < rows; r++) {
		var cy = 2 * r + 1;
		if (cy === by) { continue; }
		var rc2 = bd.getc(bx, cy);
		if (!rc2.isnull && (rc2.getNum() === digit || rc2.qnum === digit)) { return false; }
	}

	/* 3x3 box uniqueness */
	var boxSize = (Math.sqrt(cols) | 0);
	var col0 = (((bx - 1) / 2) | 0);
	var row0 = (((by - 1) / 2) | 0);
	var br = Math.floor(row0 / boxSize) * boxSize;
	var bc = Math.floor(col0 / boxSize) * boxSize;
	for (var rr = br; rr < br + boxSize; rr++) {
		for (var cc = bc; cc < bc + boxSize; cc++) {
			var bbx = 2 * cc + 1, bby = 2 * rr + 1;
			if (bbx === bx && bby === by) { continue; }
			var rc3 = bd.getc(bbx, bby);
			if (!rc3.isnull && (rc3.getNum() === digit || rc3.qnum === digit)) { return false; }
		}
	}
	return true;
}

function sudoku_onlyMatchingParityRemains(puzzle) {
	var bd = puzzle.board;
	var lastOdd = puzzle._lastDigitOdd;
	for (var i = 0; i < bd.cell.length; i++) {
		var cell = bd.cell[i];
		if (cell.qnum > 0) { continue; }
		if (cell.getNum() > 0) { continue; }
		for (var d = 1; d <= 9; d++) {
			var dOdd = (d % 2 === 1);
			if (dOdd === lastOdd) { continue; }
			if (sudoku_canPlace(bd, cell, d)) { return false; }
		}
	}
	return true;
}

function sudoku_isDigitParityAllowed(puzzle, newNum) {
	if (typeof puzzle._lastDigitOdd === "undefined") { return true; }
	var newIsOdd = (newNum % 2 === 1);
	if (newIsOdd !== puzzle._lastDigitOdd) { return true; }
	return sudoku_onlyMatchingParityRemains(puzzle);
}

function sudoku_hashClues(bd) {
	var h = 0;
	for (var i = 0; i < bd.cell.length; i++) {
		var q = bd.cell[i].qnum;
		if (q > 0) { h = (h * 31 + q + i) | 0; }
	}
	return Math.abs(h);
}

function sudoku_getKillerCage(bd) {
	if (bd._killerCage) { return bd._killerCage; }

	var h = sudoku_hashClues(bd);
	var boxIndex = h % 9;
	var boxRow = Math.floor(boxIndex / 3);
	var boxCol = boxIndex % 3;

	var startRow = boxRow * 3;
	var startCol = boxCol * 3;

	var cells = [];
	for (var r = startRow; r < startRow + 3; r++) {
		for (var c = startCol; c < startCol + 3; c++) {
			var bx = 2 * c + 1;
			var by = 2 * r + 1;
			cells.push({ bx: bx, by: by, row: r, col: c });
		}
	}

	bd._killerCage = {
		startRow: startRow,
		startCol: startCol,
		targetSum: 45,
		cells: cells
	};
	return bd._killerCage;
}

/* ---- sudoku2 helpers ---- */
function sudoku2_getCellRow(cell) {
	return ((cell.by - 1) / 2) | 0;
}

function sudoku2_getCellBox(cell) {
	var col = ((cell.bx - 1) / 2) | 0;
	var row = ((cell.by - 1) / 2) | 0;
	return Math.floor(row / 3) * 3 + Math.floor(col / 3);
}

function sudoku2_onlyMatchingRowRemains(puzzle) {
	var bd = puzzle.board;
	var lastRow = puzzle._lastEnteredRow;
	for (var i = 0; i < bd.cell.length; i++) {
		var cell = bd.cell[i];
		if (cell.qnum > 0) { continue; }
		if (cell.getNum() > 0) { continue; }
		var r = sudoku2_getCellRow(cell);
		if (r !== lastRow) { return false; }
	}
	return true;
}

function sudoku2_onlyMatchingBoxRemains(puzzle) {
	var bd = puzzle.board;
	var lastBox = puzzle._lastEnteredBox;
	for (var i = 0; i < bd.cell.length; i++) {
		var cell = bd.cell[i];
		if (cell.qnum > 0) { continue; }
		if (cell.getNum() > 0) { continue; }
		var b = sudoku2_getCellBox(cell);
		if (b !== lastBox) { return false; }
	}
	return true;
}

/* sudoku2 input check: row alternation + box alternation */
function sudoku2_checkInput(puzzle, cell, prevNum) {
	var newRow = sudoku2_getCellRow(cell);
	var newBox = sudoku2_getCellBox(cell);

	/* Rule 6: Row alternation */
	if (typeof puzzle._lastEnteredRow !== "undefined" && newRow === puzzle._lastEnteredRow) {
		if (!sudoku2_onlyMatchingRowRemains(puzzle)) {
			sudoku_rejectInput(cell, prevNum);
			return false;
		}
	}

	/* Rule 7: Box alternation */
	if (typeof puzzle._lastEnteredBox !== "undefined" && newBox === puzzle._lastEnteredBox) {
		if (!sudoku2_onlyMatchingBoxRemains(puzzle)) {
			sudoku_rejectInput(cell, prevNum);
			return false;
		}
	}

	puzzle._lastEnteredRow = newRow;
	puzzle._lastEnteredBox = newBox;
	return true;
}

/* sudoku2: get a hash-chosen diagonal (main or anti) */



(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["sudoku", "sudoku2"], {
	//---------------------------------------------------------
	// マウス入力系 (shared base)
	MouseEvent: {
		inputModes: { edit: ["number", "clear"], play: ["number", "clear"] },
		autoedit_func: "qnum",
		autoplay_func: "qnum"
	},

	/* sudoku1: same-digit rejection + digit parity alternation */
	"MouseEvent@sudoku": {
		inputqnum_main: function(cell) {
			var puzzle = this.puzzle;
			var prevNum = cell.getNum();

			this.common.inputqnum_main.call(this, cell);

			if (puzzle.playmode) {
				var newNum = cell.getNum();
				if (newNum > 0) {
					if (puzzle._lastEnteredNum === newNum) {
						sudoku_rejectInput(cell, prevNum);
						return;
					}
					if (!sudoku_isDigitParityAllowed(puzzle, newNum)) {
						sudoku_rejectInput(cell, prevNum);
						return;
					}
					puzzle._lastEnteredNum = newNum;
					puzzle._lastDigitOdd = (newNum % 2 === 1);
				}
			}
		}
	},

	/* sudoku2: row alternation + box alternation */
	"MouseEvent@sudoku2": {
		inputqnum_main: function(cell) {
			var puzzle = this.puzzle;
			var prevNum = cell.getNum();

			this.common.inputqnum_main.call(this, cell);

			if (puzzle.playmode) {
				var newNum = cell.getNum();
				if (newNum > 0) {
					if (!sudoku2_checkInput(puzzle, cell, prevNum)) {
						return;
					}
				}
			}
		}
	},

	//---------------------------------------------------------
	// キーボード入力系 (shared base)
	KeyEvent: {
		enablemake: true,
		enableplay: true
	},

	/* sudoku1: same-digit rejection + digit parity alternation */
	"KeyEvent@sudoku": {
		key_inputqnum_main: function(cell, ca) {
			var puzzle = this.puzzle;
			var prevNum = cell.getNum();

			this.common.key_inputqnum_main.call(this, cell, ca);

			if (puzzle.playmode) {
				var newNum = cell.getNum();
				if (newNum > 0) {
					if (puzzle._lastEnteredNum === newNum) {
						sudoku_rejectInput(cell, prevNum);
						return;
					}
					if (!sudoku_isDigitParityAllowed(puzzle, newNum)) {
						sudoku_rejectInput(cell, prevNum);
						return;
					}
					puzzle._lastEnteredNum = newNum;
					puzzle._lastDigitOdd = (newNum % 2 === 1);
				}
			}
		}
	},

	/* sudoku2: row alternation + box alternation */
	"KeyEvent@sudoku2": {
		key_inputqnum_main: function(cell, ca) {
			var puzzle = this.puzzle;
			var prevNum = cell.getNum();

			this.common.key_inputqnum_main.call(this, cell, ca);

			if (puzzle.playmode) {
				var newNum = cell.getNum();
				if (newNum > 0) {
					if (!sudoku2_checkInput(puzzle, cell, prevNum)) {
						return;
					}
				}
			}
		}
	},

	//---------------------------------------------------------
	// 盤面管理系
	Cell: {
		enableSubNumberArray: true,

		maxnum: function() {
			return Math.max(this.board.cols, this.board.rows);
		}
	},
	Board: {
		cols: 9,
		rows: 9,

		hasborder: 1,

		initBoardSize: function(col, row) {
			this.common.initBoardSize.call(this, col, row);

			var roomsizex, roomsizey;
			roomsizex = roomsizey = (Math.sqrt(this.cols) | 0) * 2;
			if (this.cols === 6) {
				roomsizex = 6;
			}
			for (var i = 0; i < this.border.length; i++) {
				var border = this.border[i];
				if (border.bx % roomsizex === 0 || border.by % roomsizey === 0) {
					border.ques = 1;
				}
			}
			this.rebuildInfo();

			this._killerCage = null;
		}
	},

	AreaRoomGraph: {
		enabled: true
	},

	//---------------------------------------------------------
	// 画像表示系 (shared base — minimal)
	Graphic: {
		paint: function() {
			this.drawBGCells();
			this.drawTargetSubNumber();
			this.drawGrid();
			this.drawBorders();

			this.drawSubNumbers();
			this.drawAnsNumbers();
			this.drawQuesNumbers();

			this.drawChassis();

			this.drawCursor();
		}
	},

	/* sudoku1: killer cage rendering */
	"Graphic@sudoku": {
		paint: function() {
			this.drawBGCells();
			this.drawTargetSubNumber();
			this.drawGrid();
			this.drawBorders();

			this.drawKillerCage();

			this.drawSubNumbers();
			this.drawAnsNumbers();
			this.drawQuesNumbers();

			this.drawKillerCageSum();

			this.drawChassis();

			this.drawCursor();
		},

		drawKillerCage: function() {
			var bd = this.board;
			var cage = sudoku_getKillerCage(bd);
			if (!cage) { return; }

			var g = this.vinc("killer_cage", "crispEdges", true);

			var bw = this.bw;
			var bh = this.bh;
			var tlbx = cage.cells[0].bx;
			var tlby = cage.cells[0].by;
			var brbx = cage.cells[8].bx;
			var brby = cage.cells[8].by;

			var inset = Math.max(bw * 0.12, 1);
			var px1 = (tlbx - 1) * bw + inset;
			var py1 = (tlby - 1) * bh + inset;
			var px2 = (brbx + 1) * bw - inset;
			var py2 = (brby + 1) * bh - inset;

			var lw = Math.max((this.cw / 16) | 0, 2);
			var dash = [Math.max(this.cw / 5, 3), Math.max(this.cw / 8, 2)];

			g.strokeStyle = "rgb(200, 60, 60)";
			g.lineWidth = lw;

			g.vid = "kcage_top";
			g.strokeDashedLine(px1, py1, px2, py1, dash);
			g.vid = "kcage_bot";
			g.strokeDashedLine(px1, py2, px2, py2, dash);
			g.vid = "kcage_lft";
			g.strokeDashedLine(px1, py1, px1, py2, dash);
			g.vid = "kcage_rgt";
			g.strokeDashedLine(px2, py1, px2, py2, dash);
		},

		drawKillerCageSum: function() {
			var bd = this.board;
			var cage = sudoku_getKillerCage(bd);
			if (!cage) { return; }

			var g = this.vinc("killer_sum", "auto");
			g.vid = "kcage_sum_text";

			var bw = this.bw;
			var bh = this.bh;
			var px = cage.cells[0].bx * bw;
			var py = cage.cells[0].by * bh;

			this.disptext("" + cage.targetSum, px, py, {
				position: 5,
				ratio: 0.3,
				color: "rgb(200, 60, 60)"
			});
		}
	},

	//---------------------------------------------------------
	// URLエンコード/デコード処理
	Encode: {
		decodePzpr: function(type) {
			this.decodeNumber16();
		},
		encodePzpr: function(type) {
			this.encodeNumber16();
		},

		decodeKanpen: function() {
			this.fio.decodeCellQnum_kanpen();
		},
		encodeKanpen: function() {
			this.fio.encodeCellQnum_kanpen();
		}
	},
	//---------------------------------------------------------
	FileIO: {
		decodeData: function() {
			this.decodeCellQnum();
			this.decodeCellAnumsub();
		},
		encodeData: function() {
			this.encodeCellQnum();
			this.encodeCellAnumsub();
		},

		kanpenOpen: function() {
			this.decodeCellQnum_kanpen();
			this.decodeCellAnum_kanpen();
		},
		kanpenSave: function() {
			this.encodeCellQnum_kanpen();
			this.encodeCellAnum_kanpen();
		},

		kanpenOpenXML: function() {
			this.decodeCellQnum_XMLBoard();
			this.decodeCellAnum_XMLAnswer();
		},
		kanpenSaveXML: function() {
			this.encodeCellQnum_XMLBoard();
			this.encodeCellAnum_XMLAnswer();
		},

		UNDECIDED_NUM_XML: 0
	},

	//---------------------------------------------------------
	// 正解判定処理実行部

	/* sudoku1: standard + killer cage */
	"AnsCheck@sudoku#1": {
		checklist: [
			"checkDifferentNumberInRoom",
			"checkDifferentNumberInLine",
			"checkKillerCageSum",
			"checkNoNumCell+"
		]
	},
	"AnsCheck@sudoku": {
		checkKillerCageSum: function() {
			var bd = this.board;
			var cage = sudoku_getKillerCage(bd);
			if (!cage) { return; }

			var sum = 0;
			var incomplete = false;
			var cellObjs = [];
			for (var i = 0; i < cage.cells.length; i++) {
				var ci = cage.cells[i];
				var cell = bd.getc(ci.bx, ci.by);
				if (cell.isnull) { continue; }
				cellObjs.push(cell);
				var num = cell.getNum();
				if (num > 0) {
					sum += num;
				} else {
					incomplete = true;
				}
			}

			if (incomplete) { return; }

			if (sum !== cage.targetSum) {
				this.failcode.add("bkSumNe");
				if (this.checkOnly) { return; }
				for (var j = 0; j < cellObjs.length; j++) {
					cellObjs[j].seterr(1);
				}
			}
		}
	},

	/* sudoku2: standard checks + even-digit balance */
	"AnsCheck@sudoku2#1": {
		checklist: [
			"checkDifferentNumberInRoom",
			"checkDifferentNumberInLine",
			"checkEvenDigitBalance",
			"checkNoNumCell+"
		]
	},
	"AnsCheck@sudoku2": {
		checkEvenDigitBalance: function() {
			var bd = this.board;
			for (var r = 0; r < bd.rows; r++) {
				var evenCount = 0;
				var rowCells = [];
				for (var c = 0; c < bd.cols; c++) {
					var cell = bd.getc(c * 2 + 1, r * 2 + 1);
					rowCells.push(cell);
					var num = cell.getNum();
					if (num > 0 && num % 2 === 0) { evenCount++; }
				}
				if (evenCount !== 4) {
					this.failcode.add("nmEvenBalance");
					if (this.checkOnly) { return; }
					for (var i = 0; i < rowCells.length; i++) {
						rowCells[i].seterr(1);
					}
					return;
				}
			}
		}
	}
});
