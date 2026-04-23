//
// パズル固有スクリプト部 クロット・マインスイーパ版 kurotto.js
//

/* ---- mines helpers (classic Minesweeper) ---- */
var MINES_DIRS = [
	[-2, -2], [0, -2], [2, -2],
	[-2, 0],           [2, 0],
	[-2, 2],  [0, 2],  [2, 2]
];

function mines_isMine(cell) {
	return cell.qnum === -1;
}

function mines_isRevealed(cell) {
	return cell.qans === 1;
}

function mines_isFlagged(cell) {
	return cell.qsub === 1;
}

function mines_floodReveal(bd, startCell) {
	var queue = [startCell];
	startCell.setQans(1);
	startCell.setQsub(0);
	while (queue.length > 0) {
		var cell = queue.shift();
		if (cell.qnum !== 0) { continue; }
		for (var d = 0; d < 8; d++) {
			var nb = cell.relcell(MINES_DIRS[d][0], MINES_DIRS[d][1]);
			if (nb.isnull || nb.group !== "cell") { continue; }
			if (mines_isRevealed(nb)) { continue; }
			nb.setQans(1);
			nb.setQsub(0);
			queue.push(nb);
		}
	}
}

function mines_revealAllMines(bd) {
	for (var c = 0; c < bd.cell.length; c++) {
		var cell = bd.cell[c];
		if (mines_isMine(cell) && !mines_isRevealed(cell)) {
			cell.setQans(1);
			cell.setQsub(0);
		}
	}
}

function mines_checkWin(bd) {
	for (var c = 0; c < bd.cell.length; c++) {
		var cell = bd.cell[c];
		if (!mines_isMine(cell) && !mines_isRevealed(cell)) {
			return false;
		}
	}
	return true;
}

var MINES_NUM_COLORS = [
	null,
	"#0000FF", "#008000", "#FF0000", "#000080",
	"#800000", "#008080", "#000000", "#808080"
];
/* ---- end mines helpers ---- */

(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["kurotto", "mines", "island", "mines2"], {
	//---------------------------------------------------------
	// マウス入力系
	MouseEvent: {
		use: true,
		inputModes: { edit: ["number", "clear"], play: ["shade", "unshade"] },
		mouseinput_auto: function() {
			if (this.puzzle.playmode) {
				if (this.mousestart || this.mousemove) {
					this.inputcell();
				}
				if (this.mouseend && this.notInputted()) {
					this.inputqcmp();
				}
			} else if (this.puzzle.editmode) {
				if (this.mousestart) {
					this.inputqnum();
				}
			}
		},

		inputqcmp: function() {
			var cell = this.getcell();
			if (cell.isnull || cell.noNum()) {
				return;
			}

			cell.setQcmp(+!cell.qcmp);
			cell.draw();

			this.mousereset();
		}
	},
	"MouseEvent@mines": {
		inputModes: { edit: ["number", "clear"], play: [] },
		mouseinput_auto: function() {
			if (this.puzzle.editmode) {
				if (this.mousestart) { this.inputqnum(); }
				return;
			}
			if (!this.mousestart) { return; }
			var bd = this.board;
			if (bd._minesGameOver || bd._minesWon) { return; }

			var cell = this.getcell();
			if (cell.isnull) { return; }

			if (this.btn === "left") {
				if (mines_isFlagged(cell) || mines_isRevealed(cell)) {
					this.mousereset();
					return;
				}
				var cellRow = ((cell.by - 1) / 2) | 0;
				if (bd._lastRevealRow === cellRow) {
					var onlySameRow = true;
					for (var i = 0; i < bd.cell.length; i++) {
						var nb = bd.cell[i];
						if (!nb.isnull && !mines_isRevealed(nb) && !mines_isFlagged(nb) && !mines_isMine(nb)) {
							var nbRow = ((nb.by - 1) / 2) | 0;
							if (nbRow !== cellRow) { onlySameRow = false; break; }
						}
					}
					if (!onlySameRow) {
						cell.seterr(1); cell.draw();
						var c2 = cell;
						setTimeout(function() { c2.seterr(0); c2.draw(); }, 600);
						this.mousereset();
						return;
					}
				}
				bd._lastRevealRow = cellRow;
				if (mines_isMine(cell)) {
					cell.setQans(1);
					cell.seterr(1);
					mines_revealAllMines(bd);
					bd._minesGameOver = true;
					this.puzzle.redraw();
					this.mousereset();
					return;
				}
				mines_floodReveal(bd, cell);
				if (mines_checkWin(bd)) {
					bd._minesWon = true;
				}
				this.puzzle.redraw();
			} else if (this.btn === "right") {
				if (mines_isRevealed(cell)) {
					this.mousereset();
					return;
				}
			cell.setQsub(mines_isFlagged(cell) ? 0 : 1);
			cell.draw();
		}
		this.mousereset();
	}
	},
	"MouseEvent@mines2": {
		inputModes: { edit: ["number", "clear"], play: [] },
		mouseinput_auto: function() {
			if (this.puzzle.editmode) {
				if (this.mousestart) { this.inputqnum(); }
				return;
			}
			if (!this.mousestart) { return; }
			var bd = this.board;
			if (bd._minesGameOver || bd._minesWon) { return; }

			var cell = this.getcell();
			if (cell.isnull) { return; }

			if (this.btn === "left") {
				if (mines_isFlagged(cell) || mines_isRevealed(cell)) {
					this.mousereset();
					return;
				}
				if (mines_isMine(cell)) {
					cell.setQans(1);
					cell.seterr(1);
					mines_revealAllMines(bd);
					bd._minesGameOver = true;
					bd._minesStreak = 0;
					this.puzzle.redraw();
					this.mousereset();
					return;
				}
				mines_floodReveal(bd, cell);
				bd._minesStreak = (bd._minesStreak || 0) + 1;

				if (bd._minesStreak % 3 === 0) {
					var hidden = [];
					for (var i = 0; i < bd.cell.length; i++) {
						var nb = bd.cell[i];
						if (!nb.isnull && !mines_isMine(nb) && !mines_isRevealed(nb) && !mines_isFlagged(nb)) {
							hidden.push(nb);
						}
					}
					if (hidden.length > 0) {
						var lucky = hidden[(bd._minesStreak * 7 + bd.cols) % hidden.length];
						mines_floodReveal(bd, lucky);
					}
				}

				if (mines_checkWin(bd)) {
					bd._minesWon = true;
				}
				this.puzzle.redraw();
			} else if (this.btn === "right") {
				if (mines_isRevealed(cell)) {
					this.mousereset();
					return;
				}
				cell.setQsub(mines_isFlagged(cell) ? 0 : 1);
				cell.draw();
			}
			this.mousereset();
		}
	},
	"MouseEvent@island": {
		inputModes: {
			edit: ["number", "clear"],
			play: ["shade", "unshade", "info-blk"]
		},
		dispInfoBlk: function() {
			var cell = this.getcell();
			this.mousereset();
			if (cell.isnull || !cell.island) {
				return;
			}
			cell.island.clist.setinfo(1);
			this.board.hasinfo = true;
			this.puzzle.redraw();
		}
	},

	//---------------------------------------------------------
	// キーボード入力系
	KeyEvent: {
		enablemake: true
	},

	//---------------------------------------------------------
	// 盤面管理系
	Cell: {
		numberRemainsUnshaded: true,

		minnum: 0,

		isCmp: function() {
			if (!(this.qnum === -2 || this.isValidNum())) {
				return false;
			}
			if (this.qcmp === 1) {
				return true;
			}
			if (!this.puzzle.execConfig("autocmp")) {
				return false;
			}
			return this.checkComplete();
		}
	},
	"Board@island": {
		addExtraInfo: function() {
			this.islandgraph = this.addInfoList(this.klass.AreaIslandGraph);
		}
	},
	"Board@mines": {
		initBoardSize: function(col, row) {
			this.common.initBoardSize.call(this, col, row);
			this._minesGameOver = false;
			this._minesWon = false;
			this._lastRevealRow = -1;
		}
	},
	"Board@mines2": {
		initBoardSize: function(col, row) {
			this.common.initBoardSize.call(this, col, row);
			this._minesGameOver = false;
			this._minesWon = false;
			this._minesStreak = 0;
		}
	},
	"Cell@kurotto,island": {
		maxnum: function() {
			var max = this.board.cell.length - 1;
			return max <= 999 ? max : 999;
		},

		checkComplete: function() {
			if (!this.isValidNum()) {
				return true;
			}

			var cnt = 0,
				arealist = [],
				list = this.getdir4clist();
			for (var i = 0; i < list.length; i++) {
				var area = list[i][0].sblk;
				if (area !== null) {
					for (var j = 0; j < arealist.length; j++) {
						if (arealist[j] === area) {
							area = null;
							break;
						}
					}
					if (area !== null) {
						cnt += area.clist.length;
						arealist.push(area);
					}
				}
			}
			return this.qnum === cnt;
		}
	},
	"Cell@mines": {
		maxnum: 8,

		checkComplete: function() {
			if (!this.isValidNum()) {
				return true;
			}

			var cnt = 0;
			var cells = [
				this.relcell(-2, -2),
				this.relcell(0, -2),
				this.relcell(2, -2),
				this.relcell(-2, 0),
				this.relcell(2, 0),
				this.relcell(-2, 2),
				this.relcell(0, 2),
				this.relcell(2, 2)
			];
			for (var i = 0; i < 8; i++) {
				if (
					cells[i].group === "cell" &&
					!cells[i].isnull &&
					cells[i].isShade()
				) {
					cnt++;
				}
			}
			return this.qnum === cnt;
		}
	},

	"AreaShadeGraph@kurotto,island": {
		enabled: true
	},
	"AreaIslandGraph:AreaShadeGraph@island": {
		enabled: true,
		coloring: true,
		relation: { "cell.qans": "node", "cell.qnum": "node" },
		setComponentRefs: function(obj, component) {
			obj.island = component;
		},
		getObjNodeList: function(nodeobj) {
			return nodeobj.islandnodes;
		},
		resetObjNodeList: function(nodeobj) {
			nodeobj.islandnodes = [];
		},

		isnodevalid: function(cell) {
			return cell.isShade() || cell.isNum();
		}
	},

	//---------------------------------------------------------
	// 画像表示系
	Graphic: {
		autocmp: "number",

		qanscolor: "black",

		// オーバーライド
		setRange: function(x1, y1, x2, y2) {
			var puzzle = this.puzzle,
				bd = puzzle.board;
			if (puzzle.execConfig("autocmp")) {
				x1 = bd.minbx - 2;
				y1 = bd.minby - 2;
				x2 = bd.maxbx + 2;
				y2 = bd.maxby + 2;
			}

			this.common.setRange.call(this, x1, y1, x2, y2);
		}
	},
	"Graphic@kurotto,island": {
		hideHatena: true,

		numbercolor_func: "qnum",

		circleratio: [0.45, 0.4],

		paint: function() {
			this.drawBGCells();
			this.drawShadedCells();
			this.drawDotCells();
			this.drawGrid();

			this.drawCircledNumbers();

			this.drawChassis();

			this.drawTarget();
		},

		getCircleFillColor: function(cell) {
			if (cell.isCmp()) {
				return this.qcmpcolor;
			}
			return null;
		}
	},
	"Graphic@island#1": {
		irowakeblk: true,

		getCircleFillColor: function(cell) {
			if (!cell.isCmp()) {
				return null;
			}
			var hasinfo = this.board.haserror || this.board.hasinfo;
			if (this.puzzle.execConfig("irowakeblk") && !hasinfo) {
				var color = cell.island.color;
				if (typeof color !== "string") {
					return color;
				}

				return color.replace("rgb", "rgba").replace(")", ",0.25)");
			}
			return this.qcmpcolor;
		},

		getShadedCellColor: function(cell) {
			if (cell.qans !== 1) {
				return null;
			}
			var hasinfo = this.board.haserror || this.board.hasinfo;
			var info = cell.error || cell.qinfo;
			if (info === 1) {
				return this.errcolor1;
			} else if (info === 2) {
				return this.errcolor2;
			} else if (cell.trial) {
				return this.trialcolor;
			} else if (this.puzzle.execConfig("irowakeblk") && !hasinfo) {
				return cell.island.color;
			}
			return this.shadecolor;
		}
	},
	"Graphic@mines": {
		paint: function() {
			this.drawBGCells();
			this.drawMinesHiddenCells();
			this.drawMinesRevealedNumbers();
			this.drawMinesMines();
			this.drawMinesFlags();
			this.drawGrid();
			this.drawChassis();
			this.drawTarget();
		},

		drawMinesHiddenCells: function() {
			var g = this.vinc("mines_hidden", "crispEdges", true);
			var clist = this.range.cells;
			for (var i = 0; i < clist.length; i++) {
				var cell = clist[i];
				g.vid = "m_hid_" + cell.id;
				if (!mines_isRevealed(cell)) {
					var px = cell.bx * this.bw;
					var py = cell.by * this.bh;
					g.fillStyle = mines_isFlagged(cell) ? "#999999" : "#BBBBBB";
					g.fillRectCenter(px, py, this.bw - 0.5, this.bh - 0.5);
					g.strokeStyle = "#DDDDDD";
					g.lineWidth = 1;
					g.strokeRect(px - this.bw + 1, py - this.bh + 1, (this.bw - 1) * 2, (this.bh - 1) * 2);
				} else {
					g.vhide();
				}
			}
		},

		drawMinesRevealedNumbers: function() {
			var g = this.vinc("mines_nums", "auto", true);
			var clist = this.range.cells;
			for (var i = 0; i < clist.length; i++) {
				var cell = clist[i];
				g.vid = "m_num_" + cell.id;
				if (mines_isRevealed(cell) && !mines_isMine(cell) && cell.qnum > 0) {
					var color = MINES_NUM_COLORS[cell.qnum] || "#000000";
					this.disptext("" + cell.qnum, cell.bx * this.bw, cell.by * this.bh, { ratio: 0.65, color: color });
				} else {
					g.vhide();
				}
			}
		},

		drawMinesMines: function() {
			var g = this.vinc("mines_bombs", "auto", true);
			var clist = this.range.cells;
			for (var i = 0; i < clist.length; i++) {
				var cell = clist[i];
				g.vid = "m_mine_" + cell.id;
				if (mines_isRevealed(cell) && mines_isMine(cell)) {
					var px = cell.bx * this.bw;
					var py = cell.by * this.bh;
					var r = this.bw * 0.3;
					if (cell.error === 1) {
						g.fillStyle = "#FF0000";
						g.fillRectCenter(px, py, this.bw + 0.5, this.bh + 0.5);
					}
					g.fillStyle = "#000000";
					g.beginPath();
					g.arc(px, py, r, 0, Math.PI * 2, false);
					g.fill();
				} else {
					g.vhide();
				}
			}
		},

		drawMinesFlags: function() {
			var g = this.vinc("mines_flags", "auto", true);
			var clist = this.range.cells;
			for (var i = 0; i < clist.length; i++) {
				var cell = clist[i];
				g.vid = "m_flag_" + cell.id;
				if (!mines_isRevealed(cell) && mines_isFlagged(cell)) {
					var px = cell.bx * this.bw;
					var py = cell.by * this.bh;
					var sz = this.bw * 0.3;
					g.fillStyle = "#FF0000";
					g.beginPath();
					g.moveTo(px - sz, py - sz);
					g.lineTo(px + sz, py - sz * 0.2);
					g.lineTo(px - sz, py + sz * 0.6);
					g.closePath();
					g.fill();
					g.strokeStyle = "#000000";
					g.lineWidth = 2;
					g.beginPath();
					g.moveTo(px - sz, py - sz);
					g.lineTo(px - sz, py + sz);
					g.stroke();
				} else {
					g.vhide();
				}
			}
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
		}
	},
	//---------------------------------------------------------
	FileIO: {
		decodeData: function() {
			this.decodeCellQnum();
			this.decodeCellAns();
		},
		encodeData: function() {
			this.encodeCellQnum();
			this.encodeCellAns();
		}
	},

	//---------------------------------------------------------
	// 正解判定処理実行部
	AnsCheck: {
		checkCellNumber: function(code) {
			var bd = this.board;
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				if (cell.checkComplete()) {
					continue;
				}

				this.failcode.add(code);
				if (this.checkOnly) {
					break;
				}
				cell.seterr(1);
			}
		}
	},
	"AnsCheck@kurotto,island": {
		checklist: [
			"checkShadeCellExist",
			"checkCellNumber_kurotto",
			"checkConnectShaded_island@island"
		],

		checkCellNumber_kurotto: function() {
			this.checkCellNumber("nmSumSizeNe");
		},
		checkConnectShaded_island: function() {
			this.checkOneArea(this.board.islandgraph, "csDivide");
		}
	},
	"AnsCheck@mines": {
		checklist: ["checkMinesComplete", "checkNo2x2MineBlock", "checkMineDensity"],

		checkMinesComplete: function() {
			var bd = this.board;
			if (bd._minesGameOver) {
				this.failcode.add("minesExploded");
				return;
			}
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				if (!mines_isMine(cell) && !mines_isRevealed(cell)) {
					this.failcode.add("minesIncomplete");
					return;
				}
			}
		},
		checkNo2x2MineBlock: function() {
			var bd = this.board;
			for (var r = 0; r < bd.rows - 1; r++) {
				for (var c = 0; c < bd.cols - 1; c++) {
					var c00 = bd.getc(c * 2 + 1, r * 2 + 1);
					var c01 = bd.getc(c * 2 + 3, r * 2 + 1);
					var c10 = bd.getc(c * 2 + 1, r * 2 + 3);
					var c11 = bd.getc(c * 2 + 3, r * 2 + 3);
					if (mines_isMine(c00) && mines_isMine(c01) && mines_isMine(c10) && mines_isMine(c11)) {
						this.failcode.add("mines2x2Block");
						if (this.checkOnly) { return; }
						c00.seterr(1); c01.seterr(1); c10.seterr(1); c11.seterr(1);
						return;
					}
				}
			}
		},
		checkMineDensity: function() {
			var bd = this.board;
			var total = bd.cell.length;
			var mineCount = 0;
			for (var i = 0; i < total; i++) {
				if (mines_isMine(bd.cell[i])) { mineCount++; }
			}
			if (mineCount * 4 <= total) { return; }
			this.failcode.add("minesTooManyMines");
			if (this.checkOnly) { return; }
			for (var j = 0; j < total; j++) {
				if (mines_isMine(bd.cell[j])) { bd.cell[j].seterr(1); }
			}
		}
	},
	"Graphic@mines2": {
		paint: function() {
			this.drawMinesHiddenCells();
			this.drawMinesRevealedNumbers();
			this.drawMinesMines();
			this.drawMinesFlags();
			this.drawGrid();
			this.drawChassis();
			this.drawTarget();
			this.drawStreakCounter();
		},

		drawMinesHiddenCells: function() {
			var bd = this.board;
			var g = this.vinc("m2_hidden", "crispEdges", true);
			var bw = this.bw, bh = this.bh;
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				g.vid = "m2h_" + cell.id;
				if (!mines_isRevealed(cell)) {
					g.fillStyle = mines_isFlagged(cell) ? "#999999" : "#BBBBBB";
					g.fillRectCenter(cell.bx * bw, cell.by * bh, bw + 0.5, bh + 0.5);
					g.strokeStyle = "#DDDDDD";
					g.lineWidth = 1;
					g.strokeRect(
						cell.bx * bw - bw / 2 + 0.5,
						cell.by * bh - bh / 2 + 0.5,
						bw - 1, bh - 1
					);
				} else {
					g.vhide();
				}
			}
		},

		drawMinesRevealedNumbers: function() {
			var bd = this.board;
			var g = this.vinc("m2_nums", "auto");
			var bw = this.bw, bh = this.bh;
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				g.vid = "m2n_" + cell.id;
				if (mines_isRevealed(cell) && !mines_isMine(cell) && cell.qnum > 0) {
					var color = MINES_NUM_COLORS[cell.qnum] || "#000000";
					this.disptext("" + cell.qnum, cell.bx * bw, cell.by * bh, {
						ratio: 0.65,
						color: color
					});
				} else {
					g.vhide();
				}
			}
		},

		drawMinesMines: function() {
			var bd = this.board;
			var g = this.vinc("m2_mines", "auto");
			var bw = this.bw, bh = this.bh;
			var mrad = Math.max(bw * 0.25, 3);
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				g.vid = "m2m_bg_" + cell.id;
				if (mines_isRevealed(cell) && mines_isMine(cell)) {
					if (cell.error === 1) {
						g.fillStyle = "#FF4444";
						g.fillRectCenter(cell.bx * bw, cell.by * bh, bw + 0.5, bh + 0.5);
					} else {
						g.vhide();
					}
					g.vid = "m2m_" + cell.id;
					g.fillStyle = "#000000";
					g.beginPath();
					g.arc(cell.bx * bw, cell.by * bh, mrad, 0, Math.PI * 2, false);
					g.fill();
				} else {
					g.vhide();
					g.vid = "m2m_" + cell.id;
					g.vhide();
				}
			}
		},

		drawMinesFlags: function() {
			var bd = this.board;
			var g = this.vinc("m2_flags", "auto");
			var bw = this.bw, bh = this.bh;
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				g.vid = "m2f_" + cell.id;
				if (!mines_isRevealed(cell) && mines_isFlagged(cell)) {
					var cx = cell.bx * bw, cy = cell.by * bh;
					var fh = bh * 0.6, fw = bw * 0.35;
					g.fillStyle = "#CC0000";
					g.beginPath();
					g.moveTo(cx - fw * 0.3, cy - fh * 0.5);
					g.lineTo(cx + fw * 0.5, cy - fh * 0.15);
					g.lineTo(cx - fw * 0.3, cy + fh * 0.2);
					g.closePath();
					g.fill();
					g.strokeStyle = "#000000";
					g.lineWidth = Math.max(bw / 12, 1);
					g.beginPath();
					g.moveTo(cx - fw * 0.3, cy - fh * 0.5);
					g.lineTo(cx - fw * 0.3, cy + fh * 0.5);
					g.stroke();
				} else {
					g.vhide();
				}
			}
		},

		drawStreakCounter: function() {
			var bd = this.board;
			var streak = bd._minesStreak || 0;
			var g = this.vinc("m2_streak", "auto");
			g.vid = "m2streak_text";
			if (streak > 0 && !bd._minesGameOver && !bd._minesWon) {
				var bw = this.bw;
				var nextBonus = 3 - (streak % 3);
				var px = bw;
				var py = this.bh * 0.4;
				this.disptext("Streak:" + streak + " (bonus in " + nextBonus + ")", px, py, {
					ratio: 0.2,
					color: "#FF8800"
				});
			} else {
				g.vhide();
			}
		}
	},
	"AnsCheck@mines2": {
		checklist: ["checkMinesComplete", "checkRowMineCap", "checkNo2x2MineBlock"],

		checkMinesComplete: function() {
			var bd = this.board;
			if (bd._minesGameOver) {
				this.failcode.add("minesExploded");
				return;
			}
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				if (!mines_isMine(cell) && !mines_isRevealed(cell)) {
					this.failcode.add("minesIncomplete");
					return;
				}
			}
		},
		checkRowMineCap: function() {
			var bd = this.board;
			var cap = Math.ceil(2 * bd.cols / 3);
			for (var r = 0; r < bd.rows; r++) {
				var rowMines = 0;
				for (var c = 0; c < bd.cols; c++) {
					if (mines_isMine(bd.getc(c * 2 + 1, r * 2 + 1))) { rowMines++; }
				}
				if (rowMines > cap) {
					this.failcode.add("minesRowTooMany");
					if (this.checkOnly) { return; }
					for (var c2 = 0; c2 < bd.cols; c2++) {
						var cell = bd.getc(c2 * 2 + 1, r * 2 + 1);
						if (mines_isMine(cell)) { cell.seterr(1); }
					}
					return;
				}
			}
		},
		checkNo2x2MineBlock: function() {
			var bd = this.board;
			for (var r = 0; r < bd.rows - 1; r++) {
				for (var c = 0; c < bd.cols - 1; c++) {
					var c00 = bd.getc(c * 2 + 1, r * 2 + 1);
					var c01 = bd.getc(c * 2 + 3, r * 2 + 1);
					var c10 = bd.getc(c * 2 + 1, r * 2 + 3);
					var c11 = bd.getc(c * 2 + 3, r * 2 + 3);
					if (mines_isMine(c00) && mines_isMine(c01) && mines_isMine(c10) && mines_isMine(c11)) {
						this.failcode.add("mines2x2Block");
						if (this.checkOnly) { return; }
						c00.seterr(1); c01.seterr(1); c10.seterr(1); c11.seterr(1);
						return;
					}
				}
			}
		}
	}
});
