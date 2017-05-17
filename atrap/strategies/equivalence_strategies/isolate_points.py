from .equivalence_class import EquivalenceStrategy
from grids import Tiling, Block, PositiveClass

def all_equivalent_point_isolations(tiling, **kwargs):

    for cell in tiling.point_cells:

        if sum(1 for _, col_block in tiling.get_col(cell.i) if isinstance(col_block, PositiveClass)) == 1:
            # Cell ineligible because cell is not the sole non-class cell
            # in its respective col
            yield isolate_cell_in_column(tiling, cell)


        if sum(1 for _, row_block in tiling.get_row(cell.j) if isinstance(row_block, PositiveClass)) == 1:
             # Cell ineligible because cell is not the sole non-class cell
             # in its respective row
            yield isolate_cell_in_row(tiling, cell)

def isolate_cell_in_column(tiling, cell_to_be_isolated):
    new_tiling_dict = {}
    column = cell_to_be_isolated.j

    for cell, block in tiling:

        if cell.i == cell_to_be_isolated.i:
            if cell.j == cell_to_be_isolated.j:
                new_tiling_dict[cell] = block
            else:
                new_tiling_dict[(cell.i-0.5, cell.j)] = block
                new_tiling_dict[(cell.i+0.5, cell.j)] = block
        else:
            new_tiling_dict[cell] = block

    return EquivalenceStrategy( "Isolating the point at {} in its row".format(cell), Tiling(new_tiling_dict))


def isolate_cell_in_row(tiling, cell_to_be_isolated):
    new_tiling_dict = {}
    column = cell_to_be_isolated.j

    for cell, block in tiling:

        if cell.j == cell_to_be_isolated.j:
            if cell.i == cell_to_be_isolated.i:
                new_tiling_dict[cell] = block
            else:
                new_tiling_dict[(cell.i, cell.j-0.5)] = block
                new_tiling_dict[(cell.i, cell.j+0.5)] = block
        else:
            new_tiling_dict[cell] = block

    return EquivalenceStrategy( "Isolating the point at {} in its column".format(cell), Tiling(new_tiling_dict))
