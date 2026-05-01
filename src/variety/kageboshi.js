//
// パズル固有スクリプト部 カゲボシ版 kageboshi.js
//
(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["kageboshi"], {
	//---------------------------------------------------------
	// マウス入力系
	MouseEvent: {
		use: true,
		inputModes: { edit: ["number", "clear"], play: ["shade", "unshade"] },
		autoedit_func: "qnum",
		autoplay_func: "cell"
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
		maxnum: function() {
			return this.board.cols + this.board.rows - 2;
		},
		minnum: 0
	},

	AreaUnshadeGraph: {
		enabled: true
	},

	//---------------------------------------------------------
	// 画像表示系
	Graphic: {
		gridcolor_type: "DASHED",

		numbercolor_func: "qnum",
		qanscolor: "black",

		paint: function() {
			this.drawBGCells();
			this.drawShadedCells();
			this.drawDotCells();
			this.drawGrid();
			this.drawQuesNumbers();
			this.drawChassis();
			this.drawTarget();
		},

		getQuesNumberColor: function(cell) {
			if (cell.error === 1) {
				return this.fontErrcolor;
			}
			return this.quescolor;
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
			"checkAdjacentShadeCell",
			"checkConnectUnshadeRB",
			"checkCrossCountOver",
			"checkCrossCountUnder",
			"doneShadingDecided"
		],

		checkCrossCountOver: function() {
			this.checkCrossCount(1, "kgCountGt");
		},
		checkCrossCountUnder: function() {
			this.checkCrossCount(2, "kgCountLt");
		},

		checkCrossCount: function(type, code) {
			var bd = this.board;
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				var qn = cell.qnum;
				if (qn < 0) {
					continue;
				}

				var row = cell.by >> 1;
				var col = cell.bx >> 1;
				var cnt = 0;

				for (var x = 0; x < bd.cols; x++) {
					if (x === col) {
						continue;
					}
					var rc = bd.getc(x * 2 + 1, cell.by);
					if (!rc.isnull && rc.isShade()) {
						cnt++;
					}
				}
				for (var y = 0; y < bd.rows; y++) {
					if (y === row) {
						continue;
					}
					var rc = bd.getc(cell.bx, y * 2 + 1);
					if (!rc.isnull && rc.isShade()) {
						cnt++;
					}
				}

				if ((type === 1 && qn >= cnt) || (type === 2 && qn <= cnt)) {
					continue;
				}

				this.failcode.add(code);
				if (this.checkOnly) {
					break;
				}
				cell.seterr(1);
				for (var x = 0; x < bd.cols; x++) {
					var rc = bd.getc(x * 2 + 1, cell.by);
					if (!rc.isnull && rc.isShade()) {
						rc.seterr(1);
					}
				}
				for (var y = 0; y < bd.rows; y++) {
					var rc = bd.getc(cell.bx, y * 2 + 1);
					if (!rc.isnull && rc.isShade()) {
						rc.seterr(1);
					}
				}
			}
		}
	},

	FailCode: {
		kgCountGt: "kgCountGt.kageboshi",
		kgCountLt: "kgCountLt.kageboshi"
	}
});
