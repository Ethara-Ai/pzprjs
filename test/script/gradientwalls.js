/* gradientwalls.js */

ui.debug.addDebugData("gradientwalls", {
	url: "6/6/1g1434g3h4g1i1g4g41g1k4414g4340040o00k020",
	failcheck: [
		[
			"gwWallClose",
			"pzprv3/gradientwalls/3/3/1 . 3 /1 . 3 /. 1 . /1 0 /0 0 /0 0 /0 0 0 /0 0 0 /. 2 . /. 2 2 /. 2 . /"
		],
		[
			"gwOpenFar",
			"pzprv3/gradientwalls/6/6/1 . 1 4 3 4 /. 3 . . 4 . /1 . . . 1 . /4 . 4 1 . 1 /. . . . . 4 /4 1 4 . 4 3 /0 0 1 0 0 /0 0 0 0 0 /0 0 0 0 0 /0 0 1 0 0 /0 0 0 0 0 /1 1 0 0 0 /0 0 0 0 0 0 /0 0 0 0 1 0 /1 0 0 0 0 0 /0 0 0 0 0 1 /0 0 0 0 0 0 /. 4 . . . . /2 . 2 3 . 3 /. 2 3 2 . 2 /. 3 . . 2 . /3 2 3 2 3 . /. . . 3 . . /"
		],
		[
			"ceEmpty",
			"pzprv3/gradientwalls/6/6/1 . 1 4 3 4 /. 3 . . 4 . /1 . . . 1 . /4 . 4 1 . 1 /. . . . . 4 /4 1 4 . 4 3 /0 0 1 0 0 /0 0 0 0 0 /0 0 0 0 0 /0 0 1 0 0 /0 0 0 0 0 /1 1 0 0 0 /0 0 0 0 0 0 /0 0 0 0 1 0 /1 0 0 0 0 0 /0 0 0 0 0 1 /0 0 0 0 0 0 /. . . . . . /. . . . . . /. . . . . . /. . . . . . /. . . . . . /. . . . . . /"
		],
		[
			null,
			"pzprv3/gradientwalls/6/6/1 . 1 4 3 4 /. 3 . . 4 . /1 . . . 1 . /4 . 4 1 . 1 /. . . . . 4 /4 1 4 . 4 3 /0 0 1 0 0 /0 0 0 0 0 /0 0 0 0 0 /0 0 1 0 0 /0 0 0 0 0 /1 1 0 0 0 /0 0 0 0 0 0 /0 0 0 0 1 0 /1 0 0 0 0 0 /0 0 0 0 0 1 /0 0 0 0 0 0 /. 2 . . . . /2 . 2 3 . 3 /. 2 3 2 . 2 /. 3 . . 2 . /3 2 3 2 3 . /. . . 3 . . /"
		]
	],
	inputs: [
		/* 問題入力テスト: create board, place borders and clue numbers */
		{ input: ["newboard,3,3", "editmode"] },
		{
			input: ["cursor,1,1", "key,2", "key,right,right,3"],
			result:
				"pzprv3/gradientwalls/3/3/2 . 3 /. . . /. . . /0 0 /0 0 /0 0 /0 0 0 /0 0 0 /. . . /. . . /. . . /"
		},
		{
			input: ["mouse,left, 2,0, 2,2"],
			result:
				"pzprv3/gradientwalls/3/3/2 . 3 /. . . /. . . /0 0 /0 0 /0 0 /1 0 0 /0 0 0 /. . . /. . . /. . . /"
		},
		/* 回答入力テスト: play mode number entry */
		{
			input: [
				"playmode",
				"mouse,left, 3,1",
				"mouse,left, 3,1",
				"mouse,left, 3,1"
			],
			result:
				"pzprv3/gradientwalls/3/3/2 . 3 /. . . /. . . /0 0 /0 0 /0 0 /1 0 0 /0 0 0 /. 2 . /. . . /. . . /"
		},
		/* Verify clue cells cannot be overwritten in play mode */
		{
			input: ["mouse,left, 1,1", "mouse,left, 1,1"],
			result:
				"pzprv3/gradientwalls/3/3/2 . 3 /. . . /. . . /0 0 /0 0 /0 0 /1 0 0 /0 0 0 /. 2 . /. . . /. . . /"
		},
		/* Keyboard play mode input */
		{
			input: ["cursor,3,3", "key,1"],
			result:
				"pzprv3/gradientwalls/3/3/2 . 3 /. . . /. . . /0 0 /0 0 /0 0 /1 0 0 /0 0 0 /. 2 . /. 1 . /. . . /"
		},
		/* Erase answer with space */
		{
			input: ["key, "],
			result:
				"pzprv3/gradientwalls/3/3/2 . 3 /. . . /. . . /0 0 /0 0 /0 0 /1 0 0 /0 0 0 /. 2 . /. . . /. . . /"
		}
	]
});
