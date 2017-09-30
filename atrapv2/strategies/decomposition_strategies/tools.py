def has_interleaving_decomposition(strategy):
    """Return True if decomposition strategy has interleaving recursion."""
    if strategy.back_maps is None:
        return False
    mixing = False
    bmps1 = [{c.i for c in dic.values()} for dic in strategy.back_maps]
    bmps2 = [{c.j for c in dic.values()} for dic in strategy.back_maps]
    for i in range(len(strategy.back_maps)):
        for j in range(len(strategy.back_maps)):
            if i != j:
                if (bmps1[i] & bmps1[j]) or (bmps2[i] & bmps2[j]):
                    mixing = True
    if mixing:
        return True
    return False
