"""A naive implementation of the proof tree."""


import itertools


from grids import Tiling


from .recipes import all_cell_insertions
from .recipes import all_row_and_column_insertions
from .verification import verify_tiling


RECIPES = [all_cell_insertions, all_row_and_column_insertions]


class Starter(object):
    def __init__(self, tiling):
        self.tiling = tiling
        self.batches = []
        self.verified = False
        self.verified_batches = []
        self.self_verified = False


class Batch(object):
    def __init__(self):
        self.label = ""
        self.starters = []
        self.verified = False


class Bakery(object):
    def __init__(self, input_set, recipes=RECIPES):
        # Store input set
        self.input_set = input_set

        # Set tiling class to display input set in the way we want
        Tiling.label(input_set, "X")

        # Store recipes
        self.recipes = tuple(recipes)

        # How far we have iterative deepening df searched
        self.height = 0

        # A "global" attribute to indicate how far a search reached
        self.reached_depth = 0

        # Create root starter
        tiling = Tiling({(0, 0): input_set})
        starter = Starter(tiling)

        # Create first batch
        batch = Batch()
        batch.starters.append(starter)
        batch.label = "Original batch"

        # Store first batch
        self.first_batch = batch

    def bake(self):
        depth = self.height + 1
        self.reached_depth = 0
        print("Starting baking!")
        self.baking_helper(self.first_batch, 0, depth)
        print("Baking ended!")
        self.height = max(self.height, self.reached_depth)
        if self.first_batch.verified:
            print("You can ask for a proof now!")
            return True
        else:
            return False

    def baking_helper(self, batch, depth, max_depth):

        assert 0 <= depth <= max_depth

        print("Am at depth", depth)

        if batch.verified:
            # No need to go further down
            return

        self.reached_depth = max(self.reached_depth, depth)

        # If no derived batches exist...
        # Just create all derived batches for ALL starters if not yet at max depth
        # IF a starter doesn't self verify
        if self.height <= depth < max_depth:
            print("Creating batches at depth", depth)
            for starter in batch.starters:
                if verify_tiling(starter.tiling, self.input_set) and depth != 0:
                    # And because it is self verified
                    starter.self_verified = True
                    starter.verified = True
                else:
                    # Create all the derived batches
                    assert not starter.batches  # Batches should be empty
                    derived_batches = itertools.chain(*(recipe(starter.tiling, self.input_set)
                                                        for recipe in self.recipes))
                    for label, tilings in derived_batches:
                        print("label:", label)
                        derived_batch = Batch()
                        derived_batch.label = label
                        derived_batch.starters.extend(Starter(tiling) for tiling in tilings)
                        starter.batches.append(derived_batch)

        # Now come the depth cases

        if depth <= self.height:
            print("Recursing on UNverified starters at depth", depth)
            # Recurse on unverified starters
            print("Going through starters!")
            for starter in batch.starters:
                print()
                print(starter, ":", sep="")
                print()
                print(starter.tiling)
                print()
                # Go through the starters
                if starter.verified:
                    print("Starter is already verified")
                    print()
                    pass  # starter is somehow verified, and we don't care anymore
                else:  # starter is neither verified by own tiling, nor by a derivative batch
                    print("Recursing on starters:")
                    print(starter.batches)
                    print()
                    for derived_batch in starter.batches:
                        self.baking_helper(derived_batch, depth + 1, max_depth)
                        if derived_batch.verified:
                            # Only need one derived batch to be verified for starter to be verified
                            starter.verified_batches.append(derived_batch)
                            starter.verified = True
                            break
            if all(starter.verified for starter in batch.starters):
                # All starters of the batch verified, so batch is verified
                batch.verified = True

        elif max_depth >= depth > self.height:
            print("Attempting to verify starters at depth", depth)
            # Attempt to verify batch via starter self verification
            for starter in batch.starters:
                starter.verified = starter.self_verified = verify_tiling(starter.tiling, self.input_set)
            if all(starter.self_verified for starter in batch.starters):
                print("All starters verified at depth", depth)
                # All starters of the batch verified, so batch is verified
                batch.verified = True
                # No need to recurse further
            elif depth != max_depth:
                print("Recursing because unverified starters, currently at depth", depth)
                # Recurse into derived batches
                for starter in batch.starters:
                    if not starter.verified:
                        for derived_batch in starter.batches:
                            self.baking_helper(derived_batch, depth + 1, max_depth)
                            if derived_batch.verified:
                                # Only need one derived batch to be verified for starter to be verified
                                starter.verified_batches.append(derived_batch)
                                starter.verified = True
                                break
                if all(starter.self_verified for starter in batch.starters):
                    # ... and yet again the same condition
                    batch.verified = True
            else:
                # Don't recurse into derived batches, for there are none
                pass

        else:
            raise RuntimeError("Somehow got to a case we didn't expect:\n{}".format(locals()))

    def give_me_proof(self):
        if self.first_batch.verified:
            print("I will give you proof, look:")
            self._proof = []
            self._proof_helper(self.first_batch)
            for tiling in self._proof:
                print()
                print(tiling)
                print()
        else:
            print("I WON'T GIVE YOU PROOF!!!")
            return None

    def _proof_helper(self, batch):
        for starter in batch.starters:
            if starter.self_verified:
                self._proof.append(starter.tiling)
            else:
                assert starter.verified_batches
                self._proof_helper(starter.verified_batches[0])

#number_of_unverified_starters = 0
#for starter in batch.starters:
#    if starter.verified_by is None:
#        first_time = not starter.batches  # Its descendants haven't been made
#        if first_time:
#            batches = itertools.chain(*(recipe(starter.tiling, self.input_set)
#                                        for recipe in self.recipes))
#        else:
#            batches = starter.batches
#        for index, derived_batch in enumerate(batches):
#            derived_batch = self.search_helper(derived_batch, depth + 1, max_depth)
#            if first_time:
#                starter.batches.append(derived_batch)
#            else:
#                starter.batches[index] = derived_batch
#            # Check if derived batch was verified
#    else:
#        pass  # We don't care, we have a starter verified by a batch
#if number_of_unverified_starters == 0:
#    batch.verified = True
