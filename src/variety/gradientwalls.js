//
// パズル固有スクリプト部 グラデーション・ウォールズ版 gradientwalls.js
//
// Gradient Walls: Fill each empty cell with a number 1..N.
// A wall (thick border) between two adjacent cells means their values
// differ by more than 1. An open border means their values differ by
// at most 1. Clue numbers are given and cannot be changed.
//
(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["gradientwalls"], {
	//---------------------------------------------------------
	// マウス入力系
	MouseEvent: {
		inputModes: {
			edit: ["border", "number", "clear"],
			play: ["number", "clear"]
		},
		autoedit_func: "areanum",
		autoplay_func: "qnum",
		inputqnum: function() {
			var cell = this.getcell();
			if (cell.isnull || cell === this.mouseCell) {
				return;
			}
			if (this.puzzle.playmode && cell.qnum !== -1) {
				return;
			}
			if (cell !== this.cursor.getc()) {
				this.setcursor(cell);
			} else {
				this.inputqnum_main(cell);
			}
			this.mouseCell = cell;
		}
	},

	//---------------------------------------------------------
	// キーボード入力系
	KeyEvent: {
		enablemake: true,
		enableplay: true,
		moveTarget: function(ca) {
			if (this.puzzle.playmode) {
				var cursor = this.cursor;
				var pos0 = cursor.getaddr();
				var moved = this.moveTCell(ca);
				if (!moved) {
					return false;
				}
				var cell = cursor.getobj();
				var limit = Math.max(this.puzzle.board.cols, this.puzzle.board.rows);
				var count = 0;
				while (cell && !cell.isnull && cell.qnum !== -1 && count < limit) {
					moved = this.moveTCell(ca);
					if (!moved) {
						cursor.setaddr(pos0);
						cursor.draw();
						pos0.draw();
						return false;
					}
					cell = cursor.getobj();
					count++;
				}
				if (cell && !cell.isnull && cell.qnum !== -1) {
					cursor.setaddr(pos0);
					cursor.draw();
					pos0.draw();
					return false;
				}
				return true;
			}
			return this.moveTCell(ca);
		},
		keyinput: function(ca) {
			this.key_inputqnum(ca);
		}
	},

	//---------------------------------------------------------
	// 盤面管理系
	Cell: {
		numberRemainsUnshaded: true,
		disInputHatena: true,
		supportQnumAnum: true,

		maxnum: function() {
			return Math.max(this.board.cols, this.board.rows);
		},
		minnum: 1,

		setNum: function(val) {
			if (val === 0) {
				return;
			}
			if (this.puzzle.editmode) {
				this.setQnum(val);
			} else {
				if (this.qnum !== -1) {
					return;
				}
				this.setAnum(val);
			}
		},
		getNum: function() {
			if (this.puzzle.editmode) {
				return this.qnum;
			}
			if (this.qnum !== -1) {
				return this.qnum;
			}
			return this.anum;
		}
	},

	Board: {
		hasborder: 1,
		cols: 7,
		rows: 7
	},

	//---------------------------------------------------------
	// 画像表示系
	Graphic: {
		gridcolor_type: "DASHED",

		paint: function() {
			this.drawBGCells();
			this.drawDashedGrid();
			this.drawBorders();
			this.drawQuesNumbers();
			this.drawAnsNumbers();
			this.drawChassis();
			this.drawCursor();
		},

		getBGCellColor: function(cell) {
			if (cell.error === 1) {
				return this.errbcolor1;
			}
			if (cell.qnum !== -1) {
				return "rgb(227, 238, 255)";
			}
			return null;
		},

		getAnsNumberColor: function(cell) {
			if (cell.error === 1) {
				return this.errcolor1;
			}
			return cell.trial ? this.trialcolor : this.qanscolor;
		}
	},

	//---------------------------------------------------------
	// URLエンコード/デコード処理
	Encode: {
		decodePzpr: function(type) {
			this.decodeNumber16();
			this.decodeBorder();
		},
		encodePzpr: function(type) {
			this.encodeNumber16();
			this.encodeBorder();
		}
	},

	//---------------------------------------------------------
	// ファイル入出力系
	FileIO: {
		decodeData: function() {
			this.decodeCellQnum();
			this.decodeBorderQues();
			this.decodeCellAnumsub();
		},
		encodeData: function() {
			this.encodeCellQnum();
			this.encodeBorderQues();
			this.encodeCellAnumsub();
		}
	},

	//---------------------------------------------------------
	// 正解判定処理実行部
	AnsCheck: {
		checklist: ["checkGradientWallConsistency", "checkAllCellsFilled"],

		// Main rule: wall ↔ |a-b| > 1, no wall ↔ |a-b| <= 1
		checkGradientWallConsistency: function() {
			var bd = this.board;
			for (var i = 0; i < bd.border.length; i++) {
				var border = bd.border[i];
				var cell1 = border.sidecell[0];
				var cell2 = border.sidecell[1];
				if (!cell1 || cell1.isnull || !cell2 || cell2.isnull) {
					continue;
				}

				var val1 = cell1.qnum !== -1 ? cell1.qnum : cell1.anum;
				var val2 = cell2.qnum !== -1 ? cell2.qnum : cell2.anum;

				if (val1 <= 0 || val2 <= 0) {
					continue;
				}

				var diff = Math.abs(val1 - val2);
				var hasWall = border.isBorder();

				if (hasWall && diff <= 1) {
					// Wall exists but values are too close
					cell1.seterr(1);
					cell2.seterr(1);
					this.failcode.add("gwWallClose");
					if (this.checkOnly) {
						return;
					}
				} else if (!hasWall && diff > 1) {
					// No wall but values are too far apart
					cell1.seterr(1);
					cell2.seterr(1);
					this.failcode.add("gwOpenFar");
					if (this.checkOnly) {
						return;
					}
				}
			}
		},

		// All cells must have a number
		checkAllCellsFilled: function() {
			var bd = this.board;
			for (var i = 0; i < bd.cell.length; i++) {
				var cell = bd.cell[i];
				if (cell.qnum === -1 && cell.anum <= 0) {
					this.failcode.add("ceEmpty");
					if (this.checkOnly) {
						return;
					}
					cell.seterr(1);
				}
			}
		}
	},

	FailCode: {
		gwWallClose: "gwWallClose.gradientwalls",
		gwOpenFar: "gwOpenFar.gradientwalls"
	}
});
