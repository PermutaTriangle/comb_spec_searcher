from .batch_class import BatchStrategy
from grids import Tiling, PositiveClass, Block
from itertools import combinations, chain
from copy import copy

def all_point_isolations(tiling, **kwargs):
    for cell in tiling.point_cells:

        if sum(1 for _, col_block in tiling.get_col(cell.i) if isinstance(col_block, PositiveClass) ) != 1:
            # Cell ineligible because cell is not the sole non-class cell
            # in its respective col
            yield isolate_point_in_column(tiling, cell)

        if sum(1 for _, row_block in tiling.get_row(cell.j) if isinstance(row_block, PositiveClass) ) != 1:
             # Cell ineligible because cell is not the sole non-class cell
             # in its respective row
            yield isolate_point_in_row(tiling, cell)

def isolate_point_in_row(tiling, cell_to_be_isolated):
    new_tiling_dict = {}

    positive_classes = []

    for cell, block in tiling:

        if cell.j == cell_to_be_isolated.j:
            if cell.i == cell_to_be_isolated.i:
                new_tiling_dict[cell] = block
            else:
                if block is Block.point:
                    positive_classes.append( (cell, block) )

                elif isinstance(block, PositiveClass) and not block is Block.point:

                    perm_class = block.perm_class
                    new_tiling_dict[(cell.i, cell.j-0.5)] = perm_class
                    new_tiling_dict[(cell.i, cell.j+0.5)] = perm_class

                    positive_classes.append( (cell, block) )

                else:
                    new_tiling_dict[(cell.i, cell.j-0.5)] = block
                    new_tiling_dict[(cell.i, cell.j+0.5)] = block

        else:
            new_tiling_dict[cell] = block

    isolated_tilings = []
    for subset in powerset( [ cell for cell, _ in positive_classes ] ):
        isolated_tiling_dict = copy(new_tiling_dict)
        for cell, block in positive_classes:
            if cell in subset:
                isolated_tiling_dict[ (cell.i, cell.j-0.5) ] = block
            else:
                isolated_tiling_dict[ (cell.i, cell.j+0.5) ] = block
        isolated_tilings.append( Tiling(isolated_tiling_dict) )

    # print("Isolated the point at {} in its row on the tiling".format(cell_to_be_isolated))
    # print(tiling)
    # print("it gave")
    # for tiling in isolated_tilings:
    #     print(tiling)
    #     print()
    # print()
    # print("---------")
    return BatchStrategy("Isolated the point at {} in its row".format(cell_to_be_isolated), isolated_tilings)



def isolate_point_in_column(tiling, cell_to_be_isolated):
    new_tiling_dict = {}

    positive_classes = []

    for cell, block in tiling:

        if cell.i == cell_to_be_isolated.i:
            if cell.j == cell_to_be_isolated.j:
                new_tiling_dict[cell] = block
            else:
                if block is Block.point:
                    positive_classes.append( (cell, block) )

                elif isinstance(block, PositiveClass) and not block is Block.point:

                    perm_class = block.perm_class
                    new_tiling_dict[(cell.i-0.5, cell.j)] = perm_class
                    new_tiling_dict[(cell.i+0.5, cell.j)] = perm_class

                    positive_classes.append( (cell, block) )

                else:
                    new_tiling_dict[(cell.i-0.5, cell.j)] = block
                    new_tiling_dict[(cell.i+0.5, cell.j)] = block

        else:
            new_tiling_dict[cell] = block
        isolated_tilings = []

    for subset in powerset( [ cell for cell, _ in positive_classes ] ):
        isolated_tiling_dict = copy(new_tiling_dict)
        for cell, block in positive_classes:
            if cell in subset:
                isolated_tiling_dict[ (cell.i-0.5, cell.j) ] = block
            else:
                isolated_tiling_dict[ (cell.i+0.5, cell.j) ] = block
        isolated_tilings.append( Tiling(isolated_tiling_dict) )

    # print("Isolated the point at {} in its column on the tiling".format(cell_to_be_isolated))
    # print(tiling)
    # print("it gave")
    # for tiling in isolated_tilings:
    #     print(tiling)
    #     print()
    # print()
    # print("---------")
    return BatchStrategy("Isolated the point at {} in its column".format(cell_to_be_isolated), isolated_tilings)


def powerset(l):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    return chain.from_iterable(combinations(l, r) for r in range(len(l)+1))
