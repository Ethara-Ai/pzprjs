//
// パズル固有スクリプト部 ペアループ版 pairloop.js
//
// Pairloop Rules:
// 1. Draw a single closed loop along cell borders (Slitherlink-style dot grid).
// 2. Number clues (0-4): exactly that many of the cell's 4 borders are loop segments.
// 3. Arrow clues (↑↓←→): At least 2 consecutive loop segments extend in that direction —
//    this cell's border in the arrow direction AND the adjacent cell's border in that
//    direction are both loop segments.
//
// Cell encoding: qnum 0-4 = number clues, 5=↑, 6=→, 7=↓, 8=← (arrow clues)
//
(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["pairloop"], {
	//---------------------------------------------------------
	// マウス入力系
	MouseEvent: {
		inputModes: {
			edit: ["number", "clear", "info-line"],
			play: [
				"line",
				"peke",
				"bgcolor",
				"bgcolor1",
				"bgcolor2",
				"clear",
				"info-line"
			]
		},
		mouseinput_auto: function() {
			var puzzle = this.puzzle;
			if (puzzle.playmode) {
				if (this.checkInputBGcolor()) {
					this.inputBGcolor();
				} else if (this.btn === "left") {
					if (this.mousestart || this.mousemove) {
						this.inputLine();
					} else if (this.mouseend && this.notInputted()) {
						this.prevPos.reset();
						this.inputpeke();
					}
				} else if (this.btn === "right") {
					if (this.mousestart || this.mousemove) {
						this.inputpeke();
					}
				}
			} else if (puzzle.editmode) {
				if (this.mousestart) {
					this.inputqnum();
				}
			}
		},
		checkInputBGcolor: function() {
			var inputbg = this.puzzle.execConfig("bgcolor");
			if (inputbg) {
				if (this.mousestart) {
					inputbg = this.getpos(0.25).oncell();
				} else if (this.mousemove) {
					inputbg = this.inputData >= 10;
				} else {
					inputbg = false;
				}
			}
			return inputbg;
		}
	},

	//---------------------------------------------------------
	// キーボード入力系
	KeyEvent: {
		enablemake: true,

		keyinput: function(ca) {
			if (ca === "q" || ca === "w" || ca === "e" || ca === "r") {
				// q=up(5), w=right(6), e=down(7), r=left(8)
				var cell = this.cursor.getc();
				if (!cell.isnull) {
					var arrowMap = { q: 5, w: 6, e: 7, r: 8 };
					if (cell.qnum === arrowMap[ca]) {
						cell.setQnum(-1);
					} else {
						cell.setQnum(arrowMap[ca]);
					}
					cell.draw();
				}
			} else {
				this.key_inputqnum(ca);
			}
		}
	},

	//---------------------------------------------------------
	// 盤面管理系
	Cell: {
		maxnum: 8,
		minnum: 0,

		// Count how many of the cell's 4 borders are loop lines
		getdir4BorderLine1: function() {
			var adb = this.adjborder,
				cnt = 0;
			if (adb.top.isLine()) {
				cnt++;
			}
			if (adb.bottom.isLine()) {
				cnt++;
			}
			if (adb.left.isLine()) {
				cnt++;
			}
			if (adb.right.isLine()) {
				cnt++;
			}
			return cnt;
		},

		// Check if the border in a given direction is a line
		isBorderLine: function(dir) {
			var adb = this.adjborder;
			switch (dir) {
				case 5:
					return adb.top.isLine(); // up
				case 6:
					return adb.right.isLine(); // right
				case 7:
					return adb.bottom.isLine(); // down
				case 8:
					return adb.left.isLine(); // left
			}
			return false;
		},

		// Get the adjacent cell in a given direction
		getAdjacentCell: function(dir) {
			var adj = this.adjacent;
			switch (dir) {
				case 5:
					return adj.top; // up
				case 6:
					return adj.right; // right
				case 7:
					return adj.bottom; // down
				case 8:
					return adj.left; // left
			}
			return this.board.emptycell;
		}
	},

	Board: {
		hasborder: 2,
		borderAsLine: true
	},

	LineGraph: {
		enabled: true
	},

	//---------------------------------------------------------
	// 画像表示系
	Graphic: {
		irowake: true,
		bgcellcolor_func: "qsub2",
		numbercolor_func: "qnum",
		margin: 0.5,

		paint: function() {
			this.drawBGCells();
			this.drawLines();
			this.drawBaseMarks();
			this.drawCrossErrors();
			this.drawPairloopClues();
			this.drawPekes();
			this.drawTarget();
		},

		repaintParts: function(blist) {
			this.range.crosses = blist.crossinside();
			this.drawBaseMarks();
		},

		drawPairloopClues: function() {
			var g = this.vinc("cell_clues", "auto");
			var clist = this.range.cells;
			for (var i = 0; i < clist.length; i++) {
				var cell = clist[i];
				var qn = cell.qnum;
				var px = cell.bx * this.bw;
				var py = cell.by * this.bh;

				// Draw number clues (0-4)
				g.vid = "cell_text_" + cell.id;
				if (qn >= 0 && qn <= 4) {
					g.fillStyle = this.getQuesNumberColor(cell);
					g.font = this.fontsizeratio + "em " + this.fontfamily;
					g.fillText(qn.toString(), px, py);
				}
				// Draw arrow clues (5-8)
				else if (qn >= 5 && qn <= 8) {
					this.drawArrowClue(g, cell, qn, px, py);
				} else {
					g.vhide();
				}
			}
		},

		drawArrowClue: function(g, cell, qn, px, py) {
			var al = this.cw * 0.35; // Arrow length
			var aw = this.cw * 0.08; // Arrow shaft width
			var tw = this.cw * 0.15; // Arrowhead width
			var tl = this.cw * 0.12; // Arrowhead length

			g.fillStyle = this.getQuesNumberColor(cell);
			g.beginPath();

			switch (qn) {
				case 5: // Up arrow ↑
					g.setOffsetLinePath(
						px,
						py,
						0,
						-al,
						-tw,
						-al + tl,
						-aw,
						-al + tl,
						-aw,
						al,
						aw,
						al,
						aw,
						-al + tl,
						tw,
						-al + tl,
						true
					);
					break;
				case 6: // Right arrow →
					g.setOffsetLinePath(
						px,
						py,
						al,
						0,
						al - tl,
						-tw,
						al - tl,
						-aw,
						-al,
						-aw,
						-al,
						aw,
						al - tl,
						aw,
						al - tl,
						tw,
						true
					);
					break;
				case 7: // Down arrow ↓
					g.setOffsetLinePath(
						px,
						py,
						0,
						al,
						-tw,
						al - tl,
						-aw,
						al - tl,
						-aw,
						-al,
						aw,
						-al,
						aw,
						al - tl,
						tw,
						al - tl,
						true
					);
					break;
				case 8: // Left arrow ←
					g.setOffsetLinePath(
						px,
						py,
						-al,
						0,
						-al + tl,
						-tw,
						-al + tl,
						-aw,
						al,
						-aw,
						al,
						aw,
						-al + tl,
						aw,
						-al + tl,
						tw,
						true
					);
					break;
			}
			g.fill();
		}
	},

	//---------------------------------------------------------
	// URLエンコード/デコード処理
	Encode: {
		decodePzpr: function(type) {
			this.decodePairloop();
		},
		encodePzpr: function(type) {
			this.encodePairloop();
		},

		// Custom encoding: values 0-8 in a single hex digit per cell
		// 0-4 = number clue, 5-8 = arrow (up/right/down/left)
		// 'g'-'z' = skip 1-20 empty cells
		decodePairloop: function() {
			var c = 0,
				i = 0,
				bstr = this.outbstr,
				bd = this.board;
			for (i = 0; i < bstr.length; i++) {
				var cell = bd.cell[c],
					ca = bstr.charAt(i);
				if (this.include(ca, "0", "8")) {
					cell.qnum = parseInt(ca, 10);
				} else if (this.include(ca, "g", "z")) {
					c += parseInt(ca, 36) - 16;
				}

				c++;
				if (!bd.cell[c]) {
					break;
				}
			}
			this.outbstr = bstr.substr(i + 1);
		},
		encodePairloop: function() {
			var count = 0,
				cm = "",
				bd = this.board;
			for (var c = 0; c < bd.cell.length; c++) {
				var pstr = "",
					qn = bd.cell[c].qnum;

				if (qn >= 0 && qn <= 8) {
					pstr = qn.toString(10);
				} else {
					count++;
				}

				if (count === 0) {
					cm += pstr;
				} else if (pstr || count === 20) {
					cm += (count + 15).toString(36) + pstr;
					count = 0;
				}
			}
			if (count > 0) {
				cm += (count + 15).toString(36);
			}

			this.outbstr += cm;
		}
	},

	//---------------------------------------------------------
	FileIO: {
		decodeData: function() {
			this.decodeCellQnum();
			this.decodeBorderLine();
		},
		encodeData: function() {
			this.encodeCellQnum();
			this.encodeBorderLine();
		}
	},

	//---------------------------------------------------------
	// 正解判定処理実行部
	AnsCheck: {
		checklist: [
			"checkLineExist+",
			"checkBranchLine",
			"checkCrossLine",
			"checkdir4BorderLine",
			"checkArrowExtendedReach",
			"checkOneLoop",
			"checkDeadendLine+"
		],

		// Check number clues (0-4): border line count must match
		checkdir4BorderLine: function() {
			this.checkAllCell(function(cell) {
				return (
					cell.qnum >= 0 &&
					cell.qnum <= 4 &&
					cell.getdir4BorderLine1() !== cell.qnum
				);
			}, "nmLineNe");
		},

		// Check arrow clues (5-8): extended reach — this cell's border
		// in the arrow direction AND the next cell's border in the same
		// direction must both be loop segments
		checkArrowExtendedReach: function() {
			this.checkAllCell(function(cell) {
				var qn = cell.qnum;
				if (qn < 5 || qn > 8) {
					return false;
				}

				// This cell's border in arrow direction must be a line
				if (!cell.isBorderLine(qn)) {
					return true; // fail
				}

				// Adjacent cell in arrow direction must also have its
				// border in the same direction as a line
				var neighbor = cell.getAdjacentCell(qn);
				if (neighbor.isnull) {
					return true; // fail — no neighbor means can't extend
				}
				if (!neighbor.isBorderLine(qn)) {
					return true; // fail
				}

				return false; // pass
			}, "arExtReach");
		}
	}
});
