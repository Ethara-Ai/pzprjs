//
// パズル固有スクリプト部 タイドプール版 tidepool.js
//
// Tidepool: Shade or leave cells unshaded.
// Each unshaded cell has a "depth" equal to its BFS distance
// (through unshaded cells) to the nearest grid-border cell.
// Border cells that are unshaded have depth 0.
// Clue cells show exact depths and cannot be shaded.
// Unshaded cells must form a single connected group.
//
(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["tidepool"], {
	//---------------------------------------------------------
	// マウス入力系
	MouseEvent: {
		use: true,
		inputModes: {
			edit: ["number", "clear"],
			play: ["shade", "unshade", "info-blk"]
		},
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
			var half = Math.min(this.board.cols, this.board.rows);
			return Math.floor(half / 2);
		},
		minnum: 0
	},

	Board: {
		cols: 8,
		rows: 8,

		customRules: [
			"Shade some cells. Unshaded cells form a single connected group.",
			"Each unshaded cell has a depth = BFS distance to the nearest border cell through unshaded cells only.",
			"Border unshaded cells have depth 0.",
			"Clue numbers show the exact depth of that cell. Clue cells cannot be shaded.",
			"No 2x2 block of cells may be entirely shaded."
		]
	},

	AreaShadeGraph: {
		enabled: true,
		coloring: true
	},
	AreaUnshadeGraph: {
		enabled: true
	},

	//---------------------------------------------------------
	// 画像表示系
	Graphic: {
		numbercolor_func: "qnum",
		qanscolor: "black",
		enablebcolor: true,

		paint: function() {
			this.drawBGCells();
			this.drawShadedCells();
			this.drawDotCells();
			this.drawGrid();
			this.drawQuesNumbers();
			this.drawChassis();
			this.drawTarget();
		},

		getBGCellColor: function(cell) {
			if (cell.error > 0 || cell.qinfo > 0) {
				return this.errbcolor1;
			} else if (cell.qsub === 1) {
				return this.bcolor;
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
			"check2x2ShadeCell",
			"checkConnectUnshade",
			"checkTidepoolDepth",
			"doneShadingDecided"
		],

		checkConnectUnshade: function() {
			this.checkOneArea(this.board.ublkmgr, "cuDivide");
		},

		checkTidepoolDepth: function() {
			var bd = this.board;
			var rows = bd.rows;
			var cols = bd.cols;

			// BFS from all border unshaded cells
			var dist = {};
			var queue = [];

			// Initialize: border cells that are unshaded get distance 0
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				if (cell.isShade()) {
					continue;
				}
				var r = Math.floor((cell.by - 1) / 2);
				var col = Math.floor((cell.bx - 1) / 2);
				if (r === 0 || r === rows - 1 || col === 0 || col === cols - 1) {
					dist[cell.id] = 0;
					queue.push(cell);
				}
			}

			// BFS
			var head = 0;
			while (head < queue.length) {
				var cur = queue[head++];
				var d = dist[cur.id];
				var adj = cur.adjacent;
				var dirs = ["top", "bottom", "left", "right"];
				for (var i = 0; i < dirs.length; i++) {
					var nb = adj[dirs[i]];
					if (!nb || nb.isnull || nb.isShade()) {
						continue;
					}
					if (dist[nb.id] === undefined) {
						dist[nb.id] = d + 1;
						queue.push(nb);
					}
				}
			}

			// Check clue cells against BFS distance
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				if (!cell.isValidNum()) {
					continue;
				}

				var expected = cell.qnum;
				var actual = dist[cell.id];

				if (actual === undefined || actual !== expected) {
					this.failcode.add("tpDepthNe");
					if (this.checkOnly) {
						return;
					}
					cell.seterr(1);
				}
			}
		}
	},

	FailCode: {}
});
