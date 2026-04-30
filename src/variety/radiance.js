

(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["radiance"], {

	MouseEvent: {
		use: true,
		inputModes: {
			edit: ["objplace", "clear"],
			play: ["info-line"]
		},

		mouseinput_auto: function() {
			if (this.puzzle.playmode) {
				if (this.mousestart || this.mousemove) {
					this.inputMirror();
				} else if (this.mouseend && this.notInputted()) {
					this.clickMirror();
				}
			} else if (this.puzzle.editmode) {
				if (this.mousestart) {
					this.inputEditCell();
				}
			}
		},

	
		inputEditCell: function() {
			var cell = this.getcell();
			if (cell.isnull) { return; }

			var current = cell.ques;
			var next;
			if (this.btn === "left") {
				next = (current === 0) ? 1 : (current === 1) ? 2 : (current === 2) ? 3 : 0;
			} else {
				next = (current === 0) ? 3 : (current === 3) ? 2 : (current === 2) ? 1 : 0;
			}

			if (next === 0) {
				cell.setQues(0);
				cell.setQdir(0);
				cell.setQans(0);
			} else if (next === 1) {
				cell.setQues(1);
				cell.setQdir(4);
				cell.setQans(0);
			} else if (next === 2) {
				cell.setQues(2);
				cell.setQdir(0);
				cell.setQans(0);
			} else if (next === 3) {
				cell.setQues(3);
				cell.setQdir(0);
				cell.setQans(0);
			}
			cell.draw();
		},

		inputMirror: function() {
			var cell = this.getcell();
			if (cell.isnull || cell.ques !== 3) { return; }

			if (this.mouseCell !== cell) {
				this.firstPoint.set(this.inputPoint);
			} else if (this.firstPoint.bx !== null) {
				var dx = this.inputPoint.bx - this.firstPoint.bx;
				var dy = this.inputPoint.by - this.firstPoint.by;
				var val = null;

				if (dx * dy > 0 && Math.abs(dx) >= 0.5 && Math.abs(dy) >= 0.5) {
					val = 31;
				} else if (dx * dy < 0 && Math.abs(dx) >= 0.5 && Math.abs(dy) >= 0.5) {
					val = 32;
				}

				if (val !== null) {
					if (this.inputData === null) {
						if (val === cell.qans) { val = 0; }
						this.inputData = +(val > 0);
					} else if (this.inputData === 0) {
						if (val === cell.qans) { val = 0; } else { val = null; }
					}

					if (val !== null && cell.qans !== val) {
						cell.setQans(val);
						this.puzzle.redraw();
					}
					this.firstPoint.reset();
				}
			}
			this.mouseCell = cell;
		},


		clickMirror: function() {
			var cell = this.getcell();
			if (cell.isnull || cell.ques !== 3) { return; }

			var current = cell.qans;
			var next;
			if (this.btn === "left") {
				next = (current === 0) ? 31 : (current === 31) ? 32 : 0;
			} else {
				next = (current === 0) ? 32 : (current === 32) ? 31 : 0;
			}
			cell.setQans(next);
			this.puzzle.redraw();
		}
	},


	KeyEvent: {
		enablemake: true,

		keyinput: function(ca) {
			if (this.keydown && this.puzzle.editmode) {
				this.key_inputRadiance(ca);
			}
		},

		key_inputRadiance: function(ca) {
			var cell = this.cursor.getc();
			if (cell.ques !== 1) { return; }

			var dir = 0;
			if (ca === "up") { dir = 1; }
			else if (ca === "down") { dir = 2; }
			else if (ca === "left") { dir = 3; }
			else if (ca === "right") { dir = 4; }

			if (dir > 0) {
				cell.setQdir(dir);
				cell.draw();
			}
		}
	},

	Cell: {
		isEmitter: function() {
			return this.ques === 1;
		},

		isTarget: function() {
			return this.ques === 2;
		},

		isMirrorSlot: function() {
			return this.ques === 3;
		},

		hasMirror: function() {
			return this.qans === 31 || this.qans === 32;
		},

		noLP: function() {
			return this.ques === 1 || this.ques === 2;
		}
	},


	Board: {
		cols: 8,
		rows: 8,
		disable_subclear: true
	},


	BoardExec: {
		adjustBoardData: function(key, d) {
			if (key & this.TURNFLIP) {
				var clist = this.board.cell;
				for (var i = 0; i < clist.length; i++) {
					var cell = clist[i];
					if (cell.qans === 31) {
						cell.qans = 32;
					} else if (cell.qans === 32) {
						cell.qans = 31;
					}
				}
			}
			this.adjustNumberArrow(key, d);
		}
	},


	Graphic: {
		hideHatena: true,

		paint: function() {
			this.drawBGCells();
			this.drawGrid();
			this.drawBeamPath();
			this.drawSlashes();
			this.drawSpecialCells();
			this.drawChassis();
			this.drawTarget();
		},

		drawSpecialCells: function() {
			var g = this.vinc("cell_special", "crz", true);
			var clist = this.range.cells;
			for (var i = 0; i < clist.length; i++) {
				var cell = clist[i];
				g.vid = "c_sp_" + cell.id;

				if (cell.isEmitter()) {
					var ecolor = (cell.error || cell.qinfo) ? this.errbcolor1 : "rgb(51,51,51)";
					g.fillStyle = ecolor;
					var px = cell.bx * this.bw;
					var py = cell.by * this.bh;
					var w = this.bw * 0.9;
					var h = this.bh * 0.9;
					g.fillRect(px - w, py - h, 2 * w, 2 * h);
					this.drawArrowOnCell(g, cell, px, py);
				} else if (cell.isTarget()) {
					var tcolor = (cell.error || cell.qinfo) ? this.errbcolor1 : "rgb(220,50,50)";
					g.fillStyle = tcolor;
					var tpx = cell.bx * this.bw;
					var tpy = cell.by * this.bh;
					var tr = this.bw * 0.45;
					g.beginPath();
					g.arc(tpx, tpy, tr, 0, 2 * Math.PI, false);
					g.fill();
					g.fillStyle = "white";
					g.beginPath();
					g.arc(tpx, tpy, tr * 0.5, 0, 2 * Math.PI, false);
					g.fill();
				} else if (cell.isMirrorSlot() && !cell.hasMirror()) {
					var spx = cell.bx * this.bw;
					var spy = cell.by * this.bh;
					var sr = this.bw * 0.35;
					var scolor = (cell.error || cell.qinfo) ? this.errbcolor1 : "rgb(180,180,180)";
					g.fillStyle = scolor;
					g.beginPath();
					g.moveTo(spx, spy - sr);
					g.lineTo(spx + sr, spy);
					g.lineTo(spx, spy + sr);
					g.lineTo(spx - sr, spy);
					g.closePath();
					g.fill();
				} else {
					g.vhide();
				}
			}
		},

		drawArrowOnCell: function(g, cell, px, py) {
			var dir = cell.qdir;
			if (dir === 0) { return; }

			g.strokeStyle = "white";
			g.fillStyle = "white";
			g.lineWidth = Math.max(1, this.bw * 0.1) | 0;

			var len = this.bw * 0.55;
			var head = this.bw * 0.25;
			var dx = 0;
			var dy = 0;

			if (dir === 1) { dy = -1; }
			else if (dir === 2) { dy = 1; }
			else if (dir === 3) { dx = -1; }
			else if (dir === 4) { dx = 1; }

			g.beginPath();
			g.moveTo(px - dx * len * 0.5, py - dy * len * 0.5);
			g.lineTo(px + dx * len * 0.5, py + dy * len * 0.5);
			g.stroke();

			var tipX = px + dx * len * 0.5;
			var tipY = py + dy * len * 0.5;
			g.beginPath();
			g.moveTo(tipX, tipY);
			if (dx !== 0) {
				g.lineTo(tipX - dx * head, tipY - head * 0.5);
				g.lineTo(tipX - dx * head, tipY + head * 0.5);
			} else {
				g.lineTo(tipX - head * 0.5, tipY - dy * head);
				g.lineTo(tipX + head * 0.5, tipY - dy * head);
			}
			g.closePath();
			g.fill();
		},

		drawBeamPath: function() {
			var g = this.vinc("cell_beam", "auto");
			var bd = this.board;
			g.vid = "c_beam_path";
			g.lineWidth = Math.max(2, this.bw * 0.15) | 0;

			var emitter = null;
			for (var c = 0; c < bd.cell.length; c++) {
				if (bd.cell[c].isEmitter()) {
					emitter = bd.cell[c];
					break;
				}
			}

			if (!emitter) { g.vhide(); return; }

			var segments = this.traceBeamVisual(emitter);
			if (segments.length === 0) { g.vhide(); return; }

			var lastCell = segments[segments.length - 1].cell;
			var reachedTarget = (lastCell && lastCell.isTarget());
			g.strokeStyle = reachedTarget ? "rgba(34,180,34,0.7)" : "rgba(200,80,50,0.6)";

			g.beginPath();
			var sx = emitter.bx * this.bw;
			var sy = emitter.by * this.bh;
			g.moveTo(sx, sy);
			for (var i = 0; i < segments.length; i++) {
				g.lineTo(segments[i].x, segments[i].y);
			}
			g.stroke();
		},

		traceBeamVisual: function(emitter) {
			var dir = emitter.qdir;
			var segments = [];
			var pos = emitter.getaddr();
			var maxSteps = (this.board.cols + this.board.rows) * 4;
			var visited = {};

			for (var step = 0; step < maxSteps; step++) {
				pos.movedir(dir, 2);
				var cell = pos.getc();

				if (cell.isnull) { break; }

				segments.push({
					x: cell.bx * this.bw,
					y: cell.by * this.bh,
					cell: cell
				});

				if (cell.isTarget()) { break; }
				if (cell.isEmitter()) { break; }

				if (cell.hasMirror()) {
					if (cell.qans === 31) {
						dir = [0, 4, 3, 2, 1][dir];
					} else {
						dir = [0, 3, 4, 1, 2][dir];
					}
				}

				var key = cell.id + "_" + dir;
				if (visited[key]) { break; }
				visited[key] = true;
			}
			return segments;
		}
	},

	Encode: {
		decodePzpr: function(type) {
			this.decodeRadiance();
		},
		encodePzpr: function(type) {
			this.encodeRadiance();
		},

		decodeRadiance: function() {
			var bstr = this.outbstr;
			var bd = this.board;
			var c = 0;
			var i = 0;

			while (i < bstr.length && c < bd.cell.length) {
				var ch = bstr.charAt(i);

				if (ch === "1") {
					i++;
					var dir = parseInt(bstr.charAt(i), 10);
					bd.cell[c].ques = 1;
					bd.cell[c].qdir = dir;
					c++;
				} else if (ch === "2") {
					bd.cell[c].ques = 2;
					c++;
				} else if (ch === "3") {
					bd.cell[c].ques = 3;
					c++;
				} else if (ch >= "a" && ch <= "z") {
					c += (ch.charCodeAt(0) - 96);
				}
				i++;
			}
			this.outbstr = bstr.substring(i);
		},

		encodeRadiance: function() {
			var bd = this.board;
			var cm = "";
			var empty = 0;

			for (var c = 0; c < bd.cell.length; c++) {
				var cell = bd.cell[c];
				if (cell.ques === 1) {
					if (empty > 0) {
						cm += String.fromCharCode(96 + empty);
						empty = 0;
					}
					cm += "1" + cell.qdir;
				} else if (cell.ques === 2) {
					if (empty > 0) {
						cm += String.fromCharCode(96 + empty);
						empty = 0;
					}
					cm += "2";
				} else if (cell.ques === 3) {
					if (empty > 0) {
						cm += String.fromCharCode(96 + empty);
						empty = 0;
					}
					cm += "3";
				} else {
					empty++;
					if (empty >= 26) {
						cm += "z";
						empty = 0;
					}
				}
			}
			if (empty > 0) {
				cm += String.fromCharCode(96 + empty);
			}
			this.outbstr += cm;
		}
	},


	FileIO: {
		decodeData: function() {
			this.decodeCell(function(cell, ca) {
				if (ca.charAt(0) === "E") {
					cell.ques = 1;
					cell.qdir = parseInt(ca.charAt(1), 10);
				} else if (ca === "T") {
					cell.ques = 2;
				} else if (ca === "S") {
					cell.ques = 3;
				} else if (ca === "1") {
					cell.ques = 3;
					cell.qans = 31;
				} else if (ca === "2") {
					cell.ques = 3;
					cell.qans = 32;
				}
			});
		},
		encodeData: function() {
			this.encodeCell(function(cell) {
				if (cell.ques === 1) {
					return "E" + cell.qdir + " ";
				} else if (cell.ques === 2) {
					return "T ";
				} else if (cell.ques === 3) {
					if (cell.qans === 31) { return "1 "; }
					if (cell.qans === 32) { return "2 "; }
					return "S ";
				}
				return ". ";
			});
		}
	},

	AnsCheck: {
		checklist: [
			"checkGridSize",
			"checkBeamReachesTarget",
			"checkAllSlotsUsed"
		],

		checkGridSize: function() {
			var bd = this.board;
			if (bd.cols < 6 || bd.rows < 6 || bd.cols > 12 || bd.rows > 12) {
				this.failcode.add("rdGridSize");
			}
		},

		checkBeamReachesTarget: function() {
			var bd = this.board;
			var emitter = null;
			var target = null;

			for (var c = 0; c < bd.cell.length; c++) {
				if (bd.cell[c].isEmitter()) { emitter = bd.cell[c]; }
				if (bd.cell[c].isTarget()) { target = bd.cell[c]; }
			}

			if (!emitter || !target) {
				this.failcode.add("rdMissedTarget");
				return;
			}

			var path = this.traceBeam(emitter);
			this._beamPath = path;

			var reached = false;
			for (var i = 0; i < path.length; i++) {
				if (path[i] === target) {
					reached = true;
					break;
				}
			}

			if (!reached) {
				this.failcode.add("rdMissedTarget");
				if (this.checkOnly) { return; }
				emitter.seterr(1);
				target.seterr(1);
			}
		},

		checkAllSlotsUsed: function() {
			var bd = this.board;
			var path = this._beamPath;

			if (!path) {
				var emitter = null;
				for (var c = 0; c < bd.cell.length; c++) {
					if (bd.cell[c].isEmitter()) { emitter = bd.cell[c]; break; }
				}
				if (!emitter) { return; }
				path = this.traceBeam(emitter);
			}

			var visited = {};
			for (var i = 0; i < path.length; i++) {
				visited[path[i].id] = true;
			}

			for (var c2 = 0; c2 < bd.cell.length; c2++) {
				var cell = bd.cell[c2];
				if (cell.isMirrorSlot() && !visited[cell.id]) {
					this.failcode.add("rdSlotSkipped");
					if (this.checkOnly) { return; }
					cell.seterr(1);
				}
			}
		},

		traceBeam: function(emitter) {
			var dir = emitter.qdir;
			var path = [];
			var pos = emitter.getaddr();
			var maxSteps = (this.board.cols + this.board.rows) * 4;
			var visited = {};

			for (var step = 0; step < maxSteps; step++) {
				pos.movedir(dir, 2);
				var cell = pos.getc();

				if (cell.isnull) { break; }
				if (cell.isEmitter()) { break; }

				path.push(cell);

				if (cell.isTarget()) { break; }

				if (cell.hasMirror()) {
					dir = this.reflectDirection(dir, cell.qans);
				}

				var key = cell.id + "_" + dir;
				if (visited[key]) { break; }
				visited[key] = true;
			}
			return path;
		},

		reflectDirection: function(dir, mirrorType) {
			if (mirrorType === 31) {
				return [0, 4, 3, 2, 1][dir];
			}
			return [0, 3, 4, 1, 2][dir];
		}
	},

	
	FailCode: {
		rdGridSize: "rdGridSize.radiance",
		rdMissedTarget: "rdMissedTarget.radiance",
		rdSlotSkipped: "rdSlotSkipped.radiance"
	}
});
