from atrapv2 import TileScope, StrategyPacks
from atrapv2.tilingqueue import TilingQueue
from atrapv2.tilingqueuedf import TilingQueueDF
import time

filename = 'length9' # the file with bases to be processed
# filename = 'length11afterround1'

# Will try each strategy pack in order.
strategy_packs = [  StrategyPacks.something_else,
                    StrategyPacks.row_and_column_placements,
                    StrategyPacks.row_and_column_placements_and_splittings,
                    StrategyPacks.row_and_column_placements_and_point_separation,
                    StrategyPacks.row_and_column_placements_and_splittings_and_point_separation,
                    StrategyPacks.point_separation_and_isolation,
                    StrategyPacks.point_separation_and_isolation_and_splittings,
                    StrategyPacks.row_placements,
                    StrategyPacks.row_placements_and_splittings,
                    StrategyPacks.row_placements_and_point_separation,
                    StrategyPacks.row_placements_and_splittings_and_point_separation,
                    StrategyPacks.minimum_row_placements,
                    StrategyPacks.minimum_row_placements_and_splittings,
                    StrategyPacks.minimum_row_placements_and_point_separation,
                    StrategyPacks.minimum_row_placements_and_splittings_and_point_separation,
                    StrategyPacks.column_placements,
                    StrategyPacks.column_placements_and_splittings,
                    StrategyPacks.column_placements_and_point_separation,
                    StrategyPacks.column_placements_and_splittings_and_point_separation,
                    StrategyPacks.left_column_placements,
                    StrategyPacks.left_column_placements_and_splittings,
                    StrategyPacks.left_column_placements_and_point_separation,
                    StrategyPacks.left_column_placements_and_splittings_and_point_separation,
                 ]

symmetry = False
non_interleaving_decomposition = False
tilingqueue = TilingQueue # TilingQueue for new or TilingQueueDF for old atrap style
max_time = 60 # seconds for each strategy pack (must be integer)
status_update = None # how often you want an update

start = time.time()
with open(filename) as bases:
    for task in bases.readlines():
        task = task.strip()
        with open(task, "w") as f:
            print(task)
            print(task, file=f)
            print("Symmetry:", symmetry, file=f)
            print("Non-Interleaving Decompoition:", non_interleaving_decomposition, file=f)
            print("Tiling Queue:", tilingqueue, file=f)
            print("", file=f)

            for strategy_pack in strategy_packs:
                print("--------------------------------------------------------------------------", file=f)
                print("Trying:", strategy_pack.name, file=f)
                tilescope = TileScope(task,
                                      strategy_pack,
                                      tilingqueue=tilingqueue,
                                      symmetry=symmetry,
                                      non_interleaving_decomposition=non_interleaving_decomposition)
                tilescope.auto_search(1, max_time=max_time, status_update=status_update, verbose=True, file=f)
                print("", file=f)
                if tilescope.has_proof_tree():
                    print("proof tree found")
                    break
end = time.time()
with open("total", "w") as f:
    print("Total time taken was {} seconds".format(int(end-start)), file=f)
