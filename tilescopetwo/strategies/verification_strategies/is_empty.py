
def is_empty_strategy(tiling, **kwargs):
    if tiling.is_empty():
        return True

    for reqlist in tiling.requirements:
        if all(any(ob in req for ob in tiling) for req in reqlist):
            return True
            
    return False
