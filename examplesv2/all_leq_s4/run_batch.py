from atrapv2 import TileScope, StrategyPacks
from atrapv2.tilingqueue import TilingQueue
from atrapv2.tilingqueuedf import TilingQueueDF
import time

filename = 'all_leq_S4' # the file with bases to be processed
# filename = 'length11afterround1'

# Will try each strategy pack in order.
strategy_packs = [  StrategyPacks.row_and_column_placements,
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
non_interleaving_recursion = False
tilingqueue = TilingQueue # or TilingQueueDF for old atrap style
max_time = 30 # seconds for each strategy pack (must be integer)
status_update = None # how often you want an update

start = time.time()
with open(filename) as bases:
    for task in bases.readlines():
        task = task.strip()
        with open(task, "w") as f:
            print(task)
            print(task, file=f)
            print("", file=f)

            for strategy_pack in strategy_packs:
                print("--------------------------------------------------------------------------", file=f)
                tilescope = TileScope(task,
                                      strategy_pack,
                                      tilingqueue=tilingqueue,
                                      symmetry=symmetry,
                                      non_interleaving_recursion=non_interleaving_recursion)
                tilescope.auto_search(1, max_time=max_time, status_update=status_update, verbose=True, file=f)
                print("", file=f)
                if tilescope.has_proof_tree():
                    print("proof tree found")
                    break
end = time.time()
print("Total time taken was {} seconds".format(int(end-start)))
