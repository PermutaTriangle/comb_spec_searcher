from comb_spec_searcher import VerificationStrategy

def globally_verified(tiling, **kwargs):
    '''Can't handle requirements, so rage quit.'''
    if tiling.requirements:
        return
    if not tiling.dimensions == (1, 1):
        if all(not ob.is_interleaving() for ob in tiling.obstructions):
            return VerificationStrategy(formal_step="Globally verified.")
