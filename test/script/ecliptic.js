/* ecliptic.js */

ui.debug.addDebugData("ecliptic", {
	url: "6/6/h2g0l01k1j10m1i",
	failcheck: [
		["brNoShade", "pzprv3/ecliptic/6/6"],
		[
			"ecNeighborNe",
			"pzprv3/ecliptic/6/6/. . 2 . 0 . /. . . . . 0 /1 . . . . . /1 . . . . 1 /0 . . . . . /. . 1 . . . /# # + + + + /# + # + + + /+ + + # # + /+ # + # + + /+ # + + + # /+ + + + # # /"
		],
		[
			null,
			"pzprv3/ecliptic/6/6/. . 2 . 0 . /. . . . . 0 /1 . . . . . /1 . . . . 1 /0 . . . . . /. . 1 . . . /# # + + + + /# + # + + + /+ + + # # + /+ # + # + + /+ + # + + # /+ + + + # # /"
		]
	],
	inputs: [
		{ input: ["editmode", "newboard,6,1"] },
		{
			input: [
				"cursor,1,1",
				"key,0",
				"key,right",
				"key,1",
				"key,right",
				"key,2",
				"key,right",
				"key,3",
				"key,right",
				"key,4"
			],
			result: "pzprv3/ecliptic/1/5/0 1 2 3 4 /. . . . . /"
		}
	]
});
