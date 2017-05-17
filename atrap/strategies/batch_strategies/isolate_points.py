from batch_class import BatchStrategy
from grids import Tiling, PositiveClass, Block

def all_point_isolations(tiling, **kwargs):
    tiling = Tiling()
    for point_cell in tiling.point_cells()

        if sum(1 for _, col_block in tiling.get_col(cell.i)) != 1:
            # Cell ineligible because cell is not the sole non-class cell
            # in its respective col
            hor_split = False

        if sum(1 for _, row_block in tiling.get_row(cell.j)) != 1:
             # Cell ineligible because cell is not the sole non-class cell
             # in its respective row
            vert_split = False

            
