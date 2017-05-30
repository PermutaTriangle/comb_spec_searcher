"""
RecursiveStrategies by using the definition of reversibly deletable.

This definition is essentially equivalent to the one given in enumeration schemes paper.
"""


from grids import Tiling, Block
from atrap.tools import cells_of_occurrences_by_perms

from .recursive_class import RecursiveStrategy


def reversibly_deletable_points(tiling,
                                basis,
                                current_cell=None,
                                occurrences_by_perm=None,
                                path=None,
                                basis_partitioning=None,
                                **kwargs):
    """Yield all possibly RecursiveStrategy removing reversibly deletable points."""
    if current_cell is None:
        '''Take the smallest cell in the tiling'''
        current_cell = (-1, -1)
    if occurrences_by_perm is None:
        '''Occurrences stored as sets of cells'''
        occurrences_by_perm = cells_of_occurrences_by_perms(tiling, basis, basis_partitioning=basis_partitioning)
    if path is None:
        path = []
    for cell in tiling.point_cells:
        if cell <= current_cell:
            continue
        reversibly_deletable = True
        new_occurrences_by_perm = set()
        for perm_occurrences in occurrences_by_perm:
            new_perm_occurrences = []
            if not reversibly_deletable:
                break
            for occurrence in perm_occurrences:
                if not any(cell_used == cell for cell_used in occurrence):
                    new_perm_occurrences.append(occurrence)
            if new_perm_occurrences:
                new_occurrences_by_perm.add(tuple(new_perm_occurrences))
            else:
                reversibly_deletable = False
                break
        if reversibly_deletable:
            path.append(cell)
            new_tiling_dict = dict(tiling)
            for deleted_cell in path:
                new_tiling_dict.pop(deleted_cell)
            formal_step = "Reversibly delete the points at cells {}".format(path)
            points = Tiling({cell: Block.point for cell in path})
            strategy = [Tiling(new_tiling_dict), points]
            yield RecursiveStrategy(formal_step, strategy, [t._back_map for t in strategy])
            for recursive_strategy in reversibly_deletable_points(tiling, basis, cell, new_occurrences_by_perm, path):
                yield recursive_strategy
            path.pop()


def reversibly_deletable_cells(tiling,
                               basis,
                               current_cell=None,
                               occurrences_by_perm=None,
                               path=None, basis_partitioning=None,
                               **kwargs):
    """Yield all possile RecursiveStrategy from removing reversibly deletable cells."""
    if current_cell is None:
        '''Take the smallest cell in the tiling'''
        current_cell = (-1, -1)
    if occurrences_by_perm is None:
        '''Occurrences stored as sets of cells'''
        occurrences_by_perm = cells_of_occurrences_by_perms(tiling, basis, basis_partitioning=basis_partitioning)
    if path is None:
        path = []

    if len(path) == len(tiling) - 1:
        return

    for cell, _ in tiling:
        if cell <= current_cell:
            continue
        reversibly_deletable = True
        new_occurrences_by_perm = set()
        for perm_occurrences in occurrences_by_perm:
            new_perm_occurrences = []
            for occurrence in perm_occurrences:
                if not any(cell_used == cell for cell_used in occurrence):
                    new_perm_occurrences.append(occurrence)
            if new_perm_occurrences:
                new_occurrences_by_perm.add(tuple(new_perm_occurrences))
            else:
                reversibly_deletable = False
                break

        if reversibly_deletable:
            path.append(cell)
            new_tiling_dict = dict(tiling)
            blocks = []
            for deleted_cell in path:
                blocks.append((deleted_cell, new_tiling_dict.pop(deleted_cell)))
            formal_step = "Reversibly delete the blocks at cells {}".format(path)
            blocks = Tiling({cell: block for cell, block in blocks})
            tilings = [Tiling(new_tiling_dict), blocks]
            yield RecursiveStrategy(formal_step, tilings, [t._back_map for t in tilings])
            for recursive_strategy in reversibly_deletable_cells(tiling, basis, cell, new_occurrences_by_perm, path):
                yield recursive_strategy
            path.pop()
