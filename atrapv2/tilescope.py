"""
  _______ __
 /_  __(_) /__ ___ _______  ___  ___
  / / / / / -_|_-</ __/ _ \/ _ \/ -_)
 /_/ /_/_/\__/___/\__/\___/ .__/\__/
                         /_/
"""

import sys

from permuta.descriptors import Basis
from permuta import Perm, Av

from grids import Tiling

from atrap.tools import find_symmetries

from comb_spec_searcher import CombinatorialSpecificationSearcher, ObjectQueue

from atrapv2.strategies import is_empty_strategy


class TileScope(CombinatorialSpecificationSearcher):
    """
    An instance of TileScope is used to build up knowledge about tilings with
    respect to the given basis.
    """
    def __init__(self,
                 basis,
                 strategy_pack=None,
                 interleaving_decomposition=True,
                 symmetry=False,
                 objectqueue=ObjectQueue,
                 start_tiling=None):
        """Initialise TileScope."""
        if isinstance(basis, str):
            self.basis = Basis([Perm([int(c) for c in p])
                                for p in basis.split('_')])
        else:
            self.basis = Basis(basis)


        self._basis_partitioning_cache = {}
        self._cache_hits = set()
        self._cache_misses = 0
        self._cache_hits_count = 0
        self._has_proof_tree = False

        if symmetry:
            # A list of symmetry functions of tilings.
            symmetries = find_symmetries(self.basis)
        else:
            symmetries = []

        if start_tiling is None:
            start_tiling = Tiling({(0, 0): Av(self.basis)})

        function_kwargs = {"basis": self.basis,
                           "basis_partitioning": self._basis_partitioning,
                           "interleaving_decomposition": interleaving_decomposition}

        CombinatorialSpecificationSearcher.__init__(self,
                                        start_object=start_tiling,
                                        strategy_pack=strategy_pack,
                                        symmetry=symmetries,
                                        objectqueue=ObjectQueue,
                                        is_empty_strategy=is_empty_strategy,
                                        function_kwargs=function_kwargs)

    def expand(self, label):
        super(TileScope, self).expand(label)
        if self.is_expanded(label):
            self._clean_partitioning_cache(self.objectdb.get_object(label))


    def _basis_partitioning(self, tiling, length, basis, function_name=None):
        """
        Return the basis partitioning of tiling.

        This information is stored in a cache.
        """
        # TODO: ignoring function name input, this is from deprecated feature of old version
        basis_partitioning_cache = self._basis_partitioning_cache.get(tiling)
        if basis_partitioning_cache is None:
            if tiling in self._cache_hits:
                print("!!CACHE MISS!!", file=sys.stderr)
                self._cache_misses += 1
            else:
                self._cache_hits.add(tiling)
            basis_partitioning_cache = {}
            self._basis_partitioning_cache[tiling] = basis_partitioning_cache

        basis_partitioning = basis_partitioning_cache.get(length)
        if basis_partitioning is None:
            basis_partitioning = tiling.basis_partitioning(length, basis)
            basis_partitioning_cache[length] = basis_partitioning
        else:
            self._cache_hits_count += 1

        return basis_partitioning

    def _clean_partitioning_cache(self, tiling):
        """Removes tiling from partitioning cache."""
        try:
            self._basis_partitioning_cache.pop(tiling)
        except KeyError:
            pass
