import functools
from itertools import chain

from comb_spec_searcher import StrategyPack
from tilescopetwo import strategies as strats


class ATRAPStrategyPack(StrategyPack):
    _valid_with_reqins = {strats.all_cell_insertions,
                          strats.all_requirement_insertions,
                          strats.forced_binary_pattern,
                          strats.components,
                          strats.empty_cell_inferral,
                          strats.subobstruction_inferral,
                          strats.subobstruction_inferral_rec,
                          strats.row_and_column_separation,
                          strats.subset_verified,
                          strats.database_verified}

    def __init__(self, eq_strats=None, ver_strats=None, inf_strats=None,
                 other_strats=None, name=None, old_pack=None):
        has_reqins = False
        for stratlist in other_strats:
            for strat in stratlist:
                if (isinstance(strat, functools.partial) and
                        strat.func == strats.all_requirement_insertions):
                    has_reqins = True
                elif strat == strats.all_requirement_insertions:
                    has_reqins = True

        if has_reqins:
            all_strats_used = list(chain(eq_strats,
                                         ver_strats,
                                         inf_strats,
                                         chain.from_iterable(other_strats)))
            # print(all_strats_used)
            # print(list((strat.func, strat.func in ATRAPStrategyPack._valid_with_reqins) if isinstance(strat, functools.partial) else (strat, strat in ATRAPStrategyPack._valid_with_reqins) for strat in all_strats_used))
            if not all((strat in ATRAPStrategyPack._valid_with_reqins or
                        (isinstance(strat, functools.partial) and
                         strat.func in ATRAPStrategyPack._valid_with_reqins))
                       for strat in all_strats_used):
                raise ValueError(
                    ("Requirement insertion is only allowed with: {}").format(
                        ATRAPStrategyPack._strategies_to_str(
                            list(ATRAPStrategyPack._valid_with_reqins))))

        super(ATRAPStrategyPack, self).__init__(eq_strats=eq_strats,
                                                ver_strats=ver_strats,
                                                inf_strats=inf_strats,
                                                other_strats=other_strats,
                                                name=name,
                                                old_pack=old_pack)

    @staticmethod
    def _strategies_to_str(strategies):
        """Return names of strategies/functions."""
        if not strategies:
            return ""
        output = str(strategies[0]).split(' ')[1]
        for strategy in strategies[1:]:
            output = output + ", " + str(strategy).split(' ')[1]
        return output
