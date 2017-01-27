from atrap import *
from permuta import *
import sys


# input_set = Tile.INCREASING
# input_set = Tile.DECREASING
# input_set = PermSet.avoiding([Perm((0, 1)), Perm((1, 0))])
# input_set = PermSet.avoiding([Perm((0, 2, 1))])
# input_set = PermSet.avoiding([Perm((0, 2, 1)), Perm((2, 0, 1))])
# input_set = PermSet.avoiding([Perm((1, 2, 0))])
# input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((1, 2, 0))])
# input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 0, 2))])
# input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((0, 2, 1))])
input_set = PermSet.avoiding([Perm((0, 1, 2)), Perm((2, 1, 0))])

T = Tiling({(0, 0): input_set})

print("Our tiling:")
print()
print(T)
print()

print("Doing row insertion first step")

empty_row, row_cells = row_insertion_helper(T, 0)

print("Emptied row")
print()
print(empty_row)
print()
print("The cells in the row are")
print(row_cells)
print()

print("Now inserting minimum into the row")
for letter, strategy in row_insertion(T, 0, input_set):
    print(letter)
    print("now printing all tilings from inserting into row")
    for tiling in strategy:
        print ()
        print(tiling)
        print()
        tiling_verified = verify_tiling(tiling, input_set)
        if tiling_verified:
            print("Tiling was verified")
        else:
            print("Tiling was NOT verified")
            if letter == "B":
                print("GOING FOR ROUND TWO!!")
                print("we will now try inserting into the following tile:")
                print(tiling)
                print(dict(tiling))
                print()
                print("now printing all tilings from inserting into top row")
                for letter2, strategy2 in row_insertion(tiling, 0, input_set):
                    print(letter2)

                    for tiling2 in strategy2:
                        print()
                        print(tiling2)
                        print(dict(tiling2))
                        print()
                        tiling_verified2 = verify_tiling(tiling2, input_set)
                        if tiling_verified2:
                            print("Tiling was verified")
                        else:
                            print("Tiling was NOT verified")
            else:
                print("GOING FOR ROUND TWO!!")
                print("we will now try inserting into the following tile:")
                print(tiling)
                print(dict(tiling))
                print()
                print("now printing all tilings from inserting into bottom row")
                for letter2, strategy2 in row_insertion(tiling, 1, input_set):
                    print(letter2)
                    for tiling2 in strategy2:
                        print()
                        print(tiling2)
                        print(dict(tiling2))
                        print()
                        tiling_verified2 = verify_tiling(tiling2, input_set)
                        if tiling_verified2:
                            print("Tiling was verified")
                        else:
                            print("Tiling was NOT verified")
            print("===back to round one===")
    print("=================")

#
# T = Tiling({(0, 0): input_set})
#
# print("Our tiling:")
# print()
# print(T)
# print()
#
# print("Doing column insertion first step")
#
# empty_column, column_cells = column_insertion_helper(T, 0)
#
# print("Emptied column")
# print()
# print(empty_column)
# print()
# print("The cells in the column are")
# print(column_cells)
# print()
#
# print("Now inserting minimum into the column")
# for letter, strategy in column_insertion(T, 0, input_set):
#     print(letter)
#     print("now printing all tilings from inserting into column")
#     for tiling in strategy:
#         print ()
#         print(tiling)
#         print()
#         tiling_verified = verify_tiling(tiling, input_set)
#         if tiling_verified:
#             print("Tiling was verified")
#         else:
#             print("Tiling was NOT verified")
#             if letter == "L":
#                 print("GOING FOR ROUND TWO!!")
#                 print("we will now try inserting into the following tile:")
#                 print(tiling)
#                 print(dict(tiling))
#                 print()
#                 print("now printing all tilings from inserting into right column")
#                 for letter2, strategy2 in column_insertion(tiling, 1, input_set):
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
#                 print("now printing all tilings from inserting into left column")
#                 for letter2, strategy2 in column_insertion(tiling, 0, input_set):
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
