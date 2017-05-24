from atrap import MetaTree
from permuta import Perm


from time import time
from atrap.strategies import *
from atrap.ProofTree import ProofTree

from json import loads

js = loads('''{"root": {"children": [{"children": [], "formal_step": "Verified because it is a one by one tiling with a subclass", "identifier": 1153, "in_tiling": {}, "out_tiling": {}, "recurse": "[]", "relation": ""}, {"children": [{"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1154, "in_tiling": {"[0, 1]": "point", "[1, 0]": "Av(Perm((0, 1, 2)), Perm((2, 3, 0, 1)))"}, "out_tiling": {"[0, 1]": "point", "[1, 0]": "Av(Perm((0, 1, 2)), Perm((2, 3, 0, 1)))"}, "recurse": "[]", "relation": ""}, {"children": [{"children": [{"children": [{"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1155, "in_tiling": {"[0, 0]": "point", "[1, 2]": "point", "[2, 1]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))"}, "out_tiling": {"[0, 0]": "point", "[1, 2]": "point", "[2, 1]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))"}, "recurse": "[]", "relation": ""}, {"children": [{"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1156, "in_tiling": {"[0, 2]": "point", "[1, 4]": "point", "[2, 1]": "point", "[3, 0]": "Av(Perm((0, 1)))", "[3, 3]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 2]": "point", "[1, 4]": "point", "[2, 1]": "point", "[3, 0]": "Av(Perm((0, 1)))", "[3, 3]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": ""}, {"children": [{"children": [{"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1157, "in_tiling": {"[0, 2]": "point", "[1, 5]": "Av(Perm((0, 1)))", "[2, 4]": "point", "[3, 1]": "point", "[4, 0]": "Av(Perm((0, 1)))", "[4, 3]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 2]": "point", "[1, 5]": "Av(Perm((0, 1)))", "[2, 4]": "point", "[3, 1]": "point", "[4, 0]": "Av(Perm((0, 1)))", "[4, 3]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": ""}, {"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1158, "in_tiling": {"[0, 2]": "point", "[1, 6]": "Av(Perm((0, 1)))", "[2, 4]": "point", "[3, 1]": "point", "[4, 0]": "Av(Perm((0, 1)))", "[5, 5]": "point", "[6, 3]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 2]": "point", "[1, 6]": "Av(Perm((0, 1)))", "[2, 4]": "point", "[3, 1]": "point", "[4, 0]": "Av(Perm((0, 1)))", "[5, 5]": "point", "[6, 3]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": ""}], "formal_step": "We perform cell insertion into cell (4, 5); either it is empty or Av+(Perm((0, 1)), Perm((1, 0))).", "identifier": 1159, "in_tiling": {"[0, 2]": "point", "[1, 6]": "Av(Perm((0, 1)))", "[2, 4]": "point", "[3, 1]": "point", "[4, 0]": "Av(Perm((0, 1)))", "[4, 3]": "Av(Perm((0, 1)))", "[4, 5]": "Av(Perm((0, 1)), Perm((1, 0)))"}, "out_tiling": {"[0, 2]": "point", "[1, 6]": "Av(Perm((0, 1)))", "[2, 4]": "point", "[3, 1]": "point", "[4, 0]": "Av(Perm((0, 1)))", "[4, 3]": "Av(Perm((0, 1)))", "[4, 5]": "Av(Perm((0, 1)), Perm((1, 0)))"}, "recurse": "[]", "relation": ""}, {"children": [], "formal_step": "Verified because it is a one by one tiling with a subclass", "identifier": 3, "in_tiling": {"[0, 0]": "point"}, "out_tiling": {"[0, 0]": "point"}, "recurse": "[]", "relation": ""}], "formal_step": "Reversibly delete the points at cells [Cell(i=1, j=7)]", "identifier": 1160, "in_tiling": {"[0, 2]": "point", "[1, 4]": "point", "[2, 3]": "Av+(Perm((0, 1)))", "[3, 1]": "point", "[4, 0]": "Av(Perm((0, 1)))", "[4, 3]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 2]": "point", "[1, 7]": "point", "[2, 6]": "Av(Perm((0, 1)))", "[3, 4]": "point", "[4, 1]": "point", "[5, 0]": "Av(Perm((0, 1)))", "[5, 3]": "Av(Perm((0, 1)))", "[5, 5]": "Av(Perm((0, 1)), Perm((1, 0)))"}, "recurse": "[{Cell(i=0, j=2): Cell(i=0, j=2), Cell(i=1, j=6): Cell(i=2, j=6), Cell(i=2, j=4): Cell(i=3, j=4), Cell(i=3, j=1): Cell(i=4, j=1), Cell(i=4, j=0): Cell(i=5, j=0), Cell(i=4, j=3): Cell(i=5, j=3), Cell(i=4, j=5): Cell(i=5, j=5)}, {Cell(i=0, j=0): Cell(i=1, j=7)}]", "relation": "| Inserting the bottom most point in to the cell Cell(i=2, j=3). | "}], "formal_step": "We perform cell insertion into cell (2, 3); either it is empty or Av+(Perm((0, 1))).", "identifier": 1161, "in_tiling": {"[0, 1]": "point", "[1, 3]": "point", "[2, 0]": "Av+(Perm((0, 1)))", "[2, 2]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))"}, "out_tiling": {"[0, 2]": "point", "[1, 4]": "point", "[2, 3]": "Av(Perm((0, 1)))", "[3, 1]": "point", "[4, 0]": "Av(Perm((0, 1)))", "[4, 3]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": "| Inserting the top most point in to the cell Cell(i=2, j=0). | "}], "formal_step": "We perform cell insertion into cell (2, 0); either it is empty or Av+(Perm((0, 1))).", "identifier": 1162, "in_tiling": {"[0, 1]": "point", "[1, 3]": "point", "[2, 0]": "Av(Perm((0, 1)))", "[2, 2]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))"}, "out_tiling": {"[0, 1]": "point", "[1, 3]": "point", "[2, 0]": "Av(Perm((0, 1)))", "[2, 2]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))"}, "recurse": "[]", "relation": ""}, {"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1163, "in_tiling": {"[0, 0]": "point", "[1, 2]": "point", "[2, 3]": "point", "[3, 1]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 0]": "point", "[1, 2]": "point", "[2, 3]": "point", "[3, 1]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": ""}], "formal_step": "We perform cell insertion into cell (1, 3); either it is empty or Av+(Perm((0, 1)), Perm((1, 0))).", "identifier": 1164, "in_tiling": {"[0, 1]": "point", "[1, 3]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 4]": "point", "[3, 0]": "Av(Perm((0, 1)))", "[3, 2]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))"}, "out_tiling": {"[0, 1]": "point", "[1, 3]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 4]": "point", "[3, 0]": "Av(Perm((0, 1)))", "[3, 2]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))"}, "recurse": "[]", "relation": ""}, {"children": [{"children": [{"children": [{"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1165, "in_tiling": {"[0, 1]": "point", "[1, 0]": "Av+(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))", "[2, 2]": "point"}, "out_tiling": {"[0, 1]": "point", "[1, 0]": "Av+(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))", "[2, 2]": "point"}, "recurse": "[]", "relation": ""}, {"children": [{"children": [{"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1166, "in_tiling": {"[0, 4]": "point", "[1, 3]": "Av(Perm((0, 1)))", "[2, 2]": "point", "[3, 0]": "Av(Perm((0, 1)))", "[4, 5]": "point", "[5, 1]": "point", "[6, 0]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 4]": "point", "[1, 3]": "Av(Perm((0, 1)))", "[2, 2]": "point", "[3, 0]": "Av(Perm((0, 1)))", "[4, 5]": "point", "[5, 1]": "point", "[6, 0]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": ""}, {"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1167, "in_tiling": {"[0, 6]": "point", "[1, 5]": "Av(Perm((0, 1)))", "[2, 1]": "point", "[3, 4]": "point", "[4, 0]": "Av(Perm((0, 1)))", "[5, 7]": "point", "[6, 3]": "point", "[7, 2]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 6]": "point", "[1, 5]": "Av(Perm((0, 1)))", "[2, 1]": "point", "[3, 4]": "point", "[4, 0]": "Av(Perm((0, 1)))", "[5, 7]": "point", "[6, 3]": "point", "[7, 2]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": ""}], "formal_step": "We perform cell insertion into cell (2, 0); either it is empty or Av+(Perm((0, 1)), Perm((1, 0))).", "identifier": 1168, "in_tiling": {"[0, 2]": "point", "[1, 0]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 1]": "point", "[3, 0]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))", "[4, 3]": "point", "[5, 0]": "Av+(Perm((0, 1)))"}, "out_tiling": {"[0, 4]": "point", "[1, 3]": "Av(Perm((0, 1)))", "[2, 0]": "Av(Perm((0, 1)), Perm((1, 0)))", "[3, 2]": "point", "[4, 0]": "Av(Perm((0, 1)))", "[5, 5]": "point", "[6, 1]": "point", "[7, 0]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": "| Inserting the top most point in to the cell Cell(i=5, j=0). | The reverse of: Inserting the top most point in to the cell Cell(i=1, j=2). | Inserting the bottom most point in to the cell Cell(i=1, j=2). | "}, {"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1169, "in_tiling": {"[0, 2]": "point", "[1, 0]": "Av+(Perm((0, 1)))", "[2, 3]": "point", "[3, 1]": "point", "[4, 0]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 4]": "point", "[1, 1]": "point", "[2, 0]": "Av(Perm((0, 1)))", "[3, 5]": "point", "[4, 3]": "point", "[5, 2]": "Av(Perm((0, 1)))", "[6, 0]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": "| Inserting the top most point in to the cell Cell(i=1, j=0). | "}], "formal_step": "Placing the maximum point into row 0", "identifier": 1170, "in_tiling": {"[0, 1]": "point", "[1, 0]": "Av+(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))", "[2, 2]": "point", "[3, 0]": "Av+(Perm((0, 1)))"}, "out_tiling": {"[0, 1]": "point", "[1, 0]": "Av+(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))", "[2, 2]": "point", "[3, 0]": "Av+(Perm((0, 1)))"}, "recurse": "[]", "relation": ""}], "formal_step": "We perform cell insertion into cell (3, 0); either it is empty or Av+(Perm((0, 1))).", "identifier": 1171, "in_tiling": {"[0, 4]": "point", "[1, 1]": "point", "[2, 3]": "Av(Perm((0, 1)), Perm((1, 0)))", "[3, 0]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))", "[4, 5]": "point", "[5, 2]": "Av(Perm((0, 1)))", "[6, 0]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 1]": "point", "[1, 0]": "Av+(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))", "[2, 2]": "point", "[3, 0]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": "| The reverse of: Inserting the left most point in to the cell Cell(i=1, j=0). | "}, {"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1172, "in_tiling": {"[0, 2]": "point", "[1, 3]": "point", "[2, 1]": "point", "[3, 0]": "Av(Perm((0, 1)))", "[4, 4]": "point"}, "out_tiling": {"[0, 2]": "point", "[1, 3]": "point", "[2, 1]": "Av(Perm((0, 1)))", "[3, 0]": "point", "[4, 4]": "point"}, "recurse": "[]", "relation": "| The reverse of: Inserting the top most point in to the cell Cell(i=2, j=0). | Inserting the bottom most point in to the cell Cell(i=2, j=0). | "}], "formal_step": "We perform cell insertion into cell (1, 5); either it is empty or Av+(Perm((0, 1)), Perm((1, 0))).", "identifier": 1173, "in_tiling": {"[0, 4]": "point", "[1, 5]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 1]": "point", "[3, 3]": "Av(Perm((0, 1)), Perm((1, 0)))", "[4, 0]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))", "[5, 6]": "point", "[6, 2]": "Av(Perm((0, 1)))", "[7, 0]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 4]": "point", "[1, 5]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 1]": "point", "[3, 3]": "Av(Perm((0, 1)), Perm((1, 0)))", "[4, 0]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))", "[5, 6]": "point", "[6, 2]": "Av(Perm((0, 1)))", "[7, 0]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": ""}, {"children": [{"children": [{"children": [{"children": [{"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1174, "in_tiling": {"[0, 1]": "point", "[1, 2]": "point", "[2, 0]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 1]": "point", "[1, 2]": "point", "[2, 0]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": ""}, {"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1175, "in_tiling": {"[0, 0]": "point", "[1, 1]": "point", "[2, 2]": "point"}, "out_tiling": {"[0, 0]": "point", "[1, 1]": "point", "[2, 2]": "point"}, "recurse": "[]", "relation": ""}], "formal_step": "We perform cell insertion into cell (1, 2); either it is empty or Av+(Perm((0, 1)), Perm((1, 0))).", "identifier": 1176, "in_tiling": {"[0, 1]": "point", "[1, 2]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 3]": "point", "[3, 0]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 1]": "point", "[1, 2]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 3]": "point", "[3, 0]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": ""}, {"children": [], "formal_step": "Verified because it is a one by one tiling with a subclass", "identifier": 1, "in_tiling": {"[0, 0]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 0]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": ""}, {"children": [], "formal_step": "recurse", "identifier": 3, "in_tiling": {"[0, 0]": "point"}, "out_tiling": {"[0, 0]": "point"}, "recurse": "[]", "relation": ""}, {"children": [], "formal_step": "Verified because it is a one by one tiling with a subclass", "identifier": 177, "in_tiling": {"[0, 0]": "Av+(Perm((0, 1)))"}, "out_tiling": {"[0, 0]": "Av+(Perm((0, 1)))"}, "recurse": "[]", "relation": ""}], "formal_step": "Reversibly delete the points at cells [Cell(i=2, j=2), Cell(i=3, j=1), Cell(i=5, j=4)]", "identifier": 1177, "in_tiling": {"[0, 4]": "point", "[1, 7]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 3]": "Av(Perm((0, 1)))", "[3, 2]": "point", "[4, 8]": "point", "[5, 1]": "Av(Perm((0, 1)))", "[5, 6]": "Av(Perm((0, 1)))", "[6, 5]": "point", "[7, 0]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 3]": "point", "[1, 5]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 2]": "Av(Perm((0, 1)))", "[3, 1]": "point", "[4, 6]": "point", "[5, 0]": "Av(Perm((0, 1)))", "[5, 4]": "Av+(Perm((0, 1)))"}, "recurse": "[{Cell(i=0, j=1): Cell(i=0, j=3), Cell(i=1, j=2): Cell(i=1, j=5), Cell(i=2, j=3): Cell(i=4, j=6), Cell(i=3, j=0): Cell(i=5, j=0)}, {Cell(i=0, j=0): Cell(i=2, j=2)}, {Cell(i=0, j=0): Cell(i=3, j=1)}, {Cell(i=0, j=0): Cell(i=5, j=4)}]", "relation": "| The reverse of: Inserting the bottom most point in to the cell Cell(i=5, j=4). | "}, {"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1178, "in_tiling": {"[0, 4]": "point", "[1, 3]": "Av(Perm((0, 1)))", "[2, 1]": "point", "[3, 7]": "point", "[4, 6]": "Av(Perm((0, 1)))", "[5, 2]": "point", "[6, 0]": "Av(Perm((0, 1)))", "[7, 5]": "point"}, "out_tiling": {"[0, 4]": "Av(Perm((0, 1)))", "[1, 3]": "point", "[2, 1]": "point", "[3, 7]": "point", "[4, 6]": "Av(Perm((0, 1)))", "[5, 2]": "point", "[6, 0]": "Av(Perm((0, 1)))", "[7, 5]": "point"}, "recurse": "[]", "relation": "| The reverse of: Inserting the top most point in to the cell Cell(i=0, j=3). | Inserting the bottom most point in to the cell Cell(i=0, j=3). | "}], "formal_step": "We perform cell insertion into cell (5, 3); either it is empty or Av+(Perm((0, 1)), Perm((1, 0))).", "identifier": 1179, "in_tiling": {"[0, 5]": "point", "[1, 8]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 4]": "Av(Perm((0, 1)))", "[3, 2]": "point", "[4, 9]": "point", "[5, 1]": "Av(Perm((0, 1)))", "[5, 3]": "Av(Perm((0, 1)), Perm((1, 0)))", "[5, 7]": "Av(Perm((0, 1)))", "[6, 6]": "point", "[7, 0]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 5]": "point", "[1, 8]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 4]": "Av(Perm((0, 1)))", "[3, 2]": "point", "[4, 9]": "point", "[5, 1]": "Av(Perm((0, 1)))", "[5, 3]": "Av(Perm((0, 1)), Perm((1, 0)))", "[5, 7]": "Av(Perm((0, 1)))", "[6, 6]": "point", "[7, 0]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": ""}, {"children": [{"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1180, "in_tiling": {"[0, 5]": "point", "[1, 4]": "Av(Perm((0, 1)))", "[2, 2]": "Av(Perm((0, 1)))", "[3, 1]": "point", "[4, 8]": "point", "[5, 7]": "Av(Perm((0, 1)))", "[6, 6]": "point", "[7, 3]": "point", "[8, 2]": "Av(Perm((0, 1)))", "[9, 0]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 5]": "point", "[1, 4]": "Av(Perm((0, 1)))", "[2, 2]": "Av(Perm((0, 1)))", "[3, 1]": "point", "[4, 8]": "point", "[5, 7]": "Av(Perm((0, 1)))", "[6, 6]": "point", "[7, 4]": "Av(Perm((0, 1)))", "[8, 3]": "point", "[9, 0]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": "| The reverse of: Inserting the top most point in to the cell Cell(i=6, j=2). | Inserting the bottom most point in to the cell Cell(i=6, j=2). | "}, {"children": [], "formal_step": "The tiling is a subset of the subclass", "identifier": 1181, "in_tiling": {"[0, 5]": "point", "[1, 4]": "Av(Perm((0, 1)))", "[2, 0]": "point", "[3, 8]": "point", "[4, 7]": "Av(Perm((0, 1)))", "[5, 3]": "point", "[6, 6]": "point", "[7, 2]": "point", "[8, 1]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 5]": "point", "[1, 4]": "Av(Perm((0, 1)))", "[2, 0]": "point", "[3, 8]": "point", "[4, 7]": "Av(Perm((0, 1)))", "[5, 3]": "point", "[6, 6]": "point", "[7, 2]": "Av(Perm((0, 1)))", "[8, 1]": "point"}, "recurse": "[]", "relation": "| The reverse of: Inserting the top most point in to the cell Cell(i=7, j=1). | Inserting the bottom most point in to the cell Cell(i=7, j=1). | "}], "formal_step": "We perform cell insertion into cell (6, 4); either it is empty or Av+(Perm((0, 1)), Perm((1, 0))).", "identifier": 1182, "in_tiling": {"[0, 3]": "point", "[1, 2]": "Av(Perm((0, 1)))", "[2, 1]": "point", "[3, 6]": "point", "[4, 5]": "Av(Perm((0, 1)))", "[5, 2]": "Av(Perm((0, 1)), Perm((1, 0)))", "[6, 4]": "point", "[7, 2]": "Av+(Perm((0, 1)))", "[8, 0]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 6]": "point", "[1, 5]": "Av(Perm((0, 1)))", "[10, 0]": "Av(Perm((0, 1)))", "[2, 2]": "Av(Perm((0, 1)))", "[3, 1]": "point", "[4, 9]": "point", "[5, 8]": "Av(Perm((0, 1)))", "[6, 4]": "Av(Perm((0, 1)), Perm((1, 0)))", "[7, 7]": "point", "[8, 3]": "point", "[9, 2]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": "| Inserting the top most point in to the cell Cell(i=7, j=2). | "}], "formal_step": "We perform cell insertion into cell (7, 3); either it is empty or Av+(Perm((0, 1))).", "identifier": 1183, "in_tiling": {"[0, 3]": "point", "[1, 5]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 1]": "point", "[3, 0]": "Av(Perm((0, 1)))", "[4, 6]": "point", "[5, 0]": "Av(Perm((0, 1)))", "[5, 2]": "Av(Perm((0, 1)))", "[5, 4]": "Av+(Perm((0, 1)))"}, "out_tiling": {"[0, 4]": "point", "[1, 7]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 3]": "Av(Perm((0, 1)))", "[3, 2]": "point", "[4, 8]": "point", "[5, 1]": "Av(Perm((0, 1)))", "[5, 3]": "Av(Perm((0, 1)), Perm((1, 0)))", "[5, 6]": "Av(Perm((0, 1)))", "[6, 5]": "point", "[7, 3]": "Av(Perm((0, 1)))", "[8, 0]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": "| The reverse of: Inserting the top most point in to the cell Cell(i=2, j=0). | Inserting the bottom most point in to the cell Cell(i=2, j=0). | Inserting the bottom most point in to the cell Cell(i=5, j=4). | "}], "formal_step": "We perform cell insertion into cell (6, 5); either it is empty or Av+(Perm((0, 1))).", "identifier": 1184, "in_tiling": {"[0, 1]": "point", "[1, 3]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 0]": "Av+(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))", "[3, 4]": "point", "[4, 0]": "Av(Perm((0, 1)))", "[4, 2]": "Av(Perm((0, 1)))"}, "out_tiling": {"[0, 4]": "point", "[1, 6]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 1]": "point", "[3, 3]": "Av(Perm((0, 1)), Perm((1, 0)))", "[4, 0]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))", "[5, 7]": "point", "[6, 0]": "Av(Perm((0, 1)))", "[6, 2]": "Av(Perm((0, 1)))", "[6, 5]": "Av(Perm((0, 1)))"}, "recurse": "[]", "relation": "| Inserting the left most point in to the cell Cell(i=2, j=0). | "}], "formal_step": "We perform cell insertion into cell (2, 0); either it is empty or Av+(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1))).", "identifier": 1185, "in_tiling": {"[0, 0]": "Av+(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))", "[1, 1]": "point", "[2, 0]": "Av(Perm((0, 1, 2)), Perm((2, 3, 0, 1)))"}, "out_tiling": {"[0, 1]": "point", "[1, 3]": "Av(Perm((0, 1)), Perm((1, 0)))", "[2, 0]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))", "[3, 4]": "point", "[4, 0]": "Av(Perm((0, 1)))", "[4, 2]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))"}, "recurse": "[]", "relation": "| Inserting the left most point in to the cell Cell(i=0, j=0). | "}], "formal_step": "We perform cell insertion into cell (0, 0); either it is empty or Av+(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1))).", "identifier": 1186, "in_tiling": {"[0, 0]": "Av+(Perm((0, 1, 2, 3)), Perm((0, 1, 3, 2)), Perm((0, 2, 1, 3)), Perm((1, 0, 2, 3)), Perm((1, 2, 3, 0)), Perm((2, 3, 0, 1)), Perm((3, 0, 1, 2)))"}, "out_tiling": {"[0, 0]": "Av(Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 3, 0, 1)))", "[1, 1]": "point", "[2, 0]": "Av(Perm((0, 1, 2)), Perm((2, 3, 0, 1)))"}, "recurse": "[]", "relation": "| Inserting the top most point in to the cell Cell(i=0, j=0). | "}], "formal_step": "We perform cell insertion into cell (0, 0); either it is empty or Av+(Perm((0, 1, 2, 3)), Perm((0, 1, 3, 2)), Perm((0, 2, 1, 3)), Perm((1, 0, 2, 3)), Perm((1, 2, 3, 0)), Perm((2, 3, 0, 1)), Perm((3, 0, 1, 2))).", "identifier": 1187, "in_tiling": {"[0, 0]": "Av(Perm((0, 1, 2, 3)), Perm((0, 1, 3, 2)), Perm((0, 2, 1, 3)), Perm((1, 0, 2, 3)), Perm((1, 2, 3, 0)), Perm((2, 3, 0, 1)), Perm((3, 0, 1, 2)))"}, "out_tiling": {"[0, 0]": "Av(Perm((0, 1, 2, 3)), Perm((0, 1, 3, 2)), Perm((0, 2, 1, 3)), Perm((1, 0, 2, 3)), Perm((1, 2, 3, 0)), Perm((2, 3, 0, 1)), Perm((3, 0, 1, 2)))"}, "recurse": "[]", "relation": ""}}''')

tree = ProofTree._from_attr_dict(js)
print(tree.get_genf())

# all_strategies = [ [all_cell_insertions, all_row_placements, all_column_placements], [all_point_placements, all_equivalent_row_placements, all_equivalent_column_placements, all_symmetric_tilings], [empty_cell_inferral, subclass_inferral, row_and_column_separation], [splittings, reversibly_deletable_cells, components], [subset_verified, is_empty] ]
#
# mimic_regular_insertion_encoding = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral], [reversibly_deletable_points], [one_by_one_verification, is_empty]]
#
# standard_strategies = [ [all_cell_insertions], [point_separation, all_point_placements, all_symmetric_tilings], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [splittings], [subset_verified, is_empty] ]
# # standard_strategies = [ [all_cell_insertions], [all_point_placements, all_symmetric_tilings], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [splittings], [subset_verified, is_empty] ]
# standard_strategies_w_all_row_cols = [ [all_cell_insertions, all_row_placements, all_column_placements], [all_equivalent_row_placements, all_equivalent_column_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]
#
# standard_strategies_w_all_row_cols_and_point_separation = [ [all_cell_insertions, all_row_placements, all_column_placements, all_point_isolations], [point_separation, all_equivalent_point_isolations, all_equivalent_row_placements, all_equivalent_column_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]
#
# standard_strategies_w_point_separation_and_isolation = [ [all_cell_insertions, all_point_isolations], [point_separation, all_equivalent_point_isolations], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [components, reversibly_deletable_cells], [subset_verified, is_empty] ]
# enum_sch = [ [all_cell_insertions, all_point_isolations], [point_separation, all_equivalent_point_isolations], [empty_cell_inferral], [reversibly_deletable_cells], [subset_verified, is_empty] ]
#
# # finite_strategies = [ [all_cell_insertions, all_row_placements], [all_equivalent_row_placements], [empty_cell_inferral, subclass_inferral], [], [subset_verified, is_empty] ]
# finite_strategies_w_min_row = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [], [subset_verified, is_empty] ]
# finite_strategies_w_point_pl = [ [all_cell_insertions], [all_point_placements], [empty_cell_inferral, row_and_column_separation, subclass_inferral], [], [subset_verified, is_empty] ]
#
# finite_strategies = [ [all_cell_insertions, all_minimum_row_placements], [all_equivalent_minimum_row_placements], [empty_cell_inferral, subclass_inferral], [], [subset_verified, is_empty] ]
#
# basic = [ [all_cell_insertions], [all_maximum_point_placements], [row_and_column_separation], [reversibly_deletable_cells], [one_by_one_verification] ]
#
# # mtree = MetaTree([Perm((0,2,1)), Perm((3,2,1,0))], *standard_strategies)
#
# # mtree = MetaTree(descriptors.Basis([Perm((0,1,2,3))]))
#
# # mtree = MetaTree([Perm((0,2,1))], recursive_strategies=[components], verification_strategies=[subset_verified] )
#
# # mtree = MetaTree(descriptors.Basis([Perm((0,1))]))
#
# # mtree = MetaTree([Perm((0,1,2))], *standard_strategies)
#
# # mtree = MetaTree([])
#
# # mtree = MetaTree([Perm((0,2,1)), Perm((0,1,2,3)), Perm((3,2,0,1)), Perm((2,3,0,1))], *all_strategies )
#
# # mtree = MetaTree([Perm((0,2,1)), Perm((0,1,2))], *mimic_regular_insertion_encoding )
#
# # mtree = MetaTree([Perm((1,3,0,2)), Perm((2,0,3,1))], *all_strategies)
# #
# # task = '012_2103_2301'
#
# # task = '1234_1243_1324_1342_1423_1432_2134_2143_2314_2341_3214'
#
# # task = '012_2301'
#
# # task = '012_0321_2103'
#
# # task = '012_0321_1032_2103'
# #
# # task = '012_1032_2301_2310'
#
# # task = '012_3210'
# # task = '0'
# #
# # task = '0123'
# # task = '0213'
# # task = '012'
#
# # task = '021'
#
# # task = '123'
#
# # task = '0'
#
# # task = '0132_0213_0231_3120'
#
# # task = '0213_0231'
#
# # task = "1302_2031"
#
# # task = '0231_1230_3012'
#
# # task = '0231_0321'
#
# # patts = [ Perm([ int(c) - 1 for c in p ]) for p in task.split('_') ]
#
# #
# # mtree = MetaTree( patts, *mimic_regular_insertion_encoding )
# task = '0123_0132_0213_0231_0312_1023_1203_1230_2013_2301_3012'
# patts = [ Perm([ int(c) for c in p ]) for p in task.split('_') ]
#
# row_and_column_placements = [
#     [all_cell_insertions, all_row_placements, all_column_placements],
#     [all_equivalent_row_placements, all_equivalent_column_placements],
#     [empty_cell_inferral, row_and_column_separation, subclass_inferral],
#     [components, reversibly_deletable_cells],
#     [subset_verified, is_empty]]
#
# row_and_column_placements_and_splittings = [
#     [all_cell_insertions, all_row_placements, all_column_placements],
#     [all_equivalent_row_placements, all_equivalent_column_placements],
#     [empty_cell_inferral, row_and_column_separation, subclass_inferral],
#     [splittings],
#     [subset_verified, is_empty]]
#
# # strategies = row_and_column_placements
# strategies = row_and_column_placements_and_splittings
# # strategies = enum_sch
#
# mtree = MetaTree( patts, *strategies )
#
# print("Using the strategies:")
# print(strategies)
#
# print(mtree.basis)
#
#
# def count_verified_tilings(mt):
#     count = 0
#     for tiling, or_node in mt.tiling_cache.items():
#         if or_node.sibling_node.is_verified():
#             count += 1
#     return count
#
# def count_sibling_nodes(mt):
#     s = set()
#     verified = 0
#     for tiling, or_node in mt.tiling_cache.items():
#         if or_node.sibling_node in s:
#             continue
#         if or_node.sibling_node.is_verified():
#             verified += 1
#         s.add(or_node.sibling_node)
#     return len(s), verified
#
# #mtree.do_level()
# start = time()
# max_time = 500
# while not mtree.has_proof_tree():
#     print("===============================")
#     mtree.do_level(max_time=max_time)
#     print("We had {} inferral cache hits and {} partitioning cache hits.".format(mtree.inferral_cache_hits, mtree.partitioning_cache_hits))
#     print("The partitioning cache has {} tilings in it right now.".format( len(mtree._basis_partitioning_cache) ) )
#     print("The inferral cache has {} tilings in it right now.".format( len(mtree._inferral_cache) ) )
#     print("There are {} tilings in the search tree.".format( len(mtree.tiling_cache)))
#     print("There are {} verified tilings.".format(count_verified_tilings(mtree)))
#     print("There are {} SiblingNodes of which {} are verified.".format(*count_sibling_nodes(mtree)))
#     print("Time taken so far is {} seconds.".format( time() - start ) )
#     print("")
#     for function_name, calls in mtree._partitioning_calls.items():
#         print("The function {} called the partitioning cache *{}* times, ({} originating)".format(function_name, calls[0], calls[1]))
#     print("There were {} cache misses".format(mtree._cache_misses))
#     if mtree.depth_searched == 8 or mtree.timed_out:# or time() - start > max_time:
#         break
#
# if mtree.has_proof_tree():
#     proof_tree = mtree.find_proof_tree()
#     proof_tree.pretty_print()
#     json = proof_tree.to_json(indent="  ")
#     print(json)
#     assert ProofTree.from_json(json).to_json(indent="  ") == json
#
# end = time()
#
# print("I took", end - start, "seconds")
