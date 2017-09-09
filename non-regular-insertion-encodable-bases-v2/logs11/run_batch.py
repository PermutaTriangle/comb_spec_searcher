from atrapv2 import TileScope, StrategyPacks

filename = 'length11' # the file with bases to be processed
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


max_time = 30 # seconds for each strategy pack (must be integer)
status_update = None
# max_times = 60
# max_times = [ 5, 6, 7, 8, 9, 10] # seconds for corresponding strategy pack

with open(filename) as bases:
    for task in bases.readlines():
        task = task.strip()
        with open(task, "w") as f:
            print(task)
            print(task, file=f)
            print("", file=f)

            for strategy_pack in strategy_packs:
                print("--------------------------------------------------------------------------", file=f)
                tilescope = TileScope(basis=task, **strategy_pack)
                tilescope.auto_search(1, max_time=max_time, status_update=status_update, verbose=True, file=f)
                print("", file=f)
                if tilescope.has_proof_tree():
                    print("proof tree found")
                    break
