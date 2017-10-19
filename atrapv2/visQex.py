"""
The following is an example file, highlighting the current functionality of
the TileScope.

The first thing you need to do is import the TileScope.
"""
from atrapv2 import TileScope
"""In order to use the TileScope you need to give it both the basis and a
StrategyPack to search with. Therefore we also need to import StrategyPacks."""
from atrapv2 import StrategyPacks

from atrapv2 import VisualQueue

import sys


"""There are two ways to initialise the basis for the TileScope. The simplest
way is to give the basis as a string where permutations are zero based and
separated by '_'. For example, for the basis {123, 231}, give the string
'012_120' (Otherwise expects an iterable of Perm objects from Permuta). You also
need to choose a strategy pack to search with. Other options include:
    - strategy_pack: Set the strategy pack to search for. Must be an instance of
    StrategyPack.
    - interleaving_decomposition: Setting this to False will ensure that any
    decomposition strategies used will be non-intereaving.
    - symmetry: Setting this to true will take advantage of all symmetries
    available with respect to the given basis.
    - objectqueue: By default, he tilescope searches with the order as given by
    the 'ObjectQueue' class. You can use an alternative queue system if you
    prefer for example 'ObjectQueueDF' searches in a method similar to the old
    atrap. To change you need to import the class 'objectQueueDF', and set this
    keyword to equal the class. See example at line 103 of this file.
    - start_tiling: Set this to be the start tiling which the search starts
    from. The default setting is the 1x1 tiling with basis."""
tilescope = TileScope("012_120", StrategyPacks.point_placement, objectqueue=VisualQueue)

"""Now the tilescope has been set, we are now ready to search. To easiest way to
do this is to call the 'auto_search' function. If a proof tree is found this
function will return a ProofTree object. It will continue searching until one is
found."""
proof_tree = tilescope.auto_search(cap=1)

"""To view the proof tree call the 'pretty_print' function."""
proof_tree.pretty_print()

"""Alternatively you can use the 'to_json' function. This returns some json code
which can be copied and pasted into the 'Draw ATRAP Trees' feature at
permpal.ru.is."""
print(proof_tree.to_json())

sys.exit(1)

"""There are a number of additional options to the 'auto_search' function. They
are as follows:
    - 'cap': When cap is set, this is the number of tilings expanded before
    searching for a proof tree. When not set, the TileScope will finish the
    'level' before searching for a proof tree.
    - 'verbose': When verbose is True, TileScope will print information about
    the run. This includes the functions used and a detailed status of the run
    when a proof tree is found. The proof tree is also printed, and its json.
    - 'status_update': if verbose is true, then if you would like regular status
    updates, then set this to be the number of seconds between status updates
    that you want.
    - 'max_time': This is the maximum number of seconds that the auto search
    function will search for. If no proof tree is found, the function will
    return 'None'. By not setting it, it will search forever!
    - 'file': This is the file that the TileScope will print to. The default
    setting is 'sys.stderr'.
These can be triggered as keyword arguments when calling the 'auto_search'
function."""
tilescope = TileScope("1302_2031", StrategyPacks.row_and_column_placements)
tilescope.auto_search(cap=1, verbose=True, status_update=5, max_time=10)

"""If you wish to do the search more manually, then you can use the functions
'expand_objects' and 'get_proof_tree'. The 'get_proof_tree' function will return
a ProofTree object if one has been found, or else it will return 'None'."""
tilescope.expand_objects(20)
proof_tree = tilescope.get_proof_tree()
proof_tree.pretty_print()

"""You can also instead use the 'do_level' function. This will expand the
remainder of the current level."""
tilescope = TileScope("012", StrategyPacks.point_separation_and_isolation)
tilescope.do_level()
proof_tree = tilescope.get_proof_tree()
if proof_tree is not None:
    proof_tree.pretty_print()
else:
    print("No tree found.")

"""You can manually call for a status update using the 'status' function."""
while proof_tree is None:
    tilescope.do_level()
    proof_tree = tilescope.get_proof_tree()
proof_tree.pretty_print()
tilescope.status()

"""If you wish to search using a different queue system, you will first need to
import the queue class you wish to search with. For example, lets assume you
wish to search with the old atrap style."""
from comb_spec_searcher.objectqueuedf import ObjectQueueDF
"""After importing you set the keyword 'objectqueue' when initialising the
tilescope"""
tilescope = TileScope("0132_0231_0312_0321_1032_3120",
                      StrategyPacks.minimum_row_placements,
                      objectqueue=ObjectQueueDF)
tilescope.auto_search(1, verbose=True, status_update=10)
