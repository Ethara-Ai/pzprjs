(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["lits2"], {
	MouseEvent: {
		use: true,
		inputModes: {
			edit: ["border", "info-blk"],
			play: ["shade", "unshade", "info-blk"]
		},
		mouseinput_auto: function() {
			if (this.puzzle.playmode) {
				if (this.mousestart || this.mousemove) {
					this.inputcell();
				}
			} else if (this.puzzle.editmode) {
				if (this.mousestart || this.mousemove) {
					this.inputborder();
				}
			}
		}
	},

	Cell: {
		posthook: {
			qans: function() {
				this.room.checkAutoCmp();
			}
		}
	},
	Board: {
		hasborder: 1
	},
	CellList: {
		checkCmp: function() {
			var scnt = 0,
				sblk = null;
			for (var i = 0; i < this.length; i++) {
				if (this[i].qans === 1) {
					scnt++;
					if (!sblk) {
						sblk = this[i].sblk;
					} else if (sblk !== this[i].sblk) {
						return false;
					}
				}
			}
			return scnt === 3;
		}
	},

	AreaShadeGraph: {
		enabled: true
	},
	AreaRoomGraph: {
		enabled: true
	},

	Graphic: {
		autocmp: "room",
		gridcolor_type: "DARK",
		qanscolor: "rgb(96, 96, 96)",
		shadecolor: "rgb(96, 96, 96)",
		qcmpbgcolor: "rgb(96, 255, 160)",
		errbcolor2: "rgb(192, 192, 255)",

		getBGCellColor: function(cell) {
			if (cell.error === 2 || cell.qinfo === 2) {
				return this.errbcolor2;
			}
			return this.getBGCellColor_qcmp(cell);
		},

		paint: function() {
			this.drawBGCells();
			this.drawShadedCells();
			this.drawDotCells();
			this.drawGrid();
			this.drawBorders();
			this.drawChassis();
		}
	},

	Encode: {
		decodePzpr: function() {
			this.decodeBorder();
		},
		encodePzpr: function() {
			this.outpflag = "";
			this.encodeBorder();
		}
	},
	FileIO: {
		decodeData: function() {
			this.decodeBorderQues();
			this.decodeCellAns();
		},
		encodeData: function() {
			this.filever = 1;
			this.encodeBorderQues();
			this.encodeCellAns();
		}
	},

	AnsCheck: {
		checklist: [
			"check2x2ShadeCell",
			"checkOverShadeCellInArea",
			"checkSeqBlocksInRoom",
			"checkConnectShade",
			"checkNoShadeCellInArea",
			"checkLessShadeCellInArea"
		],

		checkOverShadeCellInArea: function() {
			this.checkAllBlock(
				this.board.roommgr,
				function(cell) {
					return cell.isShade();
				},
				function(w, h, a, n) {
					return a <= 3;
				},
				"bkShadeGt3"
			);
		},
		checkLessShadeCellInArea: function() {
			this.checkAllBlock(
				this.board.roommgr,
				function(cell) {
					return cell.isShade();
				},
				function(w, h, a, n) {
					return a >= 3;
				},
				"bkShadeLt3"
			);
		},

		checkSeqBlocksInRoom: function() {
			var bd = this.board,
				rooms = bd.roommgr.components;
			for (var r = 0; r < rooms.length; r++) {
				var clist = rooms[r].clist,
					sblkbase = null,
					check = true;
				for (var i = 0; i < clist.length; i++) {
					if (clist[i].qans !== 1) {
						continue;
					}
					var sblk = clist[i].sblk;
					if (sblk === null) {
						continue;
					}
					if (sblkbase === null) {
						sblkbase = sblk;
					} else if (sblk !== sblkbase) {
						check = false;
						break;
					}
				}
				if (check) {
					continue;
				}
				this.failcode.add("bkShadeDivide");
				if (this.checkOnly) {
					break;
				}
				clist.seterr(1);
			}
		}
	}
});
