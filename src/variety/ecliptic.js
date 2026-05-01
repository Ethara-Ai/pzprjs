//
// パズル固有スクリプト部 エクリプティック版 ecliptic.js
//
(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["ecliptic"], {
	//---------------------------------------------------------
	// マウス入力系
	MouseEvent: {
		use: true,
		inputModes: {
			edit: ["number", "clear"],
			play: ["shade", "unshade"]
		},
		mouseinput_auto: function() {
			if (this.puzzle.playmode) {
				if (this.mousestart || this.mousemove) {
					this.inputcell();
				}
			} else if (this.puzzle.editmode) {
				if (this.mousestart) {
					this.inputqnum();
				}
			}
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
		maxnum: 4,

		countShadedNeighbors: function() {
			var cnt = 0;
			var list = this.getdir4clist();
			for (var i = 0; i < list.length; i++) {
				if (list[i][0].isShade()) {
					cnt++;
				}
			}
			return cnt;
		}
	},

	Board: {
		hasborder: 0
	},

	AreaUnshadeGraph: {
		enabled: true
	},

	//---------------------------------------------------------
	// 画像表示系
	Graphic: {
		numbercolor_func: "qnum",
		circleratio: [0.42, 0.37],

		paint: function() {
			this.drawBGCells();
			this.drawShadedCells();
			this.drawDotCells();
			this.drawGrid();
			this.drawCircledNumbers();
			this.drawChassis();
			this.drawTarget();
		},

		getCircleStrokeColor: function(cell) {
			if (cell.isNum()) {
				if (cell.error === 1) {
					return this.errcolor1;
				}
				return this.quescolor;
			}
			return null;
		},
		getCircleFillColor: function(cell) {
			if (cell.isNum()) {
				return "white";
			}
			return null;
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
	// ファイル入出力系
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
		checklist: [
			"checkShadeCellExist",
			"check2x2ShadeCell+",
			"checkConnectUnshadeRB",
			"checkNeighborCount",
			"checkRowColBalance",
			"doneShadingDecided"
		],

		checkNeighborCount: function() {
			var bd = this.board;
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				if (!cell.isValidNum()) {
					continue;
				}
				var cnt = cell.countShadedNeighbors();
				if (cell.qnum !== cnt) {
					this.failcode.add("ecNeighborNe");
					if (this.checkOnly) {
						break;
					}
					cell.seterr(1);
				}
			}
		},

		checkRowColBalance: function() {
			var bd = this.board;
			if (bd.rows === 0 || bd.cols === 0) {
				return;
			}

			var rowCounts = [];
			for (var r = 0; r < bd.rows; r++) {
				var cnt = 0;
				for (var c = 0; c < bd.cols; c++) {
					var cell = bd.getc(c * 2 + 1, r * 2 + 1);
					if (cell.isShade()) {
						cnt++;
					}
				}
				rowCounts.push(cnt);
			}

			var rowTarget = rowCounts[0];
			for (var r2 = 1; r2 < bd.rows; r2++) {
				if (rowCounts[r2] !== rowTarget) {
					this.failcode.add("ecRowUnbal");
					if (this.checkOnly) {
						return;
					}
					for (var c2 = 0; c2 < bd.cols; c2++) {
						var cell2 = bd.getc(c2 * 2 + 1, r2 * 2 + 1);
						if (cell2.isShade()) {
							cell2.seterr(1);
						}
					}
					return;
				}
			}

			var colCounts = [];
			for (var c3 = 0; c3 < bd.cols; c3++) {
				var cnt3 = 0;
				for (var r3 = 0; r3 < bd.rows; r3++) {
					var cell3 = bd.getc(c3 * 2 + 1, r3 * 2 + 1);
					if (cell3.isShade()) {
						cnt3++;
					}
				}
				colCounts.push(cnt3);
			}

			var colTarget = colCounts[0];
			for (var c4 = 1; c4 < bd.cols; c4++) {
				if (colCounts[c4] !== colTarget) {
					this.failcode.add("ecColUnbal");
					if (this.checkOnly) {
						return;
					}
					for (var r4 = 0; r4 < bd.rows; r4++) {
						var cell4 = bd.getc(c4 * 2 + 1, r4 * 2 + 1);
						if (cell4.isShade()) {
							cell4.seterr(1);
						}
					}
					return;
				}
			}

			if (rowTarget !== colTarget) {
				this.failcode.add("ecRowColNe");
				if (this.checkOnly) {
					return;
				}
			}
		}
	},

	FailCode: {
		ecNeighborNe: "ecNeighborNe.ecliptic",
		ecRowUnbal: "ecRowUnbal.ecliptic",
		ecColUnbal: "ecColUnbal.ecliptic",
		ecRowColNe: "ecRowColNe.ecliptic"
	}
});
