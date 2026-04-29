//
// パズル固有スクリプト部 ノリブリッジ版 noribridge.js
//
(function(pidlist, classbase) {
	if (typeof module === "object" && module.exports) {
		module.exports = [pidlist, classbase];
	} else {
		pzpr.classmgr.makeCustom(pidlist, classbase);
	}
})(["noribridge"], {
	//---------------------------------------------------------
	// マウス入力系
	MouseEvent: {
		autoedit_func: "areanum",
		autoplay_func: "border",
		inputModes: {
			edit: ["border", "number", "clear"],
			play: ["border", "subline"]
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
		maxnum: 8,
		minnum: 0
	},

	Border: {
		isBorder: function() {
			return this.ques > 0;
		},
		isBridge: function() {
			return this.ques > 0 && this.qans > 0;
		},

		prehook: {
			qans: function() {
				return this.ques === 0;
			},
			qsub: function() {
				return this.ques === 0;
			}
		}
	},

	Board: {
		hasborder: 1,
		customRules: [
			"Bridge Placement \u2014 place bridges on border segments between adjacent regions.",
			"Connected Graph \u2014 all regions must be connected via bridges.",
			"Degree Match \u2014 numbered regions must have exactly that many bridges.",
			"Single Bridge Per Border \u2014 at most one bridge per shared border between two regions."
		]
	},

	AreaRoomGraph: {
		enabled: true,
		hastop: true
	},

	//---------------------------------------------------------
	// 画像表示系
	Graphic: {
		gridcolor_type: "LIGHT",

		numbercolor_func: "qnum",

		paint: function() {
			this.drawBGCells();
			this.drawGrid();
			this.drawBridges();
			this.drawBorders();
			this.drawChassis();
			this.drawBoxBorders(false);
			this.drawQuesNumbers();
			this.drawPekes();
			this.drawTarget();
		},

		getBorderColor: function(border) {
			if (border.ques > 0) {
				return border.error === 1 ? this.errcolor1 : this.quescolor;
			}
			return null;
		},

		drawBridges: function() {
			var g = this.vinc("bridge_line", "crispEdges", true);

			var lw = Math.max(this.lw * 1.5, 3);
			var blist = this.range.borders;
			for (var i = 0; i < blist.length; i++) {
				var border = blist[i];

				g.vid = "b_bridge_" + border.id;
				if (border.ques > 0 && border.qans > 0) {
					var px = border.bx * this.bw,
						py = border.by * this.bh;
					var color;
					if (border.error === 1) {
						color = this.errcolor1;
					} else if (border.trial) {
						color = this.trialcolor;
					} else {
						color = "rgb(0, 160, 0)";
					}
					g.fillStyle = color;
					if (border.isVert()) {
						// Vertical border: draw horizontal bridge line crossing it
						g.fillRectCenter(px, py, this.bw * 0.7, lw / 2);
					} else {
						// Horizontal border: draw vertical bridge line crossing it
						g.fillRectCenter(px, py, lw / 2, this.bh * 0.7);
					}
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
			this.decodeBorder();
			this.decodeRoomNumber16();
		},
		encodePzpr: function(type) {
			this.encodeBorder();
			this.encodeRoomNumber16();
		}
	},

	//---------------------------------------------------------
	// ファイル入出力処理
	FileIO: {
		decodeData: function() {
			this.decodeBorderQues();
			this.decodeCellQnum();
			this.decodeBorderAns();
		},
		encodeData: function() {
			this.encodeBorderQues();
			this.encodeCellQnum();
			this.encodeBorderAns();
		}
	},

	//---------------------------------------------------------
	// 正解判定処理実行部
	AnsCheck: {
		checklist: [
			"checkBridgeExist",
			"checkSingleBridgePerPair",
			"checkDegreeOver",
			"checkBridgeConnectivity",
			"checkDegreeUnder"
		],

		checkBridgeExist: function() {
			var bd = this.board;
			for (var i = 0; i < bd.border.length; i++) {
				if (bd.border[i].ques > 0 && bd.border[i].qans > 0) {
					return;
				}
			}
			this.failcode.add("brNone");
		},

		checkSingleBridgePerPair: function() {
			var bd = this.board;
			var rooms = bd.roommgr.components;
			var len = rooms.length;
			for (var r = 0; r < len; r++) {
				rooms[r]._nid = r;
			}

			var pairBridges = {};
			for (var i = 0; i < bd.border.length; i++) {
				var b = bd.border[i];
				if (!b || b.isnull || b.ques === 0 || b.qans === 0) {
					continue;
				}

				var c1 = b.sidecell[0],
					c2 = b.sidecell[1];
				if (!c1 || c1.isnull || !c2 || c2.isnull) {
					continue;
				}
				var r1 = c1.room,
					r2 = c2.room;
				if (!r1 || !r2 || r1 === r2) {
					continue;
				}

				var key =
					r1._nid < r2._nid
						? r1._nid + "," + r2._nid
						: r2._nid + "," + r1._nid;

				if (!pairBridges[key]) {
					pairBridges[key] = [];
				}
				pairBridges[key].push(b);
			}

			for (var key in pairBridges) {
				if (pairBridges[key].length > 1) {
					this.failcode.add("brDuplicate");
					if (this.checkOnly) {
						return;
					}
					var blist = pairBridges[key];
					for (var j = 0; j < blist.length; j++) {
						blist[j].seterr(1);
					}
				}
			}
		},

		checkDegreeOver: function() {
			this.checkDegreeMatch("brDegreeOver", function(count, num) {
				return count > num;
			});
		},

		checkDegreeUnder: function() {
			this.checkDegreeMatch("brDegreeUnder", function(count, num) {
				return count < num;
			});
		},

		checkDegreeMatch: function(code, cmpfunc) {
			var bd = this.board;
			var rooms = bd.roommgr.components;
			var len = rooms.length;
			for (var r = 0; r < len; r++) {
				rooms[r]._nid = r;
			}

			for (var r = 0; r < len; r++) {
				var room = rooms[r];
				var num = room.top.qnum;
				if (num < 0) {
					continue;
				}

				// Count distinct rooms connected by bridge
				var connectedRooms = {};
				var clist = room.clist;
				for (var c = 0; c < clist.length; c++) {
					var cell = clist[c];
					var cblist = cell.getdir4cblist();
					for (var i = 0; i < cblist.length; i++) {
						var neighbor = cblist[i][0];
						var border = cblist[i][1];
						if (border.isnull || neighbor.isnull) {
							continue;
						}
						if (border.ques === 0 || border.qans === 0) {
							continue;
						}
						var otherRoom = neighbor.room;
						if (!otherRoom || otherRoom === room) {
							continue;
						}
						connectedRooms[otherRoom._nid] = true;
					}
				}

				var bridgeCount = Object.keys(connectedRooms).length;
				if (cmpfunc(bridgeCount, num)) {
					this.failcode.add(code);
					if (this.checkOnly) {
						return;
					}
					room.clist.seterr(1);
				}
			}
		},

		checkBridgeConnectivity: function() {
			var bd = this.board;
			var rooms = bd.roommgr.components;
			var len = rooms.length;
			if (len <= 1) {
				return;
			}

			for (var r = 0; r < len; r++) {
				rooms[r]._nid = r;
			}

			// Build adjacency via bridges
			var adj = {};
			for (var r = 0; r < len; r++) {
				adj[r] = {};
			}

			for (var i = 0; i < bd.border.length; i++) {
				var b = bd.border[i];
				if (!b || b.isnull || b.ques === 0 || b.qans === 0) {
					continue;
				}
				var c1 = b.sidecell[0],
					c2 = b.sidecell[1];
				if (!c1 || c1.isnull || !c2 || c2.isnull) {
					continue;
				}
				var r1 = c1.room,
					r2 = c2.room;
				if (!r1 || !r2 || r1 === r2) {
					continue;
				}
				adj[r1._nid][r2._nid] = true;
				adj[r2._nid][r1._nid] = true;
			}

			// BFS from room 0
			var visited = {};
			var queue = [0];
			visited[0] = true;
			while (queue.length > 0) {
				var cur = queue.shift();
				for (var nb in adj[cur]) {
					if (!visited[nb]) {
						visited[nb] = true;
						queue.push(+nb);
					}
				}
			}

			// Check all rooms visited
			var unreached = [];
			for (var r = 0; r < len; r++) {
				if (!visited[r]) {
					unreached.push(r);
				}
			}
			if (unreached.length > 0) {
				this.failcode.add("brDisconnected");
				if (this.checkOnly) {
					return;
				}
				for (var u = 0; u < unreached.length; u++) {
					rooms[unreached[u]].clist.seterr(1);
				}
			}
		}
	}
});
