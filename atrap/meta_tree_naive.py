"""A naive implementation of the proof tree."""


import itertools


from grids import Tiling


from .proof_strategies import cell_insertion
from .proof_strategies import verify_tiling


PROOF_STRATEGIES = [cell_insertion, cell_insertion]


class Starter(object):
    def __init__(self, tiling):
        self.tiling = tiling
        self.strategies = []


class Batch(object):
    def __init__(self):
        self.unverified = []
        self.verified = []


class MetaTree(object):
    def __init__(self, input_set):
        # Store input set
        self.input_set = input_set

        # Create root starter
        tiling = Tiling({(0, 0): input_set})
        starter = Starter(tiling)

        # Create root batch
        batch = Batch()
        batch.unverified.append(starter)

        # Store root batch
        self.root_batch = batch
