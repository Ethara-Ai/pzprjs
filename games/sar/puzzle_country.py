import sys
import time
from datetime import datetime, timezone

_PUZZLES = {
    "easy": {
        "rows": 5, "cols": 5,
        "url_body": "013n0vu03154g2",
        "room_grid": [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [1, 1, 2, 2, 2], [3, 3, 4, 5, 2], [3, 3, 4, 5, 2]],
        "clues": {"0": 3, "1": 1, "2": 5, "3": 4, "5": 2},
        "moves_required": ["mouse,left,1,3,3,3", "mouse,left,3,3,5,3", "mouse,left,1,3,1,5", "mouse,left,5,3,5,5", "mouse,left,5,5,7,5", "mouse,left,7,5,9,5", "mouse,left,1,5,1,7", "mouse,left,9,5,9,7", "mouse,left,3,7,5,7", "mouse,left,5,7,7,7", "mouse,left,1,7,1,9", "mouse,left,3,7,3,9", "mouse,left,7,7,7,9", "mouse,left,9,7,9,9", "mouse,left,1,9,3,9", "mouse,left,7,9,9,9"],
        "moves_hint": ["mouse,right,2,1", "mouse,right,4,1", "mouse,right,6,1", "mouse,right,8,1", "mouse,right,1,2", "mouse,right,3,2", "mouse,right,5,2", "mouse,right,7,2", "mouse,right,9,2", "mouse,right,6,3", "mouse,right,8,3", "mouse,right,3,4", "mouse,right,7,4", "mouse,right,9,4", "mouse,right,2,5", "mouse,right,4,5", "mouse,right,3,6", "mouse,right,5,6", "mouse,right,7,6", "mouse,right,2,7", "mouse,right,8,7", "mouse,right,5,8", "mouse,right,4,9", "mouse,right,6,9"],
    },
    "medium": {
        "rows": 10, "cols": 10,
        "url_body": "24gelnnvem7u6vd9bg7tbqlh3i9q8s4nda1vg43j6h1k2h5",
        "room_grid": [[0, 0, 0, 0, 1, 1, 1, 1, 2, 2], [0, 0, 3, 3, 3, 3, 3, 3, 2, 4], [0, 3, 3, 5, 5, 6, 6, 3, 4, 4], [7, 3, 8, 5, 9, 9, 6, 3, 4, 10], [7, 3, 8, 11, 12, 12, 6, 3, 10, 10], [7, 8, 8, 11, 3, 3, 3, 3, 13, 10], [7, 14, 8, 11, 3, 13, 13, 13, 13, 10], [7, 14, 14, 11, 3, 15, 13, 15, 15, 16], [7, 17, 17, 11, 11, 15, 15, 15, 16, 16], [7, 17, 17, 11, 18, 19, 19, 19, 19, 19]],
        "clues": {"1": 4, "2": 3, "7": 6, "10": 1, "16": 2, "19": 5},
        "moves_required": ["mouse,left,3,1,5,1", "mouse,left,5,1,7,1", "mouse,left,7,1,9,1", "mouse,left,9,1,11,1", "mouse,left,11,1,13,1", "mouse,left,13,1,15,1", "mouse,left,17,1,19,1", "mouse,left,3,1,3,3", "mouse,left,15,1,15,3", "mouse,left,17,1,17,3", "mouse,left,19,1,19,3", "mouse,left,1,3,3,3", "mouse,left,15,3,17,3", "mouse,left,1,3,1,5", "mouse,left,19,3,19,5", "mouse,left,7,5,9,5", "mouse,left,11,5,13,5", "mouse,left,17,5,19,5", "mouse,left,1,5,1,7", "mouse,left,7,5,7,7", "mouse,left,9,5,9,7", "mouse,left,11,5,11,7", "mouse,left,13,5,13,7", "mouse,left,17,5,17,7", "mouse,left,5,7,7,7", "mouse,left,9,7,11,7", "mouse,left,1,7,1,9", "mouse,left,5,7,5,9", "mouse,left,13,7,13,9", "mouse,left,17,7,17,9", "mouse,left,7,9,9,9", "mouse,left,9,9,11,9", "mouse,left,11,9,13,9", "mouse,left,1,9,1,11", "mouse,left,5,9,5,11", "mouse,left,7,9,7,11", "mouse,left,17,9,17,11", "mouse,left,3,11,5,11", "mouse,left,1,11,1,13", "mouse,left,3,11,3,13", "mouse,left,7,11,7,13", "mouse,left,17,11,17,13", "mouse,left,11,13,13,13", "mouse,left,13,13,15,13", "mouse,left,15,13,17,13", "mouse,left,1,13,1,15", "mouse,left,3,13,3,15", "mouse,left,7,13,7,15", "mouse,left,11,13,11,15", "mouse,left,3,15,5,15", "mouse,left,15,15,17,15", "mouse,left,17,15,19,15", "mouse,left,1,15,1,17", "mouse,left,5,15,5,17", "mouse,left,7,15,7,17", "mouse,left,11,15,11,17", "mouse,left,15,15,15,17", "mouse,left,19,15,19,17", "mouse,left,1,17,3,17", "mouse,left,7,17,9,17", "mouse,left,11,17,13,17", "mouse,left,13,17,15,17", "mouse,left,3,17,3,19", "mouse,left,5,17,5,19", "mouse,left,9,17,9,19", "mouse,left,19,17,19,19", "mouse,left,3,19,5,19", "mouse,left,9,19,11,19", "mouse,left,11,19,13,19", "mouse,left,13,19,15,19", "mouse,left,15,19,17,19", "mouse,left,17,19,19,19"],
        "moves_hint": ["mouse,right,2,1", "mouse,right,16,1", "mouse,right,1,2", "mouse,right,5,2", "mouse,right,7,2", "mouse,right,9,2", "mouse,right,11,2", "mouse,right,13,2", "mouse,right,4,3", "mouse,right,6,3", "mouse,right,8,3", "mouse,right,10,3", "mouse,right,12,3", "mouse,right,14,3", "mouse,right,18,3", "mouse,right,3,4", "mouse,right,5,4", "mouse,right,7,4", "mouse,right,9,4", "mouse,right,11,4", "mouse,right,13,4", "mouse,right,15,4", "mouse,right,17,4", "mouse,right,2,5", "mouse,right,4,5", "mouse,right,6,5", "mouse,right,10,5", "mouse,right,14,5", "mouse,right,16,5", "mouse,right,3,6", "mouse,right,5,6", "mouse,right,15,6", "mouse,right,19,6", "mouse,right,2,7", "mouse,right,4,7", "mouse,right,8,7", "mouse,right,12,7", "mouse,right,14,7", "mouse,right,16,7", "mouse,right,18,7", "mouse,right,3,8", "mouse,right,7,8", "mouse,right,9,8", "mouse,right,11,8", "mouse,right,15,8", "mouse,right,19,8", "mouse,right,2,9", "mouse,right,4,9", "mouse,right,6,9", "mouse,right,14,9", "mouse,right,16,9", "mouse,right,18,9", "mouse,right,3,10", "mouse,right,9,10", "mouse,right,11,10", "mouse,right,13,10", "mouse,right,15,10", "mouse,right,19,10", "mouse,right,2,11", "mouse,right,6,11", "mouse,right,8,11", "mouse,right,10,11", "mouse,right,12,11", "mouse,right,14,11", "mouse,right,16,11", "mouse,right,18,11", "mouse,right,5,12", "mouse,right,9,12", "mouse,right,11,12", "mouse,right,13,12", "mouse,right,15,12", "mouse,right,19,12", "mouse,right,2,13", "mouse,right,4,13", "mouse,right,6,13", "mouse,right,8,13", "mouse,right,10,13", "mouse,right,18,13", "mouse,right,5,14", "mouse,right,9,14", "mouse,right,13,14", "mouse,right,15,14", "mouse,right,17,14", "mouse,right,19,14", "mouse,right,2,15", "mouse,right,6,15", "mouse,right,8,15", "mouse,right,10,15", "mouse,right,12,15", "mouse,right,14,15", "mouse,right,3,16", "mouse,right,9,16", "mouse,right,13,16", "mouse,right,17,16", "mouse,right,4,17", "mouse,right,6,17", "mouse,right,10,17", "mouse,right,16,17", "mouse,right,18,17", "mouse,right,1,18", "mouse,right,7,18", "mouse,right,11,18", "mouse,right,13,18", "mouse,right,15,18", "mouse,right,17,18", "mouse,right,2,19", "mouse,right,6,19", "mouse,right,8,19"],
    },
    "hard": {
        "rows": 15, "cols": 15,
        "url_body": (
            "al4la9alilb59m9bcimgi91d96qidikql9laial4la000pvv6000frvu0007vuo"
            "3fvs000fvru000cvvj00032234413g2g2g44i2g4g44362g33g144i42h13g3i4"
        ),
        "room_grid": [[0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 6, 6], [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5, 6, 6], [7, 7, 1, 1, 8, 8, 9, 9, 10, 10, 11, 11, 12, 13, 13], [7, 7, 14, 14, 8, 8, 9, 9, 10, 10, 11, 11, 12, 13, 13], [7, 7, 14, 14, 8, 8, 15, 15, 15, 16, 17, 17, 12, 18, 18], [19, 19, 20, 20, 20, 21, 21, 22, 22, 16, 17, 17, 12, 18, 18], [19, 19, 20, 20, 20, 21, 21, 22, 22, 16, 17, 17, 23, 23, 23], [24, 24, 24, 25, 25, 25, 26, 26, 26, 16, 16, 16, 23, 23, 23], [24, 24, 24, 27, 27, 25, 28, 28, 29, 29, 30, 30, 30, 31, 31], [32, 32, 33, 27, 27, 25, 28, 28, 29, 29, 30, 30, 30, 31, 31], [32, 32, 33, 27, 27, 25, 34, 34, 34, 35, 35, 36, 36, 37, 37], [38, 38, 33, 39, 39, 40, 40, 41, 41, 35, 35, 36, 36, 37, 37], [38, 38, 33, 39, 39, 40, 40, 41, 41, 35, 35, 42, 42, 37, 37], [43, 43, 44, 44, 44, 45, 45, 46, 46, 47, 47, 42, 42, 48, 48], [43, 43, 44, 44, 44, 45, 45, 46, 46, 47, 47, 42, 42, 48, 48]],
        "clues": {"0": 3, "1": 2, "2": 2, "3": 3, "4": 4, "5": 4, "6": 1, "7": 3, "9": 2, "11": 2, "13": 4, "14": 4, "18": 2, "20": 4, "22": 4, "23": 4, "24": 3, "25": 6, "26": 2, "28": 3, "29": 3, "31": 1, "32": 4, "33": 4, "37": 4, "38": 2, "41": 1, "42": 3, "44": 3, "48": 4},
        "moves_required": ["mouse,left,3,1,5,1", "mouse,left,5,1,7,1", "mouse,left,7,1,9,1", "mouse,left,13,1,15,1", "mouse,left,15,1,17,1", "mouse,left,19,1,21,1", "mouse,left,21,1,23,1", "mouse,left,23,1,25,1", "mouse,left,3,1,3,3", "mouse,left,9,1,9,3", "mouse,left,13,1,13,3", "mouse,left,17,1,17,3", "mouse,left,19,1,19,3", "mouse,left,25,1,25,3", "mouse,left,1,3,3,3", "mouse,left,17,3,19,3", "mouse,left,25,3,27,3", "mouse,left,1,3,1,5", "mouse,left,9,3,9,5", "mouse,left,13,3,13,5", "mouse,left,27,3,27,5", "mouse,left,1,5,3,5", "mouse,left,9,5,11,5", "mouse,left,13,5,15,5", "mouse,left,15,5,17,5", "mouse,left,19,5,21,5", "mouse,left,21,5,23,5", "mouse,left,23,5,25,5", "mouse,left,27,5,29,5", "mouse,left,3,5,3,7", "mouse,left,11,5,11,7", "mouse,left,17,5,17,7", "mouse,left,19,5,19,7", "mouse,left,25,5,25,7", "mouse,left,29,5,29,7", "mouse,left,3,7,5,7", "mouse,left,5,7,7,7", "mouse,left,9,7,11,7", "mouse,left,17,7,19,7", "mouse,left,27,7,29,7", "mouse,left,7,7,7,9", "mouse,left,9,7,9,9", "mouse,left,25,7,25,9", "mouse,left,27,7,27,9", "mouse,left,5,9,7,9", "mouse,left,9,9,11,9", "mouse,left,13,9,15,9", "mouse,left,15,9,17,9", "mouse,left,21,9,23,9", "mouse,left,5,9,5,11", "mouse,left,11,9,11,11", "mouse,left,13,9,13,11", "mouse,left,17,9,17,11", "mouse,left,21,9,21,11", "mouse,left,23,9,23,11", "mouse,left,25,9,25,11", "mouse,left,27,9,27,11", "mouse,left,1,11,3,11", "mouse,left,5,11,7,11", "mouse,left,15,11,17,11", "mouse,left,23,11,25,11", "mouse,left,1,11,1,13", "mouse,left,3,11,3,13", "mouse,left,7,11,7,13", "mouse,left,11,11,11,13", "mouse,left,13,11,13,13", "mouse,left,15,11,15,13", "mouse,left,21,11,21,13", "mouse,left,27,11,27,13", "mouse,left,3,13,5,13", "mouse,left,5,13,7,13", "mouse,left,11,13,13,13", "mouse,left,15,13,17,13", "mouse,left,21,13,23,13", "mouse,left,27,13,29,13", "mouse,left,1,13,1,15", "mouse,left,17,13,17,15", "mouse,left,23,13,23,15", "mouse,left,29,13,29,15", "mouse,left,1,15,3,15", "mouse,left,3,15,5,15", "mouse,left,5,15,7,15", "mouse,left,7,15,9,15", "mouse,left,9,15,11,15", "mouse,left,15,15,17,15", "mouse,left,19,15,21,15", "mouse,left,21,15,23,15", "mouse,left,27,15,29,15", "mouse,left,11,15,11,17", "mouse,left,15,15,15,17", "mouse,left,19,15,19,17", "mouse,left,27,15,27,17", "mouse,left,7,17,9,17", "mouse,left,13,17,15,17", "mouse,left,25,17,27,17", "mouse,left,7,17,7,19", "mouse,left,9,17,9,19", "mouse,left,11,17,11,19", "mouse,left,13,17,13,19", "mouse,left,19,17,19,19", "mouse,left,25,17,25,19", "mouse,left,1,19,3,19", "mouse,left,3,19,5,19", "mouse,left,17,19,19,19", "mouse,left,23,19,25,19", "mouse,left,1,19,1,21", "mouse,left,5,19,5,21", "mouse,left,7,19,7,21", "mouse,left,9,19,9,21", "mouse,left,11,19,11,21", "mouse,left,13,19,13,21", "mouse,left,17,19,17,21", "mouse,left,23,19,23,21", "mouse,left,1,21,3,21", "mouse,left,9,21,11,21", "mouse,left,13,21,15,21", "mouse,left,15,21,17,21", "mouse,left,19,21,21,21", "mouse,left,25,21,27,21", "mouse,left,27,21,29,21", "mouse,left,3,21,3,23", "mouse,left,5,21,5,23", "mouse,left,7,21,7,23", "mouse,left,19,21,19,23", "mouse,left,21,21,21,23", "mouse,left,23,21,23,23", "mouse,left,25,21,25,23", "mouse,left,29,21,29,23", "mouse,left,7,23,9,23", "mouse,left,11,23,13,23", "mouse,left,23,23,25,23", "mouse,left,3,23,3,25", "mouse,left,5,23,5,25", "mouse,left,9,23,9,25", "mouse,left,11,23,11,25", "mouse,left,13,23,13,25", "mouse,left,19,23,19,25", "mouse,left,21,23,21,25", "mouse,left,29,23,29,25", "mouse,left,5,25,7,25", "mouse,left,7,25,9,25", "mouse,left,13,25,15,25", "mouse,left,21,25,23,25", "mouse,left,23,25,25,25", "mouse,left,3,25,3,27", "mouse,left,11,25,11,27", "mouse,left,15,25,15,27", "mouse,left,19,25,19,27", "mouse,left,25,25,25,27", "mouse,left,29,25,29,27", "mouse,left,1,27,3,27", "mouse,left,11,27,13,27", "mouse,left,15,27,17,27", "mouse,left,19,27,21,27", "mouse,left,25,27,27,27", "mouse,left,1,27,1,29", "mouse,left,13,27,13,29", "mouse,left,17,27,17,29", "mouse,left,21,27,21,29", "mouse,left,27,27,27,29", "mouse,left,29,27,29,29", "mouse,left,1,29,3,29", "mouse,left,3,29,5,29", "mouse,left,5,29,7,29", "mouse,left,7,29,9,29", "mouse,left,9,29,11,29", "mouse,left,11,29,13,29", "mouse,left,17,29,19,29", "mouse,left,19,29,21,29", "mouse,left,27,29,29,29"],
        "moves_hint": ["mouse,right,2,1", "mouse,right,10,1", "mouse,right,12,1", "mouse,right,18,1", "mouse,right,26,1", "mouse,right,28,1", "mouse,right,1,2", "mouse,right,5,2", "mouse,right,7,2", "mouse,right,11,2", "mouse,right,15,2", "mouse,right,21,2", "mouse,right,23,2", "mouse,right,27,2", "mouse,right,29,2", "mouse,right,4,3", "mouse,right,6,3", "mouse,right,8,3", "mouse,right,10,3", "mouse,right,12,3", "mouse,right,14,3", "mouse,right,16,3", "mouse,right,20,3", "mouse,right,22,3", "mouse,right,24,3", "mouse,right,28,3", "mouse,right,3,4", "mouse,right,5,4", "mouse,right,7,4", "mouse,right,11,4", "mouse,right,15,4", "mouse,right,17,4", "mouse,right,19,4", "mouse,right,21,4", "mouse,right,23,4", "mouse,right,25,4", "mouse,right,29,4", "mouse,right,4,5", "mouse,right,6,5", "mouse,right,8,5", "mouse,right,12,5", "mouse,right,18,5", "mouse,right,26,5", "mouse,right,1,6", "mouse,right,5,6", "mouse,right,7,6", "mouse,right,9,6", "mouse,right,13,6", "mouse,right,15,6", "mouse,right,21,6", "mouse,right,23,6", "mouse,right,27,6", "mouse,right,2,7", "mouse,right,8,7", "mouse,right,12,7", "mouse,right,14,7", "mouse,right,16,7", "mouse,right,20,7", "mouse,right,22,7", "mouse,right,24,7", "mouse,right,26,7", "mouse,right,1,8", "mouse,right,3,8", "mouse,right,5,8", "mouse,right,11,8", "mouse,right,13,8", "mouse,right,15,8", "mouse,right,17,8", "mouse,right,19,8", "mouse,right,21,8", "mouse,right,23,8", "mouse,right,29,8", "mouse,right,2,9", "mouse,right,4,9", "mouse,right,8,9", "mouse,right,12,9", "mouse,right,18,9", "mouse,right,20,9", "mouse,right,24,9", "mouse,right,26,9", "mouse,right,28,9", "mouse,right,1,10", "mouse,right,3,10", "mouse,right,7,10", "mouse,right,9,10", "mouse,right,15,10", "mouse,right,19,10", "mouse,right,29,10", "mouse,right,4,11", "mouse,right,8,11", "mouse,right,10,11", "mouse,right,12,11", "mouse,right,14,11", "mouse,right,18,11", "mouse,right,20,11", "mouse,right,22,11", "mouse,right,26,11", "mouse,right,28,11", "mouse,right,5,12", "mouse,right,9,12", "mouse,right,17,12", "mouse,right,19,12", "mouse,right,23,12", "mouse,right,25,12", "mouse,right,29,12", "mouse,right,2,13", "mouse,right,8,13", "mouse,right,10,13", "mouse,right,14,13", "mouse,right,18,13", "mouse,right,20,13", "mouse,right,24,13", "mouse,right,26,13", "mouse,right,3,14", "mouse,right,5,14", "mouse,right,7,14", "mouse,right,9,14", "mouse,right,11,14", "mouse,right,13,14", "mouse,right,15,14", "mouse,right,19,14", "mouse,right,21,14", "mouse,right,25,14", "mouse,right,27,14", "mouse,right,12,15", "mouse,right,14,15", "mouse,right,18,15", "mouse,right,24,15", "mouse,right,26,15", "mouse,right,1,16", "mouse,right,3,16", "mouse,right,5,16", "mouse,right,7,16", "mouse,right,9,16", "mouse,right,13,16", "mouse,right,17,16", "mouse,right,21,16", "mouse,right,23,16", "mouse,right,25,16", "mouse,right,29,16", "mouse,right,2,17", "mouse,right,4,17", "mouse,right,6,17", "mouse,right,10,17", "mouse,right,12,17", "mouse,right,16,17", "mouse,right,18,17", "mouse,right,20,17", "mouse,right,22,17", "mouse,right,24,17", "mouse,right,28,17", "mouse,right,1,18", "mouse,right,3,18", "mouse,right,5,18", "mouse,right,15,18", "mouse,right,17,18", "mouse,right,21,18", "mouse,right,23,18", "mouse,right,27,18", "mouse,right,29,18", "mouse,right,6,19", "mouse,right,8,19", "mouse,right,10,19", "mouse,right,12,19", "mouse,right,14,19", "mouse,right,16,19", "mouse,right,20,19", "mouse,right,22,19", "mouse,right,26,19", "mouse,right,28,19", "mouse,right,3,20", "mouse,right,15,20", "mouse,right,19,20", "mouse,right,21,20", "mouse,right,25,20", "mouse,right,27,20", "mouse,right,29,20", "mouse,right,4,21", "mouse,right,6,21", "mouse,right,8,21", "mouse,right,12,21", "mouse,right,18,21", "mouse,right,22,21", "mouse,right,24,21", "mouse,right,1,22", "mouse,right,9,22", "mouse,right,11,22", "mouse,right,13,22", "mouse,right,15,22", "mouse,right,17,22", "mouse,right,27,22", "mouse,right,2,23", "mouse,right,4,23", "mouse,right,6,23", "mouse,right,10,23", "mouse,right,14,23", "mouse,right,16,23", "mouse,right,18,23", "mouse,right,20,23", "mouse,right,22,23", "mouse,right,26,23", "mouse,right,28,23", "mouse,right,1,24", "mouse,right,7,24", "mouse,right,15,24", "mouse,right,17,24", "mouse,right,23,24", "mouse,right,25,24", "mouse,right,27,24", "mouse,right,2,25", "mouse,right,4,25", "mouse,right,10,25", "mouse,right,12,25", "mouse,right,16,25", "mouse,right,18,25", "mouse,right,20,25", "mouse,right,26,25", "mouse,right,28,25", "mouse,right,1,26", "mouse,right,5,26", "mouse,right,7,26", "mouse,right,9,26", "mouse,right,13,26", "mouse,right,17,26", "mouse,right,21,26", "mouse,right,23,26", "mouse,right,27,26", "mouse,right,4,27", "mouse,right,6,27", "mouse,right,8,27", "mouse,right,10,27", "mouse,right,14,27", "mouse,right,18,27", "mouse,right,22,27", "mouse,right,24,27", "mouse,right,28,27", "mouse,right,3,28", "mouse,right,5,28", "mouse,right,7,28", "mouse,right,9,28", "mouse,right,11,28", "mouse,right,15,28", "mouse,right,19,28", "mouse,right,23,28", "mouse,right,25,28", "mouse,right,14,29", "mouse,right,16,29", "mouse,right,22,29", "mouse,right,24,29", "mouse,right,26,29"],
    },
}


def generate_puzzle_country(level="easy"):
    p = _PUZZLES[level]
    rows, cols = p["rows"], p["cols"]
    now = datetime.now(timezone.utc).isoformat()

    mr = p["moves_required"]
    mh = p["moves_hint"]
    mf = mr + mh

    return {
        "puzzle_url": f"http://localhost:8000/p.html?country/{cols}/{rows}/{p['url_body']}",
        "pid": "country",
        "sort_key": None,
        "width": cols,
        "height": rows,
        "area": rows * cols,
        "number_required_moves": len(mr),
        "number_total_solution_moves": len(mf),
        "puzzlink_url": f"http://localhost:8000/p.html?country/{cols}/{rows}/{p['url_body']}",
        "source": {
            "site_name": "ppbench_golden",
            "page_url": None,
            "feed_type": "golden_dataset",
            "published_at": now,
        },
        "metadata": {
            "has_structured_solution": True,
            "cspuz_is_unique": True,
            "db_w": cols,
            "db_h": rows,
            "level": level,
            "num_rooms": len(set(c for row in p["room_grid"] for c in row)),
            "num_clued_rooms": len(p["clues"]),
        },
        "created_at": now,
        "solution": {
            "moves_full": mf,
            "moves_required": mr,
            "moves_hint": mh,
        },
    }


if __name__ == "__main__":
    import json

    level = sys.argv[1] if len(sys.argv) > 1 else "easy"
    if level not in _PUZZLES:
        print(f"Usage: python puzzle_country.py [easy|medium|hard]")
        sys.exit(1)

    t0 = time.monotonic()
    puzzle_data = generate_puzzle_country(level)
    elapsed = time.monotonic() - t0

    print(json.dumps(puzzle_data, indent=2, default=str))
    meta = puzzle_data["metadata"]
    print(f"\nLevel: {level}")
    print(f"Grid: {meta['db_w']}×{meta['db_h']}")
    print(f"Rooms: {meta['num_rooms']} ({meta['num_clued_rooms']} clued)")
    print(f"Generated in {elapsed:.4f}s")
    print(f"\nPlay: {puzzle_data['puzzlink_url']}")
