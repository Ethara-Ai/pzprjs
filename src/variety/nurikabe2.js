//
// nurikabe2.js
//
(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["nurikabe2"], {
	//---------------------------------------------------------
	// Mouse input
	MouseEvent: {
		use: true,
		inputModes: {
			edit: ["number", "clear", "info-blk"],
			play: ["shade", "unshade", "info-blk"]
		},
		autoedit_func: "qnum",
		autoplay_func: "cell"
	},

	//---------------------------------------------------------
	// Keyboard input
	KeyEvent: {
		enablemake: true
	},

	//---------------------------------------------------------
	// Board management
	Cell: {
		numberRemainsUnshaded: true,
		maxnum: function() {
			return this.board.cols * this.board.rows;
		}
	},

	AreaShadeGraph: {
		enabled: true,
		coloring: true
	},
	AreaUnshadeGraph: {
		enabled: true
	},

	//---------------------------------------------------------
	// Graphics
	Graphic: {
		numbercolor_func: "qnum",
		qanscolor: "black",
		irowakeblk: true,

		paint: function() {
			this.drawBGCells();
			this.drawShadedCells();
			this.drawDotCells();
			this.drawGrid();
			this.drawQuesNumbers();
			this.drawChassis();
			this.drawTarget();
		}
	},

	//---------------------------------------------------------
	// URL encode/decode
	Encode: {
		decodePzpr: function(type) {
			this.decodeNumber16();
		},
		encodePzpr: function(type) {
			this.encodeNumber16();
		}
	},

	//---------------------------------------------------------
	// File I/O
	FileIO: {
		decodeData: function() {
			this.decodeCellQnumAns();
		},
		encodeData: function() {
			this.encodeCellQnumAns();
		}
	},

	//---------------------------------------------------------
	// Answer checking
	AnsCheck: {
		checklist: [
			"check2x2UnshadedCell",
			"checkShadeDomino",
			"checkNoNumberInUnshade",
			"checkDoubleNumberInUnshade",
			"checkNumberAndUnshadeSize",
			"doneShadingDecided"
		],

		// Rule 1: No 2x2 block of unshaded cells
		check2x2UnshadedCell: function() {
			var bd = this.board;
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				if (cell.bx >= bd.maxbx - 1 || cell.by >= bd.maxby - 1) {
					continue;
				}
				var adc = cell.adjacent;
				if (
					cell.isUnshade() &&
					adc.right.isUnshade() &&
					adc.bottom.isUnshade() &&
					adc.right.adjacent.bottom.isUnshade()
				) {
					this.failcode.add("cu2x2");
					if (this.checkOnly) {
						break;
					}
					cell.seterr(1);
					adc.right.seterr(1);
					adc.bottom.seterr(1);
					adc.right.adjacent.bottom.seterr(1);
				}
			}
		},

		// Rule 2: Every shaded group must have exactly 2 cells (domino)
		checkShadeDomino: function() {
			this.checkAllArea(
				this.board.sblkmgr,
				function(w, h, a, n) {
					return a === 2;
				},
				"csNotDomino"
			);
		},

		// Rule 3: All shaded cells must be connected (uses built-in checkConnectShade)

		// Standard: Each island must contain at least one number
		checkNoNumberInUnshade: function() {
			this.checkAllBlock(
				this.board.ublkmgr,
				function(cell) {
					return cell.isNum();
				},
				function(w, h, a, n) {
					return a !== 0;
				},
				"bkNoNum"
			);
		},

		// Standard: No island with two or more numbers
		checkDoubleNumberInUnshade: function() {
			this.checkAllBlock(
				this.board.ublkmgr,
				function(cell) {
					return cell.isNum();
				},
				function(w, h, a, n) {
					return a < 2;
				},
				"bkNumGe2"
			);
		},

		// Standard: Island size must match the clue number
		checkNumberAndUnshadeSize: function() {
			this.checkAllCell(function(cell) {
				if (!cell.isValidNum()) {
					return false;
				}
				if (!cell.ublk) {
					return true;
				}
				if (cell.ublk.clist.length !== cell.getNum()) {
					cell.ublk.clist.seterr(1);
					return true;
				}
				return false;
			}, "bkSizeNe");
		}
	},

	//---------------------------------------------------------
	// Fail codes for error messages
	FailCode: {
		cu2x2: [
			"2x2 block of unshaded cells found.",
			"白マスの2x2ブロックがあります。"
		],
		csNotDomino: [
			"A shaded group is not a domino (must be exactly 2 cells).",
			"黒マスのグループがドミノではありません（2マスにしてください）。"
		]
	}
});
