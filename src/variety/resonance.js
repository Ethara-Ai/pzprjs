//
// パズル固有スクリプト部 レゾナンス版 resonance.js
//
(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["resonance"], {
	//---------------------------------------------------------
	// マウス入力系
	MouseEvent: {
		use: true,
		inputModes: {
			edit: ["number", "border", "clear"],
			play: ["number", "clear"]
		},
		mouseinput_auto: function() {
			if (this.puzzle.playmode) {
				if (this.mousestart) {
					this.inputqnum_play();
				}
			} else if (this.puzzle.editmode) {
				if (this.mousestart || this.mousemove) {
					if (this.isBorderMode()) {
						this.inputborder();
					} else {
						this.inputqnum();
					}
				}
			}
		},
		inputqnum_play: function() {
			var cell = this.getcell();
			if (cell.isnull || cell.qnum !== -1) {
				return;
			}
			// Cycle through: empty -> 1 -> 2 -> 3 -> empty
			var val = cell.anum;
			if (val === -1) {
				val = 1;
			} else if (val < 3) {
				val = val + 1;
			} else {
				val = -1;
			}
			cell.setAnum(val);
			cell.draw();
			this.mousereset();
		}
	},

	//---------------------------------------------------------
	// キーボード入力系
	KeyEvent: {
		enablemake: true,
		enableplay: true,
		moveTarget: function(ca) {
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
		maxnum: function() {
			return Math.max(this.board.cols, this.board.rows);
		},
		minnum: 0,

		// Play mode: emitters use anum (answer number)
		// Edit mode: clues use qnum (question number)
		posthook: {
			anum: function() {
				this.board.calcSignals();
			}
		}
	},

	Board: {
		hasborder: 1,

		cols: 6,
		rows: 6,

		// Signal strength cache: indexed by cell id
		signals: null,

		createExtraObject: function() {
			this.signals = [];
		},
		initExtraObject: function(col, row) {
			this.signals = new Array(this.cell.length);
			for (var i = 0; i < this.signals.length; i++) {
				this.signals[i] = 0;
			}
		},

		rebuildInfo: function() {
			this.calcSignals();
		},

		calcSignals: function() {
			if (!this.signals) {
				return;
			}
			var bd = this;
			// Reset all signals
			for (var i = 0; i < bd.cell.length; i++) {
				bd.signals[i] = 0;
			}
			// For each emitter, add signal to nearby cells
			for (var i = 0; i < bd.cell.length; i++) {
				var cell = bd.cell[i];
				var val = cell.anum;
				if (val <= 0) {
					continue;
				}
				// Emit signal: strength = val - manhattan_distance
				var cx = cell.bx;
				var cy = cell.by;
				for (var j = 0; j < bd.cell.length; j++) {
					var target = bd.cell[j];
					var dist =
						Math.abs(target.bx - cx) / 2 + Math.abs(target.by - cy) / 2;
					var strength = val - dist;
					if (strength > 0) {
						bd.signals[j] += strength;
					}
				}
			}
			// Trigger repaint for cells with clues
			this.puzzle.painter.paintRange(bd.minbx, bd.minby, bd.maxbx, bd.maxby);
		}
	},

	AreaRoomGraph: {
		enabled: true
	},

	//---------------------------------------------------------
	// 画像表示系
	Graphic: {
		gridcolor_type: "DASHED",

		paint: function() {
			this.drawBGCells();
			this.drawDashedGrid();
			this.drawBorders();

			this.drawEmitters();
			this.drawQuesNumbers();

			this.drawChassis();
			this.drawTarget();
		},

		getBGCellColor: function(cell) {
			if (cell.error === 1) {
				return this.errbcolor1;
			}
			// Show signal strength as background tint for cells with clues
			if (cell.qnum >= 0) {
				var sig = this.puzzle.board.signals[cell.id];
				if (sig === cell.qnum) {
					// Satisfied - light green
					return "rgba(144, 238, 144, 0.4)";
				} else if (sig > cell.qnum) {
					// Over-saturated - light red
					return "rgba(255, 160, 160, 0.4)";
				}
			}
			return null;
		},

		drawEmitters: function() {
			var g = this.vinc("cell_emitter", "auto");
			var rsize = this.cw * 0.36;
			var clist = this.range.cells;
			for (var i = 0; i < clist.length; i++) {
				var cell = clist[i];
				g.vid = "c_EM_" + cell.id;
				if (cell.anum > 0) {
					// Draw emitter circle
					var px = cell.bx * this.bw;
					var py = cell.by * this.bh;
					g.fillStyle = !cell.trial ? "rgb(50, 100, 200)" : this.trialcolor;
					g.fillCircle(px, py, rsize);

					// Draw number inside
					g.vid = "c_EMn_" + cell.id;
					g.fillStyle = "white";
					g.font = ((this.ch * 0.5) | 0) + "px " + this.fontfamily;
					g.textAlign = "center";
					g.textBaseline = "middle";
					g.fillText("" + cell.anum, px, py);
				} else {
					g.vhide();
					g.vid = "c_EMn_" + cell.id;
					g.vhide();
				}
			}
		},

		getQuesNumberColor: function(cell) {
			if (cell.qnum >= 0) {
				var sig = this.puzzle.board.signals[cell.id];
				if (sig > cell.qnum) {
					return this.errcolor1;
				}
			}
			return this.quescolor;
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
	FileIO: {
		decodeData: function() {
			this.decodeCellQnum();
			this.decodeAreaRoom();
			this.decodeCellAnumsub();
		},
		encodeData: function() {
			this.encodeCellQnum();
			this.encodeAreaRoom();
			this.encodeCellAnumsub();
		}
	},

	//---------------------------------------------------------
	// 正解判定処理実行部
	AnsCheck: {
		checklist: [
			"checkAdjacentEmitters",
			"checkRegionEmitters",
			"checkOverSaturated",
			"checkUnderSaturated"
		],

		// No two emitters orthogonally adjacent
		checkAdjacentEmitters: function() {
			var bd = this.board;
			for (var i = 0; i < bd.cell.length; i++) {
				var cell = bd.cell[i];
				if (cell.anum <= 0) {
					continue;
				}
				var adj = cell.adjacent;
				var dirs = [adj.top, adj.bottom, adj.left, adj.right];
				for (var d = 0; d < dirs.length; d++) {
					var cell2 = dirs[d];
					if (!cell2.isnull && cell2.anum > 0) {
						cell.seterr(1);
						cell2.seterr(1);
						this.failcode.add("emAdj");
						return;
					}
				}
			}
		},

		// No two emitters in the same region
		checkRegionEmitters: function() {
			var dominated = this.board.roommgr.components;
			for (var r = 0; r < dominated.length; r++) {
				var room = dominated[r];
				var count = 0;
				for (var i = 0; i < room.clist.length; i++) {
					if (room.clist[i].anum > 0) {
						count++;
					}
				}
				if (count > 1) {
					room.clist.seterr(1);
					this.failcode.add("emRegion");
					return;
				}
			}
		},

		// Clue cells must not receive more signal than their number
		checkOverSaturated: function() {
			var bd = this.board;
			for (var i = 0; i < bd.cell.length; i++) {
				var cell = bd.cell[i];
				if (cell.qnum < 0) {
					continue;
				}
				if (bd.signals[i] > cell.qnum) {
					cell.seterr(1);
					this.failcode.add("sigOver");
					return;
				}
			}
		},

		// Clue cells must receive exactly their number
		checkUnderSaturated: function() {
			var bd = this.board;
			for (var i = 0; i < bd.cell.length; i++) {
				var cell = bd.cell[i];
				if (cell.qnum < 0) {
					continue;
				}
				if (bd.signals[i] !== cell.qnum) {
					cell.seterr(1);
					this.failcode.add("sigUnder");
					return;
				}
			}
		}
	}
});
