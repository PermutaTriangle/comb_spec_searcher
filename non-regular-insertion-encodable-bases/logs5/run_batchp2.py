from permuta import *
from atrap import MetaTree, StrategyPacks
from atrap.ProofTree import ProofTree

import time

# filename = 'length5' # the file with bases to be processed
# filename = 'length5afterround1'
#filename = 'length5fixiso'
# filename = 'length5afterround2p2'
# filename = 'length5afterround3p2'
# filename = 'length5afterround4p2'
# filename = 'length5afterround5p2'
# filename = 'length5afterround6p2'
filename = 'length5afterround7p2'

# Will try each strategy pack in order.
strategy_packs = [
                    StrategyPacks.row_and_column_placements_and_all_321_boundaries,
                    StrategyPacks.row_and_column_placements_and_all_321_boundaries_and_splittings,
                    StrategyPacks.point_placement_and_all_321_boundaries,
                    StrategyPacks.point_placement_and_all_321_boundaries_and_splittings,
                    StrategyPacks.point_placement_and_all_lrm_and_rlm_placements,
                    StrategyPacks.point_placement_and_all_lrm_and_rlm_placements_and_splittings,
                    StrategyPacks.row_and_column_placements_and_all_lrm_and_rlm_placements,
                    StrategyPacks.row_and_column_placements_and_all_lrm_and_rlm_placements_and_splittings,
                    StrategyPacks.point_placement,
                    StrategyPacks.point_placement_and_splittings,
                    StrategyPacks.point_placement_and_point_separation,
                    StrategyPacks.point_placement_and_splittings_and_point_separation,
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


# max_times = 30 # seconds for each strategy pack (must be integer)
# max_times = 60
# max_times = 120
max_times = 600
# max_times = 1800
# max_times = 3600
# max_times = [ 5, 6, 7, 8, 9, 10] # seconds for corresponding strategy pack

def perm_to_str(perm):
    return "".join([str(i) for i in list(perm)])

def basis_to_str(basis):
    return "_".join(perm_to_str(perm) for perm in basis)

def str_to_basis(string):
    return [ Perm([ int(c) for c in p ]) for p in string.split('_') ]

def strategy_to_str(strategy):
    return str(strategy).split(' ')[1]

def strategies_to_str(strategies):
    if len(strategies) == 0:
        return ""
    output = strategy_to_str( strategies[0] )
    for strategy in strategies[1:]:
        output = output + ", " + strategy_to_str(strategy)
    return output

def count_verified_tilings(mt):
    count = 0
    for tiling, or_node in mt.tiling_cache.items():
        if or_node.sibling_node.is_verified():
            count += 1
    return count

def count_sibling_nodes(mt):
    s = set()
    verified = 0
    for tiling, or_node in mt.tiling_cache.items():
        if or_node.sibling_node in s:
            continue
        if or_node.sibling_node.is_verified():
            verified += 1
        s.add(or_node.sibling_node)
    return len(s), verified

if isinstance(max_times, int):
    max_times = [ max_times for i in range(len(strategy_packs)) ]

if len(strategy_packs) != len(max_times):
    raise ValueError("The length of strategy_packs does not match the length of max_time")


with open(filename) as f:

    content = f.readlines()
    bases = [ str_to_basis( x.strip() ) for x in content]

for basis in bases:
    task = basis_to_str(basis)
    no_proof_tree_found = True

    with open(task, "w") as f:
        print(task, file=f)
        print("", file=f)

    print('-----------------------------------------------------------------')
    print('Now processing {}'.format(task))
    for strategy_pack, max_time, attempt in zip(strategy_packs, max_times, range(len(strategy_packs))):
        print()
        print("Attempt {} with the following strategies:".format(attempt))
        print("Batch: {}".format( strategies_to_str(strategy_pack[0])))
        print("Equivalent: {}".format( strategies_to_str(strategy_pack[1])))
        print("Inferral: {}".format( strategies_to_str(strategy_pack[2])))
        print("Recursive: {}".format( strategies_to_str(strategy_pack[3])))
        print("Verification: {}".format( strategies_to_str(strategy_pack[4])) )
        mtree = MetaTree( basis, *strategy_pack )

        start_time = time.time()
        end_time = start_time + max_time

        while True:
            time_remaining = end_time - time.time()
            mtree.do_level(max_time = time_remaining)
            if mtree.has_proof_tree():
                break
            if time.time() > end_time:
                print('Ran out of time, without finding a proof tree')
                break

        with open(task, "a" ) as f:
            print( "===========================================", file=f)
            total_time = int( time.time() - start_time )
            print("Log created", time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()),file=f)
            print("",file=f)
            print("Maximum depth fully searched was {}".format(mtree.depth_searched), file=f)
            print("",file=f)
            print('Maximum time set at {} seconds'.format(str(max_time)), file=f)
            print("",file=f)
            print("Total time taken was {} seconds".format( total_time ),file=f)
            print("",file=f)
            print("The strategies applied were:",file=f)
            print("Batch: {}".format( strategies_to_str(strategy_pack[0])), file=f )
            print("Equivalent: {}".format( strategies_to_str(strategy_pack[1])), file=f )
            print("Inferral: {}".format( strategies_to_str(strategy_pack[2])), file=f )
            print("Recursive: {}".format( strategies_to_str(strategy_pack[3])), file=f )
            print("Verification: {}".format( strategies_to_str(strategy_pack[4])), file=f )
            print("",file=f)
            print("There were {} inferral cache hits and {} partitioning cache hits.".format(mtree.inferral_cache_hits, mtree.partitioning_cache_hits),file=f)
            print("The partitioning cache had {} tilings in it right now.".format( len(mtree._basis_partitioning_cache) ) ,file=f)
            print("The inferral cache has {} tilings in it right now.".format( len(mtree._inferral_cache) ) ,file=f)
            print("There were {} tilings of which {} are verified.".format( len(mtree.tiling_cache), count_verified_tilings(mtree)),file=f)
            print("There were {} SiblingNodes of which {} are verified.".format(*count_sibling_nodes(mtree)),file=f)
            print("",file=f)
            for function_name, calls in mtree._partitioning_calls.items():
                print("The function {} called the partitioning cache *{}* times, ({} originating)".format(function_name, calls[0], calls[1]),file=f)
            print("There were {} cache misses".format(mtree._cache_misses),file=f)
            print("",file=f)

            if mtree.has_proof_tree():
                proof_tree = mtree.find_proof_tree()
                print("A proof tree was found in {} seconds".format(total_time), file=f)
                print("",file=f)
                print("Human readable:", file=f)
                print("",file=f)

                proof_tree.pretty_print(file=f)

                print("",file=f)
                print("Computer readable (JSON):", file=f)
                print("", file=f)
                print(proof_tree.to_json(sort_keys=True), file=f)

                no_proof_tree_found = False
                break
            else:
                print("No proof tree was found after {} seconds".format(total_time),file=f)
                print("",file=f)

    if no_proof_tree_found:
        with open(task, "a" ) as f:
            print('Unable to find a proof tree within the time limits', file=f)
