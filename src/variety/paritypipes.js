//
// パズル固有スクリプト部 パリティパイプス版 paritypipes.js
//
// Parity Pipes: Draw closed loops on grid edges.
// Every vertex is pre-colored black (B) or white (W).
// Black vertex: the loop passes through it (exactly 2 drawn edges).
// White vertex: the loop does not pass through it (exactly 0 drawn edges).
// All drawn edges form disjoint simple closed loops.
//
(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["paritypipes"], {
	//---------------------------------------------------------
	// マウス入力系
	MouseEvent: {
		inputModes: {
			edit: ["number", "clear"],
			play: ["line", "peke", "clear", "info-line"]
		},

		mouseinput_clear: function() {
			this.inputclean_cross();
		},
		mouseinput_number: function() {
			if (this.mousestart) {
				this.inputqnum_cross();
			}
		},

		mouseinput_auto: function() {
			if (this.puzzle.playmode) {
				if (this.btn === "left") {
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
			} else if (this.puzzle.editmode) {
				if (this.mousestart) {
					this.inputqnum_cross();
				}
			}
		}
	},

	//---------------------------------------------------------
	// キーボード入力系
	KeyEvent: {
		enablemake: true,
		moveTarget: function(ca) {
			return this.moveTCross(ca);
		},
		keyinput: function(ca) {
			this.key_inputcross(ca);
		}
	},

	TargetCursor: {
		crosstype: true
	},

	//---------------------------------------------------------
	// 盤面管理系
	Cross: {
		maxnum: 2,
		minnum: 1
	},

	Board: {
		hasborder: 2,
		borderAsLine: true,

		customRules: [
			"Draw edges on the grid to form closed loops.",
			"Every vertex is pre-colored black (1) or white (2).",
			"Black vertex: the loop passes through (exactly 2 drawn edges).",
			"White vertex: the loop does not pass through (exactly 0 drawn edges).",
			"All drawn edges form simple closed loops (no branches or dead ends)."
		]
	},

	LineGraph: {
		enabled: true
	},

	//---------------------------------------------------------
	// 画像表示系
	Graphic: {
		irowake: true,
		margin: 0.5,

		circlesize_cross: 0.28,

		paint: function() {
			this.drawBGCells();
			this.drawLines();
			this.drawBaseMarks();
			this.drawVertexCircles();
			this.drawCrossErrors();
			this.drawPekes();
			this.drawTarget();
		},

		repaintParts: function(blist) {
			this.range.crosses = blist.crossinside();
			this.drawBaseMarks();
		},

		drawVertexCircles: function() {
			var g = this.vinc("cross_circle", "auto");
			var clist = this.range.crosses;
			var r = this.circlesize_cross * this.cw;
			if (r < 3) {
				r = 3;
			}

			for (var i = 0; i < clist.length; i++) {
				var cross = clist[i];
				var px = cross.bx * this.bw;
				var py = cross.by * this.bh;
				var qn = cross.qnum;

				g.vid = "x_cp_" + cross.id;
				if (qn === 1) {
					g.fillStyle = cross.error === 1 ? this.errbcolor1 : "#222222";
					g.strokeStyle = cross.error === 1 ? this.errbcolor1 : "#222222";
					g.shapeCircle(px, py, r);
				} else if (qn === 2) {
					g.fillStyle = cross.error === 1 ? this.errbcolor1 : "#ffffff";
					g.strokeStyle = cross.error === 1 ? this.errbcolor1 : "#222222";
					g.shapeCircle(px, py, r);
				} else {
					g.vhide();
				}
			}
		}
	},

	//---------------------------------------------------------
	// URLエンコード/デコード処理
	// Binary encoding: pack vertex colors as bits (1=black, 0=white)
	// 5 bits per base-32 character
	Encode: {
		decodePzpr: function(type) {
			this.decodeParity();
		},
		encodePzpr: function(type) {
			this.encodeParity();
		},

		decodeParity: function() {
			var bstr = this.outbstr;
			var bd = this.board;
			var idx = 0;

			for (var i = 0; i < bstr.length && idx < bd.cross.length; i++) {
				var ch = bstr.charAt(i);
				var val = parseInt(ch, 32);
				if (isNaN(val)) {
					continue;
				}
				for (var bit = 4; bit >= 0 && idx < bd.cross.length; bit--) {
					var b = (val >> bit) & 1;
					bd.cross[idx].qnum = b === 1 ? 1 : 2;
					idx++;
				}
			}
			this.outbstr = bstr.substr(i);
		},

		encodeParity: function() {
			var bd = this.board;
			var cm = "";
			var bits = 0;
			var count = 0;

			for (var c = 0; c < bd.cross.length; c++) {
				var qn = bd.cross[c].qnum;
				bits = (bits << 1) | (qn === 1 ? 1 : 0);
				count++;
				if (count === 5) {
					cm += bits.toString(32);
					bits = 0;
					count = 0;
				}
			}
			if (count > 0) {
				bits = bits << (5 - count);
				cm += bits.toString(32);
			}
			this.outbstr += cm;
		}
	},

	//---------------------------------------------------------
	// ファイル入出力系
	FileIO: {
		decodeData: function() {
			this.decodeCross(function(cross, ca) {
				cross.qnum = +ca;
			});
			this.decodeBorderLine();
		},
		encodeData: function() {
			this.encodeCross(function(cross) {
				return cross.qnum + " ";
			});
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
			"checkVertexParity",
			"checkDeadendLine+"
		],

		checkVertexParity: function() {
			var bd = this.board;
			for (var c = 0; c < bd.cross.length; c++) {
				var cross = bd.cross[c];
				var qn = cross.qnum;
				if (qn < 1) {
					continue;
				}

				var lcnt = cross.lcnt;
				var wantPass = qn === 1;
				var passes = lcnt === 2;

				if (wantPass !== passes) {
					this.failcode.add("ppVertexParity");
					if (this.checkOnly) {
						break;
					}
					cross.seterr(1);
				}
			}
		}
	},

	FailCode: {}
});
