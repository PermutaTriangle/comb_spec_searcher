from tilescopetwo import TileScopeTWO, StrategyPacks

basis = '012'

strategies = StrategyPacks.row_and_column_placements_with_subobstruction_inferral

tilescope = TileScopeTWO(basis, strategies, interleaving_decomposition=True,
                         complement_verify=True, symmetry=True, compress=False,
                         forward_equivalence=False)

tree = tilescope.auto_search(cap=1)

tree.pretty_print()
print(tree.to_json())

alt_tree = tilescope.alternative_get_proof_tree()

alt_tree.pretty_print()

root = alt_tree.root
#
# print("---------root---------")
# for o in root.eqv_path_objects:
#     print(o)
#     print()
#
# for child in root.children:
#     print("---------child---------")
#     for i, o in enumerate(child.eqv_path_objects):
#         print(o)
#         print()
#         if len(child.eqv_explanations) != i:
#             explanation = child.eqv_explanations[i]
#             print(explanation)
#             print()
#
#     for childchild in child.children:
#         print("---------childchild---------")
#         for i, o in enumerate(childchild.eqv_path_objects):
#             print(o)
#             print()
#             if len(childchild.eqv_explanations) != i:
#                 explanation = childchild.eqv_explanations[i]
#                 print(explanation)
#                 print()
#
#         for childchildchild in childchild.children:
#             print("---------childchildchild---------")
#             for i, o in enumerate(childchildchild.eqv_path_objects):
#                 print(o)
#                 print()
#                 if len(childchildchild.eqv_explanations) != i:
#                     explanation = childchildchild.eqv_explanations[i]
#                     print(explanation)
#                     print()
#             for childchildchildchild in childchildchild.children:
#                 print("---------childchildchildchild---------")
#                 for i, o in enumerate(childchildchildchild.eqv_path_objects):
#                     print(o)
#                     print()
#                     if len(childchildchildchild.eqv_explanations) != i:
#                         explanation = childchildchildchild.eqv_explanations[i]
#                         print(explanation)
#                         print()
#                 for childchildchildchildchild in childchildchildchild.children:
#                     print("---------childchildchildchildchild---------")
#                     for i, o in enumerate(childchildchildchildchild.eqv_path_objects):
#                         print(o)
#                         print()
#                         if len(childchildchildchildchild.eqv_explanations) != i:
#                             explanation = childchildchildchildchild.eqv_explanations[i]
#                             print(explanation)
#                             print()
