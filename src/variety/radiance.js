//
// パズル固有スクリプト部 光線版 radiance.js
//
(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["radiance"], {
	//---------------------------------------------------------
	// マウス入力系
	MouseEvent: {
		use: true,
		inputModes: {
			edit: ["number", "direc", "clear"],
			play: ["slash", "unshade"]
		},
		mouseinput_auto: function() {
			if (this.puzzle.playmode) {
				if (this.mousestart || this.mousemove) {
					this.inputslash();
				} else if (this.mouseend && this.notInputted()) {
					this.clickslash();
				}
			} else if (this.puzzle.editmode) {
				if (this.mousestart || this.mousemove) {
					this.inputdirec();
				} else if (this.mouseend && this.notInputted()) {
					this.inputqnum();
				}
			}
		},
		mouseinput_other: function() {
			if (this.inputMode === "slash") {
				if (this.mousestart || this.mousemove) {
					this.inputslash();
				} else if (this.mouseend && this.notInputted()) {
					this.clickslash();
				}
			}
		},

		inputslash: function() {
			var cell = this.getcell();
			if (cell.isnull || cell.isEmitter()) {
				return;
			}

			if (this.mouseCell !== cell) {
				this.firstPoint.set(this.inputPoint);
			} else if (this.firstPoint.bx !== null) {
				var val = null,
					dx = this.inputPoint.bx - this.firstPoint.bx,
					dy = this.inputPoint.by - this.firstPoint.by;
				if (dx * dy > 0 && Math.abs(dx) >= 0.5 && Math.abs(dy) >= 0.5) {
					val = 31;
				} else if (
					dx * dy < 0 &&
					Math.abs(dx) >= 0.5 &&
					Math.abs(dy) >= 0.5
				) {
					val = 32;
				}

				if (val !== null) {
					if (this.inputData === null) {
						if (val === cell.qans) {
							val = 0;
						}
						this.inputData = +(val > 0);
					} else if (this.inputData === 0) {
						if (val === cell.qans) {
							val = 0;
						} else {
							val = null;
						}
					}
					if (val !== null) {
						cell.setQans(val);
						cell.draw();
					}
					this.firstPoint.reset();
				}
			}

			this.mouseCell = cell;
		},
		clickslash: function() {
			var cell = this.getcell();
			if (cell.isnull || cell.isEmitter()) {
				return;
			}

			var qa = cell.qans;
			cell.setQans(
				(this.btn === "left"
					? { 0: 31, 31: 32, 32: 0 }
					: { 0: 32, 31: 0, 32: 31 })[qa]
			);

			cell.draw();
		}
	},

	//---------------------------------------------------------
	// キーボード入力系
	KeyEvent: {
		enablemake: true,
		moveTarget: function(ca) {
			if (ca.match(/shift/)) {
				return false;
			}
			return this.moveTCell(ca);
		},

		keyinput: function(ca) {
			if (this.key_inputdirec(ca)) {
				return;
			}
			this.key_inputqnum(ca);
		}
	},

	//---------------------------------------------------------
	// 盤面管理系
	Cell: {
		minnum: 1,
		maxnum: function() {
			return (this.board.cols + this.board.rows) * 2;
		},

		isEmitter: function() {
			return this.qnum !== -1 && this.qdir !== 0;
		},

		noLP: function() {
			return this.isEmitter();
		}
	},
	Board: {
		cols: 7,
		rows: 7,
		disable_subclear: true
	},
	BoardExec: {
		adjustBoardData: function(key, d) {
			if (key & this.TURNFLIP) {
				var clist = this.board.cell;
				for (var i = 0; i < clist.length; i++) {
					var cell = clist[i];
					cell.qans = { 0: 0, 31: 32, 32: 31 }[cell.qans] || 0;
				}
			}
			this.adjustNumberArrow(key, d);
		}
	},

	//---------------------------------------------------------
	// 画像表示系
	Graphic: {
		gridcolor_type: "DLIGHT",
		numbercolor_func: "fixed",
		errcolor1: "red",
		errbcolor1: "rgb(255, 192, 192)",

		paint: function() {
			this.drawBGCells();
			this.drawGrid();

			this.drawSlashes();
			this.drawEmitterCells();
			this.drawArrowNumbers();

			this.drawChassis();
			this.drawTarget();
		},

		getBGCellColor: function(cell) {
			if (cell.error === 1) {
				return this.errbcolor1;
			}
			return null;
		},

		drawEmitterCells: function() {
			var g = this.vinc("cell_emitter", "auto");

			var clist = this.range.cells;
			for (var i = 0; i < clist.length; i++) {
				var cell = clist[i];
				g.vid = "c_emit_" + cell.id;
				if (cell.isEmitter()) {
					var px = cell.bx * this.bw,
						py = cell.by * this.bh;
					g.fillStyle = cell.error === 1
						? this.errcolor1
						: "rgb(32, 32, 32)";
					g.fillRect(px - this.bw + 1, py - this.bh + 1, this.cw - 2, this.ch - 2);
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
			this.decodeArrowNumber16();
		},
		encodePzpr: function(type) {
			this.encodeArrowNumber16();
		}
	},
	//---------------------------------------------------------
	FileIO: {
		decodeData: function() {
			this.decodeCellDirecQnum();
			this.decodeCell(function(cell, ca) {
				if (ca === "1") {
					cell.qans = 31;
				} else if (ca === "2") {
					cell.qans = 32;
				}
			});
		},
		encodeData: function() {
			this.encodeCellDirecQnum();
			this.encodeCell(function(cell) {
				if (cell.qans === 31) {
					return "1 ";
				} else if (cell.qans === 32) {
					return "2 ";
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
			"checkBeamLengths",
			"checkNoCrossBeams",
			"checkFullCoverage",
			"checkUnusedMirrors"
		],

		// Beam deflection: traces from emitter through cells, bouncing off at most one mirror
		traceBeam: function(emitter) {
			var dir = emitter.qdir; // UP=1, DN=2, LT=3, RT=4
			var cells = [];
			var pos = emitter.getaddr();
			var bounced = false;

			while (true) {
				pos.movedir(dir, 2);
				var cell = pos.getc();

				if (cell.isnull || cell.isEmitter()) {
					break;
				}

				if (cell.qans === 31 || cell.qans === 32) {
					if (bounced) {
						break;
					}
					cells.push(cell);
					bounced = true;

					// Forward slash: RT<->UP, LT<->DN
					if (cell.qans === 31) {
						if (dir === 4) { dir = 1; }
						else if (dir === 1) { dir = 4; }
						else if (dir === 3) { dir = 2; }
						else if (dir === 2) { dir = 3; }
					}
					// Backslash: RT<->DN, LT<->UP
					else if (cell.qans === 32) {
						if (dir === 4) { dir = 2; }
						else if (dir === 2) { dir = 4; }
						else if (dir === 3) { dir = 1; }
						else if (dir === 1) { dir = 3; }
					}
				} else {
					cells.push(cell);
				}
			}
			return cells;
		},

		getEmitters: function() {
			var emitters = [];
			var bd = this.board;
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				if (cell.isEmitter()) {
					emitters.push(cell);
				}
			}
			return emitters;
		},

		checkBeamLengths: function() {
			var emitters = this.getEmitters();
			for (var i = 0; i < emitters.length; i++) {
				var emitter = emitters[i];
				var beamCells = this.traceBeam(emitter);
				if (beamCells.length !== emitter.qnum) {
					this.failcode.add("bkLenNe");
					if (this.checkOnly) {
						break;
					}
					emitter.seterr(1);
					for (var j = 0; j < beamCells.length; j++) {
						beamCells[j].seterr(1);
					}
				}
			}
		},

		checkNoCrossBeams: function() {
			var emitters = this.getEmitters();
			var illuminated = {};

			for (var i = 0; i < emitters.length; i++) {
				var beamCells = this.traceBeam(emitters[i]);
				for (var j = 0; j < beamCells.length; j++) {
					var cell = beamCells[j];
					if (illuminated[cell.id]) {
						this.failcode.add("cuDouble");
						if (this.checkOnly) {
							return;
						}
						cell.seterr(1);
					}
					illuminated[cell.id] = true;
				}
			}
		},

		checkFullCoverage: function() {
			var emitters = this.getEmitters();
			var illuminated = {};

			for (var i = 0; i < emitters.length; i++) {
				var beamCells = this.traceBeam(emitters[i]);
				for (var j = 0; j < beamCells.length; j++) {
					illuminated[beamCells[j].id] = true;
				}
			}

			var bd = this.board;
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				if (cell.isEmitter()) {
					continue;
				}
				if (!illuminated[cell.id]) {
					this.failcode.add("cuNoBeam");
					if (this.checkOnly) {
						break;
					}
					cell.seterr(1);
				}
			}
		},

		checkUnusedMirrors: function() {
			var emitters = this.getEmitters();
			var illuminated = {};

			for (var i = 0; i < emitters.length; i++) {
				var beamCells = this.traceBeam(emitters[i]);
				for (var j = 0; j < beamCells.length; j++) {
					illuminated[beamCells[j].id] = true;
				}
			}

			var bd = this.board;
			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				if ((cell.qans === 31 || cell.qans === 32) && !illuminated[cell.id]) {
					this.failcode.add("mrUnused");
					if (this.checkOnly) {
						break;
					}
					cell.seterr(1);
				}
			}
		}
	},

	FailCode: {
		bkLenNe: "bkLenNe.radiance",
		cuDouble: "cuDouble.radiance",
		cuNoBeam: "cuNoBeam.radiance",
		mrUnused: "mrUnused.radiance"
	}
});
