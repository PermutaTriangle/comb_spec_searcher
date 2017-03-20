from atrap import *
from permuta import *
import sys

def all_strategies(tiling, input_set):
    # for strategy in all_cell_insertions(tiling, input_set):
    #     yield strategy
    for strategy in all_row_and_column_insertions(tiling, input_set):
        yield strategy
# input_set = Tile.INCREASING
# input_set = Tile.DECREASING
# input_set = PermSet.avoiding([Perm((0, 1)), Perm((1, 0))])
# input_set = PermSet.avoiding([Perm((0, 2, 1))])
# input_set = PermSet.avoiding([Perm((0, 2, 1)), Perm((2, 0, 1))])
# input_set = PermSet.avoiding([Perm((1, 2, 0))])
# input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((1, 2, 0))])
# input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2))])
# input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((0, 2, 1))])
# input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((2, 1, 0))])
# input_set = PermSet.avoiding([Perm((0,2,1)), Perm((1,2,0)), Perm((1,0,2)), Perm((2,0,1)) ])
input_set = PermSet.avoiding([Perm((0,1,2,3)), Perm((2,3,1,0))])


T = Tiling({(0, 0): input_set})

print("Our tiling:")
print()
print(T)
print()

print( "Doing all row and column insertions" )
for description, strategy in all_strategies(T, input_set):
    print("--------")
    print("--------", description)
    print("--------")
    for new_tiling in strategy:
        myStr = new_tiling.__str__()
        print('--------', '-------- '.join(myStr.splitlines(True)))
        if verify_tiling(new_tiling, input_set):
            print("--------", "Tiling is verified")
            print("--------")
        else:
            print("--------", "Tiling is NOT verified")
            print("--------")
            print("---------------- We will now look at strategies on the tiling:")
            print('----------------', '---------------- '.join(myStr.splitlines(True)))

            for second_description, second_strategy in all_strategies(new_tiling, input_set):
                print("----------------")
                print("----------------", second_description)
                print("----------------", )
                for second_new_tiling in second_strategy:
                    myStr = second_new_tiling.__str__()
                    print('----------------', '---------------- '.join(myStr.splitlines(True)))
                    if verify_tiling(second_new_tiling, input_set):
                        print("----------------", "Tiling is verified")
                        print("----------------")
                    else:
                        print("----------------", "Tiling is NOT verified")
                        print("----------------")
            print("--------")



# T = Tiling({(0, 0): input_set})
#
# print("Our tiling:")
# print()
# print(T)
# print()
#
# print("Doing row insertion first step")
#
# empty_row, row_cells = row_insertion_helper(T, 0)
#
# print("Emptied row")
# print()
# print(empty_row)
# print()
# print("The cells in the row are")
# print(row_cells)
# print()
#
# print("Now inserting minimum into the row")
# for letter, strategy in row_insertion(T, 0, input_set):
#     print(letter)
#     print("now printing all tilings from inserting into row")
#     for tiling in strategy:
#         print ()
#         print(tiling)
#         print()
#         tiling_verified = verify_tiling(tiling, input_set)
#         if tiling_verified:
#             print("Tiling was verified")
#         else:
#             print("Tiling was NOT verified")
#             if letter == "B":
#                 print("GOING FOR ROUND TWO!!")
#                 print("we will now try inserting into the following tile:")
#                 print(tiling)
#                 print(dict(tiling))
#                 print()
#                 print("now printing all tilings from inserting into top row")
#                 for letter2, strategy2 in row_insertion(tiling, 0, input_set):
#                     print(letter2)
#
#                     for tiling2 in strategy2:
#                         print()
#                         print(tiling2)
#                         print(dict(tiling2))
#                         print()
#                         tiling_verified2 = verify_tiling(tiling2, input_set)
#                         if tiling_verified2:
#                             print("Tiling was verified")
#                         else:
#                             print("Tiling was NOT verified")
#             else:
#                 print("GOING FOR ROUND TWO!!")
#                 print("we will now try inserting into the following tile:")
#                 print(tiling)
#                 print(dict(tiling))
#                 print()
#                 print("now printing all tilings from inserting into bottom row")
#                 for letter2, strategy2 in row_insertion(tiling, 1, input_set):
#                     print(letter2)
#                     for tiling2 in strategy2:
#                         print()
#                         print(tiling2)
#                         print(dict(tiling2))
#                         print()
#                         tiling_verified2 = verify_tiling(tiling2, input_set)
#                         if tiling_verified2:
#                             print("Tiling was verified")
#                         else:
#                             print("Tiling was NOT verified")
#             print("===back to round one===")
#     print("=================")
#
# #
# # T = Tiling({(0, 0): input_set})
# #
# # print("Our tiling:")
# # print()
# # print(T)
# # print()
# #
# # print("Doing column insertion first step")
# #
# # empty_column, column_cells = column_insertion_helper(T, 0)
# #
# # print("Emptied column")
# # print()
# # print(empty_column)
# # print()
# # print("The cells in the column are")
# # print(column_cells)
# # print()
# #
# # print("Now inserting minimum into the column")
# # for letter, strategy in column_insertion(T, 0, input_set):
# #     print(letter)
# #     print("now printing all tilings from inserting into column")
# #     for tiling in strategy:
# #         print ()
# #         print(tiling)
# #         print()
# #         tiling_verified = verify_tiling(tiling, input_set)
# #         if tiling_verified:
# #             print("Tiling was verified")
# #         else:
# #             print("Tiling was NOT verified")
# #             if letter == "L":
# #                 print("GOING FOR ROUND TWO!!")
# #                 print("we will now try inserting into the following tile:")
# #                 print(tiling)
# #                 print(dict(tiling))
# #                 print()
# #                 print("now printing all tilings from inserting into right column")
# #                 for letter2, strategy2 in column_insertion(tiling, 1, input_set):
# #                     print(letter2)
# #
# #                     for tiling2 in strategy2:
# #                         print()
# #                         print(tiling2)
# #                         print(dict(tiling2))
# #                         print()
# #                         tiling_verified2 = verify_tiling(tiling2, input_set)
# #                         if tiling_verified2:
# #                             print("Tiling was verified")
# #                         else:
# #                             print("Tiling was NOT verified")
# #             else:
# #                 print("GOING FOR ROUND TWO!!")
# #                 print("we will now try inserting into the following tile:")
# #                 print(tiling)
# #                 print(dict(tiling))
# #                 print()
# #                 print("now printing all tilings from inserting into left column")
# #                 for letter2, strategy2 in column_insertion(tiling, 0, input_set):
# #                     print(letter2)
# #                     for tiling2 in strategy2:
# #                         print()
# #                         print(tiling2)
# #                         print(dict(tiling2))
# #                         print()
# #                         tiling_verified2 = verify_tiling(tiling2, input_set)
# #                         if tiling_verified2:
# #                             print("Tiling was verified")
# #                         else:
# #                             print("Tiling was NOT verified")
# #             print("===back to round one===")
# #     print("=================")
