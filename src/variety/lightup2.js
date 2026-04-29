//
// パズル固有スクリプト部 美術館2版 lightup2.js
//
(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["lightup2"], {
	//---------------------------------------------------------
	// マウス入力系
	MouseEvent: {
		use: true,
		inputModes: {
			edit: ["number", "clear"],
			play: ["akari", "unshade", "completion"]
		},
		mouseinput_other: function() {
			if (this.inputMode === "akari" && this.mousestart) {
				this.inputcell();
			}
		},
		mouseinput_auto: function() {
			if (this.puzzle.playmode) {
				if (this.mousestart || (this.mousemove && this.inputData !== 1)) {
					this.inputcell();
				} else if (this.mouseend && this.notInputted()) {
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

	//---------------------------------------------------------
	// キーボード入力系
	KeyEvent: {
		enablemake: true
	},

	//---------------------------------------------------------
	// 盤面管理系
	Cell: {
		akariinfo: 0 /* 0:なし 1:あかり 2:黒マス */,
		qlight: 0,

		numberRemainsUnshaded: true,

		maxnum: 4,
		minnum: 0,

		posthook: {
			qnum: function(num) {
				this.setAkariInfo(num);
			},
			qans: function(num) {
				this.setAkariInfo(num);
			}
		},

		isAkari: function() {
			return this.qans === 1;
		},

		setAkariInfo: function(num) {
			var val = 0,
				old = this.akariinfo;
			if (this.qnum !== -1) {
				val = 2;
			} else if (this.qans === 1) {
				val = 1;
			}
			if (old === val) {
				return;
			}

			this.akariinfo = val;
			this.setQlight(old, val);
		},
		setQlight: function(old, val) {
			var clist = this.akariRangeClist();
			if (old === 0 && val === 1) {
				for (var i = 0; i < clist.length; i++) {
					clist[i].qlight = 1;
				}
			} else {
				for (var i = 0; i < clist.length; i++) {
					var cell2 = clist[i],
						ql_old = cell2.qlight;
					if (
						ql_old === 0 &&
						((old === 1 && val === 0) || (old === 0 && val === 2))
					) {
						continue;
					}
					if (ql_old === 1 && old === 2 && val === 0) {
						continue;
					}

					cell2.qlight = cell2.akariRangeClist().some(function(cell) {
						return cell.isAkari();
					})
						? 1
						: 0;
				}
				if (val === 2) {
					this.qlight = 0;
				}
			}

			var d = this.viewRange();
			this.puzzle.painter.paintRange(
				d.x1 - 1,
				d.y1 - 1,
				d.x2 + 1,
				d.y2 + 1
			);
		},

		/* Diagonal ray illumination: 4 diagonal directions until wall/edge */
		akariRangeClist: function() {
			var clist = new this.klass.CellList(),
				bd = this.board;
			var dirs = [
				[-2, -2],
				[-2, 2],
				[2, -2],
				[2, 2]
			];
			for (var d = 0; d < dirs.length; d++) {
				var dx = dirs[d][0],
					dy = dirs[d][1];
				var bx = this.bx + dx,
					by = this.by + dy;
				while (true) {
					var cell2 = bd.getc(bx, by);
					if (cell2.isnull) {
						break;
					}
					if (cell2.qnum !== -1) {
						break;
					}
					clist.add(cell2);
					bx += dx;
					by += dy;
				}
			}
			return clist;
		},
		viewRange: function() {
			var bd = this.board,
				x1 = this.bx,
				x2 = this.bx,
				y1 = this.by,
				y2 = this.by;
			var dirs = [
				[-2, -2],
				[-2, 2],
				[2, -2],
				[2, 2]
			];
			for (var d = 0; d < dirs.length; d++) {
				var dx = dirs[d][0],
					dy = dirs[d][1];
				var bx = this.bx + dx,
					by = this.by + dy;
				while (true) {
					var cell2 = bd.getc(bx, by);
					if (cell2.isnull || cell2.qnum !== -1) {
						break;
					}
					if (bx < x1) { x1 = bx; }
					if (bx > x2) { x2 = bx; }
					if (by < y1) { y1 = by; }
					if (by > y2) { y2 = by; }
					bx += dx;
					by += dy;
				}
			}
			return { x1: x1, x2: x2, y1: y1, y2: y2 };
		}
	},

	Board: {
		rebuildInfo: function() {
			this.initQlight();
		},

		initQlight: function() {
			for (var c = 0; c < this.cell.length; c++) {
				var cell = this.cell[c];
				cell.qlight = 0;
				cell.akariinfo = 0;
				if (cell.qnum !== -1) {
					cell.akariinfo = 2;
				} else if (cell.qans === 1) {
					cell.akariinfo = 1;
				}
			}
			for (var c = 0; c < this.cell.length; c++) {
				var cell = this.cell[c];
				if (cell.akariinfo !== 1) {
					continue;
				}

				var clist = cell.akariRangeClist();
				for (var i = 0; i < clist.length; i++) {
					clist[i].qlight = 1;
				}
			}
		}
	},

	//---------------------------------------------------------
	// 画像表示系
	Graphic: {
		hideHatena: true,
		autocmp: "akari",

		gridcolor_type: "LIGHT",

		fgcellcolor_func: "qnum",

		fontShadecolor: "white",
		qcmpcolor: "rgb(127,127,127)",
		bgcellcolor_func: "light",

		lightcolor: "rgb(192, 255, 127)",

		paint: function() {
			this.drawBGCells();
			this.drawGrid();
			this.drawQuesCells();
			this.drawQuesNumbers();

			this.drawAkari();
			this.drawDotCells();

			this.drawChassis();

			this.drawTarget();
		},

		getBGCellColor: function(cell) {
			if (cell.qnum === -1) {
				if (cell.error === 1) {
					return this.errbcolor1;
				} else if (cell.qlight === 1 && this.puzzle.execConfig("autocmp")) {
					return this.lightcolor;
				}
			}
			return null;
		},
		drawAkari: function() {
			var g = this.vinc("cell_akari", "auto");

			var rsize = this.cw * 0.4;
			var lampcolor = "rgb(0, 127, 96)";
			var clist = this.range.cells;
			for (var i = 0; i < clist.length; i++) {
				var cell = clist[i];
				g.vid = "c_AK_" + cell.id;
				if (cell.isAkari()) {
					g.fillStyle =
						cell.error === 4
							? this.errcolor1
							: !cell.trial
							? lampcolor
							: this.trialcolor;
					g.fillCircle(cell.bx * this.bw, cell.by * this.bh, rsize);
				} else {
					g.vhide();
				}
			}
		},
		getQuesNumberColor: function(cell) {
			return cell.qcmp === 1 ? this.qcmpcolor : this.fontShadecolor;
		}
	},

	//---------------------------------------------------------
	// URLエンコード/デコード処理
	Encode: {
		decodePzpr: function(type) {
			this.decode4Cell();
		},
		encodePzpr: function(type) {
			this.encode4Cell();
		}
	},
	//---------------------------------------------------------
	FileIO: {
		decodeData: function() {
			this.decodeCellQnumAns();
			this.decodeCellQcmp();
		},
		encodeData: function() {
			this.encodeCellQnumAns();
			this.encodeCellQcmp();
		},

		decodeCellQcmp: function() {
			this.decodeCell(function(cell, ca) {
				if (ca === "-") {
					cell.qcmp = 1;
				}
			});
		},
		encodeCellQcmp: function() {
			if (
				!this.puzzle.board.cell.some(function(cell) {
					return cell.qcmp === 1;
				})
			) {
				return;
			}
			this.encodeCell(function(cell) {
				if (cell.qcmp === 1) {
					return "- ";
				} else {
					return ". ";
				}
			});
		}
	},

	//---------------------------------------------------------
	// 正解判定処理実行部
	AnsCheck: {
		checklist: [
			"checkDiag4Akari",
			"checkOrthAdjacentAkari",
			"checkShinedCell"
		],

		/* Diagonal wall counting: numbered wall must have exactly N bulbs
		   among its 4 diagonal neighbours */
		checkDiag4Akari: function() {
			var bd = this.board;
			var dirs = [
				[-2, -2],
				[-2, 2],
				[2, -2],
				[2, 2]
			];
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				if (cell.qnum < 0) {
					continue;
				}
				var cnt = 0;
				for (var d = 0; d < dirs.length; d++) {
					var cell2 = bd.getc(cell.bx + dirs[d][0], cell.by + dirs[d][1]);
					if (!cell2.isnull && cell2.isAkari()) {
						cnt++;
					}
				}
				if (cnt !== cell.qnum) {
					cell.seterr(1);
					return;
				}
			}
		},

		/* No two bulbs may be orthogonally adjacent */
		checkOrthAdjacentAkari: function() {
			var bd = this.board;
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				if (!cell.isAkari()) {
					continue;
				}
				var dirs = [
					[2, 0],
					[0, 2]
				]; /* only right & down to avoid double-count */
				for (var d = 0; d < dirs.length; d++) {
					var cell2 = bd.getc(cell.bx + dirs[d][0], cell.by + dirs[d][1]);
					if (!cell2.isnull && cell2.isAkari()) {
						cell.seterr(4);
						cell2.seterr(4);
						return;
					}
				}
			}
		},

		checkShinedCell: function() {
			this.checkAllCell(function(cell) {
				return cell.noNum() && !cell.isAkari() && cell.qlight !== 1;
			}, "ceDark");
		}
	}
});
