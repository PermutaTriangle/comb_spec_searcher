"""A basic inferral strategy that determines if cells are empty based on points placed."""


from grids import Tiling, Block, PositiveClass
from comb_spec_searcher import InferralStrategy


def empty_cell_inferral(tiling, basis=None, **kwargs):
    """Yield InferralStrategy by removing all empty cells."""
    print(tiling)
    new_tiling_dict = dict(tiling)

    point_cells = {}
    for cell, block in tiling:
        if block is Block.point or isinstance(block, PositiveClass):
            point_cells[cell] = Block.point

    cells_removed = []
    for cell, block in tiling.classes:
        point_cells[cell] = Block.point
        verification_length = len(point_cells)
        point_cell_tiling = Tiling(point_cells)
        point_cells.pop(cell)
        if any(perm.avoids(*basis) for perm in point_cell_tiling.perms_of_length(verification_length)):
            continue
        cells_removed.append(cell)
        new_tiling_dict.pop(cell)

    if cells_removed:
        new_tiling = Tiling(new_tiling_dict)
        formal_step = "The cells {} are empty."
        formal_step = formal_step.format(tuple(cells_removed))
        yield InferralStrategy(formal_step, new_tiling)
