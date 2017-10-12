
import sys
import time
from collections import defaultdict

from .equivdb import EquivalenceDB
from .LRUCache import LRUCache
from .ProofTree import ProofTree, ProofTreeNode
from .ruledb import RuleDB

from .strategies import InferralStrategy
from .strategies import Strategy
from .strategies import VerificationStrategy
from .strategies import StrategyPack

from .objectdb import ObjectDB
from .objectqueue import ObjectQueue
from .objectqueuedf import ObjectQueueDF

from .tree_searcher import proof_tree_bfs, prune


class CombinatorialSpecificationSearcher(object):
    """
    An instance of CombinatorialSpecificationSearcher is used to build up
    knowledge about an object with respect to the given strategies.
    """
    def __init__(self,
                 start_object=None,
                 strategy_pack=None,
                 symmetry=False,
                 objectqueue=ObjectQueue,
                 is_empty_strategy=None,
                 function_kwargs=dict()):
        """Initialise CombinatorialSpecificationSearcher."""
        if start_object is None:
            raise ValueError("CombinatorialSpecificationSearcher requires a start object.")

        self.equivdb = EquivalenceDB()
        self.ruledb = RuleDB()
        self.objectdb = ObjectDB(type(start_object))

        self.objectdb.add(start_object, expandable=True)
        self.start_label = self.objectdb.get_label(start_object)

        self._inferral_cache = LRUCache(100000)
        self._has_proof_tree = False
        if symmetry:
            # A list of symmetry functions of objects.
            if not isinstance(symmetry, list) or any(not callable(f) for f in symmetry):
                raise ValueError("To use symmetries need to give a list of symmetry functions.")
            self.symmetry = symmetry
        else:
            self.symmetry = []

        if objectqueue == ObjectQueue:
            self.objectqueue = ObjectQueue()
        elif objectqueue == ObjectQueueDF:
            self.objectqueue = ObjectQueueDF(rules_dict=self.ruledb.rules_dict,
                                             root=self.start_label,
                                             equivalent_set=self.equivdb.equivalent_set)

        self.objectqueue.add_to_working(self.start_label)



        if strategy_pack is not None:
            if not isinstance(strategy_pack, StrategyPack):
                raise TypeError("Strategy pack given not instance of strategy pack.")
            else:
                self.equivalence_strategy_generators = []
                self.inferral_strategy_generators = strategy_pack.inf_strats
                self.verif_strat_gen = strategy_pack.ver_strats
                self.strategy_generators = strategy_pack.other_strats
                if strategy_pack.eq_strats:
                    if self.strategy_generators:
                        self.strategy_generators[0].extend(strategy_pack.eq_strats)
                    else:
                        self.strategy_generators = strategy_pack.eq_strats
                        
        self.kwargs = function_kwargs

        if not callable(is_empty_strategy):
            raise ValueError("CombinatorialSpecificationSearcher requires a strategy that tests is an object is the empty set.")
        else:
            self.is_empty_strategy = is_empty_strategy

        self.expanded_objects = [0 for _ in self.strategy_generators]
        self.expansion_times = [0 for _ in self.strategy_generators]
        self.equivalent_time = 0
        self.verification_time = 0
        self.inferral_time = 0
        self.symmetry_time = 0
        self.tree_search_time = 0
        self.prepping_for_tree_search_time = 0
        self.queue_time = 0
        self._time_taken = 0
        self._cache_misses = 0 # this for status and should be updated if you use a cache



    def try_verify(self, obj, force=False):
        """
        Try to verify an object, obj.

        It will only try to verify objects who have no equivalent objects
        already verified. If force=True, it will try to verify obj if it is
        not already strategy verified.
        """
        start = time.time()
        label = self.objectdb.get_label(obj)
        if force:
            if self.objectdb.is_strategy_verified(label):
                self.verification_time += time.time() - start
                return
        elif self.equivdb.is_verified(label):
            self.verification_time += time.time() - start
            return
        for generator in self.verif_strat_gen:
            for strategy in generator(obj,
                                      **self.kwargs):
                if not isinstance(strategy, VerificationStrategy):
                    raise TypeError("Attempting to verify with non VerificationStrategy.")
                formal_step = strategy.formal_step
                self.objectdb.set_verified(obj, formal_step)
                self.objectdb.set_strategy_verified(obj)
                self.equivdb.update_verified(label)
                self.verification_time += time.time() - start
                return

    def is_empty(self, obj):
        """Return True if a object contains no permutations, False otherwise"""
        start = time.time()
        if self.objectdb.is_empty(obj) is not None:
            self.verification_time += time.time() - start
            return self.objectdb.is_empty(obj)
        if self.is_empty_strategy(obj, **self.kwargs):
            self.objectdb.set_empty(obj)
            self.verification_time += time.time() - start
            return True
        self.objectdb.set_empty(obj, empty=False)
        self.verification_time += time.time() - start
        return False

    def _inferral(self, obj):
        """
        Return fully inferred object.

        Will repeatedly use inferral strategies until object changes no more.
        """
        start = time.time()
        inferred_object = self._inferral_cache.get(obj)
        semi_inferred_objects = []
        if inferred_object is None:
            inferred_object = obj
            fully_inferred = False
            for strategy_generator in self.inferral_strategy_generators:
                # For each inferral strategy,
                if fully_inferred:
                    break
                for strategy in strategy_generator(inferred_object,
                                                   **self.kwargs):
                    if not isinstance(strategy, InferralStrategy):
                        raise TypeError("Attempted to infer on a non InferralStrategy")
                    # TODO: Where should the inferral formal step go?

                    # we infer as much as possible about the object and replace it.
                    soon_to_be_object = strategy.object

                    if soon_to_be_object is inferred_object:
                        continue

                    if soon_to_be_object in self._inferral_cache:
                        soon_to_be_object = self._inferral_cache.get(soon_to_be_object)
                        semi_inferred_objects.append(inferred_object)
                        inferred_object = soon_to_be_object
                        fully_inferred = True
                        break
                    else:
                        semi_inferred_objects.append(inferred_object)
                        inferred_object = soon_to_be_object
            for semi_inferred_object in semi_inferred_objects:
                self._inferral_cache.set(semi_inferred_object, inferred_object)
                if self.symmetry:
                    for sym_obj, sym_inf_obj in zip(self._symmetric_objects(semi_inferred_object,
                                                                        ordered=True),
                                                    self._symmetric_objects(inferred_object,
                                                                        ordered=True)):
                        self._inferral_cache.set(sym_obj, sym_inf_obj)
            self._inferral_cache.set(inferred_object, inferred_object)
        self.inferral_time += time.time() - start
        return inferred_object

    def _symmetric_objects(self, obj, ordered=False):
        """Return all symmetries of an object.

        This function only works if symmetry strategies have been given to the
        CombinatorialSpecificationSearcher. Sometimes, the order symmetries are
        appied are important. Therefore, if order=True, this will return a list
        with each symmetry applied (this functionality is needed for inferral).
        """
        if ordered:
            return [sym(obj) for sym in self.symmetry]
        else:
            symmetric_objects = set()
            for sym in self.symmetry:
                symmetric_object = sym(obj)
                if symmetric_object != obj:
                    symmetric_objects.add(symmetric_object)

        return symmetric_objects


    def expand(self, label):
        """
        Will expand the object with given label.

        The first time function called with label, it will expand with the
        first set of other strategies, second time the second set etc.
        """
        start = time.time()
        obj = self.objectdb.get_object(label)
        expanding = self.objectdb.number_times_expanded(label)
        strategy_generators = self.strategy_generators[expanding]
        for generator in strategy_generators:
            for strategy in generator(obj, **self.kwargs):
                if not isinstance(strategy, Strategy):
                    print(strategy, file=sys.stderr)
                    print(strategy.formal_step, file=sys.stderr)
                    print(generator, file=sys.stderr)
                    raise TypeError("Strategy given not of the right form.")

                if not strategy.back_maps:
                    start -= time.time()
                    objects = [self._inferral(o) for o in strategy.objects]
                    start += time.time()
                else:
                    objects = strategy.objects

                for ob, work in zip(objects, strategy.workable):
                    start -= time.time()
                    self.try_verify(ob)
                    start += time.time()
                    if work:
                        self.objectdb.set_expandable(ob)

                if strategy.back_maps:
                    if all(self.objectdb.is_expandable(o) for o in objects):
                        self.objectdb.set_workably_decomposed(label)

                if not strategy.back_maps:
                    start -= time.time()
                    objects = [o for o in objects if not self.is_empty(o)]
                    start += time.time()
                # TODO: put information about deleted empty strategy.objects into the
                #       formal step

                start -= time.time()
                for ob in objects:
                    if self.symmetry:
                        self._symmetry_expand(ob)
                    self._equivalent_expand(ob)
                start += time.time()

                if not objects:
                    # all the tilings are empty so the tiling itself must be empty!
                    self.objectdb.set_empty(label)
                    self.objectdb.set_verified(label, "This tiling contains no avoiding perms")
                    self.objectdb.set_strategy_verified(label)
                    self.equivdb.update_verified(label)
                    break
                # If we have an equivalent strategy
                # elif len(objects) == 1:
                #     other_label = self.objectdb.get_label(objects[0])
                #     self.equivdb.union(label, other_label, strategy.formal_step)
                #     if not (self.is_expanded(other_label)
                #             or self.objectdb.is_expanding_other_sym(other_label)):
                #         self.objectqueue.add_to_working(other_label)
                else:
                    end_labels = [self.objectdb.get_label(o) for o in objects]
                    self.ruledb.add(label, end_labels, strategy.formal_step)
                    for end_label in end_labels:
                        if (self.is_expanded(end_label)
                            or self.objectdb.is_expanding_other_sym(end_label)):
                            continue
                        self.objectqueue.add_to_next(end_label)
                if strategy.back_maps is not None:
                    if label not in self.ruledb.back_maps:
                        self.ruledb.back_maps[label] = {}
                    self.ruledb.back_maps[label][tuple(sorted(end_labels))] = strategy.back_maps

        if not self.is_expanded(label):
            self.objectdb.increment_expanded(label)
            self.expanded_objects[expanding] += 1
            self.expansion_times[expanding] += time.time() - start
            if not self.is_expanded(label):
                self.objectqueue.add_to_curr(label)

    def is_expanded(self, label):
        """Return True if an object has been expanded by all strategies."""
        number_times_expanded = self.objectdb.number_times_expanded(label)
        if number_times_expanded >= len(self.strategy_generators):
            return True
        return False

    def _symmetry_expand(self, obj):
        """Add symmetries of object to the database."""
        start = time.time()
        if not self.objectdb.is_symmetry_expanded(obj):
            for sym_o in self._symmetric_objects(obj):
                self.objectdb.add(sym_o,
                                  expanding_other_sym=True,
                                  symmetry_expanded=True)
                self.equivdb.union(self.objectdb.get_label(obj),
                                   self.objectdb.get_label(sym_o),
                                   "a symmetry")
        self.symmetry_time += time.time() - start

    def _equivalent_expand(self, obj):
        """
        Equivalent expand object with given label and equivalent strategies.

        It will apply the equivalence strategies as often as possible to
        find as many equivalent objects as possible.
        """
        if not self.objectdb.is_expandable(obj):
            return
        start = time.time()
        equivalent_objects = set([obj])
        objects_to_expand = set([obj])

        while objects_to_expand:
            # For each object to be expanded and
            obj = objects_to_expand.pop()
            if self.objectdb.is_equivalent_expanded(obj):
                continue
            label = self.objectdb.get_label(obj)
            for generator in self.equivalence_strategy_generators:
                # for all equivalent strategies
                for strategy in generator(obj,
                                          **self.kwargs):

                    if (not isinstance(strategy, Strategy)
                            or len(strategy.objects) != 1):
                        raise TypeError("Attempting to combine non equivalent strategy.")

                    formal_step = strategy.formal_step
                    start -= time.time()
                    eq_object = self._inferral(strategy.objects[0])
                    start += time.time()

                    # If we have already seen this object while building, we skip it
                    if eq_object in equivalent_objects:
                        continue

                    self.objectdb.add(eq_object, expandable=strategy.workable[0])
                    eq_label = self.objectdb.get_label(eq_object)
                    self.equivdb.union(label, eq_label, formal_step)
                    # Add it to the equivalent objects found
                    equivalent_objects.add(eq_object)
                    # And the objects to be checked for equivalencesß
                    objects_to_expand.add(eq_object)
                    start -= time.time()
                    self._symmetry_expand(eq_object)
                    self.try_verify(eq_object)
                    start += time.time()
                    self.objectqueue.add_to_next(eq_label)
            self.objectdb.set_equivalent_expanded(obj)
        self.equivalent_time += time.time() - start


    def do_level(self):
        """Expand objects in current queue. Objects found added to next."""
        start = time.time()
        queue_start = time.time()
        for label in self.objectqueue.do_level():
            if label is None:
                return True
            if self.is_expanded(label) or self.equivdb.is_verified(label):
                continue
            if self.objectdb.is_empty(label):
                continue
            elif not self.objectdb.is_expandable(label):
                continue
            elif self.objectdb.is_expanding_other_sym(label):
                continue
            elif self.objectdb.is_workably_decomposed(label):
                continue
            queue_start -= time.time()
            self.expand(label)
            queue_start += time.time()
        self.queue_time += time.time() - queue_start
        self._time_taken += time.time() - start

    def expand_objects(self, cap):
        """Will send "cap" many objects to the expand function."""
        start = time.time()
        queue_start = time.time()
        count = 0
        while count < cap:
            label = self.objectqueue.next()
            if label is None:
                return True
            if self.is_expanded(label) or self.equivdb.is_verified(label):
                continue
            if self.objectdb.is_empty(label):
                continue
            elif not self.objectdb.is_expandable(label):
                continue
            elif self.objectdb.is_expanding_other_sym(label):
                continue
            elif self.objectdb.is_workably_decomposed(label):
                continue
            count += 1
            queue_start -= time.time()
            self.expand(label)
            queue_start += time.time()
        self.queue_time += time.time() - queue_start
        self._time_taken += time.time() - start

    def status(self, file=sys.stderr):
        """
        Print the current status of the tilescope.

        It includes:
        - number of objects, and information about verification
        - the times spent in each of the main functions
        """

        print(" ------------- ", file=file)
        print("|STATUS UPDATE|", file=file)
        print(" ------------- ", file=file)
        print("", file=file)
        print("Time spent searching so far: {} seconds".format(self._time_taken), file=file)

        for i, expanded in enumerate(self.expanded_objects):
            print("Number of objects expanded by Set {} is {}".format(str(i+1),
                                                                      str(expanded)),
                  file=file)
        all_labels = self.objectdb.label_to_info.keys()
        print("Total number of objects is {}".format(str(len(all_labels))), file=file)
        expandable = 0
        verified = 0
        strategy_verified = 0
        empty = 0
        equivalent_sets = set()
        for label in all_labels:
            if self.objectdb.is_expandable(label):
                expandable += 1
            if self.objectdb.is_verified(label):
                verified += 1
            if self.objectdb.is_strategy_verified(label):
                strategy_verified += 1
            if self.objectdb.is_empty(label):
                empty += 1
            equivalent_sets.add(self.equivdb[label])
        print("Total number of equivalent sets is {}".format(str(len(equivalent_sets))),
              file=file)
        print("Total number of expandable objects is {}".format(str(expandable)),
              file=file)
        print("Total number of verified objects is {}".format(str(verified)),
              file=file)
        print("Total number of strategy verified objects is {}".format(str(strategy_verified)),
              file=file)
        print("Total number of empty objects is {}".format(str(empty)), file=file)
        print("Currently on 'level' {}".format(str(self.objectqueue.levels_completed + 1)), file=file)
        print("The size of the working queue is", self.objectqueue.working.qsize(), file=file)
        print("The size of the current queue is", self.objectqueue.curr_level.qsize(), file=file)
        print("The size of the next queue is", self.objectqueue.next_level.qsize(), file=file)
        print("There were {} cache misses".format(str(self._cache_misses)), file=file)
        print("", file=file)
        equiv_perc = int(self.equivalent_time/self._time_taken * 100)
        verif_perc = int(self.verification_time/self._time_taken * 100)
        infer_perc = int(self.inferral_time/self._time_taken * 100)
        symme_perc = int(self.symmetry_time/self._time_taken * 100)
        print("Time spent equivalent expanding: {} seconds, ~{}%".format(str(self.equivalent_time),
                                                                         equiv_perc),
              file=file)
        print("Time spent strategy verifying: {} seconds, ~{}%".format(str(self.verification_time),
                                                                       verif_perc),
              file=file)
        print("Time spent inferring: {} seconds, ~{}%".format(str(self.inferral_time),
                                                              infer_perc),
              file=file)
        if self.symmetry:
            print("Time spent symmetry expanding: {} seconds, ~{}%".format(str(self.symmetry_time),
                                                                           symme_perc),
                  file=file)
        for i, exp_time in enumerate(self.expansion_times):
            expand_perc = str(int(exp_time/self._time_taken * 100))
            print("Time spent expanding Set {}: {} seconds, ~{}%".format(str(i+1),
                                                                         str(exp_time),
                                                                         expand_perc),
                  file=file)
        queue_perc = int(self.queue_time/self._time_taken * 100)
        prep_time = self.prepping_for_tree_search_time
        prpts_perc = int(prep_time/self._time_taken * 100)
        tsrch_perc = int(self.tree_search_time/self._time_taken * 100)
        print("Time spent queueing: {} seconds, ~{}%".format(str(self.queue_time),
                                                             queue_perc),
              file=file)
        print("Time spent prepping for tree search: {} seconds, ~{}%".format(str(prep_time),
                                                                             prpts_perc),
              file=file)
        print("Time spent searching for tree: {} seconds, ~{}%".format(str(self.tree_search_time),
                                                                       tsrch_perc),
              file=file)
        total_perc = equiv_perc+verif_perc+infer_perc+symme_perc+queue_perc+prpts_perc+tsrch_perc
        for i, exp_time in enumerate(self.expansion_times):
            total_perc += int(exp_time/self._time_taken * 100)
        print("Total of ~{}% accounted for.".format(str(total_perc)), file=file)
        print("", file=file)


    def _strategies_to_str(self, strategies):
        """Return names of strategies/functions."""
        if not strategies:
            return ""
        output = str(strategies[0]).split(' ')[1]
        for strategy in strategies[1:]:
            output = output + ", " + str(strategy).split(' ')[1]
        return output

    def auto_search(self, cap=None, verbose=False, status_update=None, max_time=None, file=sys.stderr):
        """
        An automatic search function.

        It will either search for a proof tree after cap many objects have been
        expanded, or if cap=None, call do_level, before searching for tree.
        It will continue doing this until a proof tree is found.

        If verbose=True, a status update is given when a tree is found and
        after status_update many seconds have passed. It will also print
        the proof tree, in both json and pretty_print formats.
        """
        if verbose:
            if status_update:
                status_start = time.time()
            print("Auto search started", time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()),
                  file=file)
            print("", file=file)
            print("Looking for proof tree for:", file=file)
            print(self.objectdb.get_object(self.start_label), file=file)
            print("", file=file)
            print("The strategies being used are:", file=file)
            equiv_strats = self._strategies_to_str(self.equivalence_strategy_generators)
            infer_strats = self._strategies_to_str(self.inferral_strategy_generators)
            verif_strats = self._strategies_to_str(self.verif_strat_gen)
            print("Equivalent: {}".format(equiv_strats), file=file)
            print("Inferral: {}".format(infer_strats), file=file)
            print("Verification: {}".format(verif_strats), file=file)
            if self.symmetry:
                symme_strats = self._strategies_to_str(self.symmetry)
                print("Symmetries: {}".format(symme_strats), file=file)
            for i, strategies in enumerate(self.strategy_generators):
                strats = self._strategies_to_str(strategies)
                print("Set {}: {}".format(str(i+1), strats), file=file)
            print("", file=file)
        while True:
            if cap is None:
                if self.do_level():
                    break
            else:
                if self.expand_objects(cap):
                    break
                # TODO: if the above functions does nothing, it returns True,
                #       need to catch this in a better way.
            proof_tree = self.get_proof_tree()
            if proof_tree is not None:
                if verbose:
                    self.status(file=file)
                    print("Proof tree found", time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()),
                          file=file)
                    print("", file=file)
                    proof_tree.pretty_print(file=file)
                    print(proof_tree.to_json(), file=file)
                    print("Time taken was " + str(self._time_taken) + " seconds", file=file)
                return proof_tree
            if max_time is not None:
                if self._time_taken > max_time:
                    self.status(file=file)
                    print("Exceeded maximum time. Aborting auto search.", file=file)
                    return

            if status_update is not None and verbose:
                if time.time() - status_start > status_update:
                    self.status(file=file)
                    status_start = time.time()

    def has_proof_tree(self):
        return self._has_proof_tree

    def find_tree(self):
        """Search for a tree based on current data found."""
        start = time.time()
        rules_dict = defaultdict(set)
        # convert rules to equivalent labels
        for rule in self.ruledb:
            first, rest = rule
            first = self.equivdb[first]
            rest = tuple(sorted(self.equivdb[x] for x in rest))
            # this means union
            rules_dict[first] |= set((tuple(rest),))
        # add an empty rule, that represents verified in the tree searcher
        for label in self.objectdb.verified_labels():
            verified_label = self.equivdb[label]
            rules_dict[verified_label] |= set(((),))

        self.prepping_for_tree_search_time += time.time() - start
        self._time_taken += time.time() - start
        start = time.time()
        # Prune all unverifiable labels (recursively)
        rules_dict = prune(rules_dict)

        for label in rules_dict.keys():
            self.equivdb.update_verified(label)

        # only verified labels in rules_dict, in particular, there is a tree if
        # the start label is in the rules_dict
        if self.equivdb[self.start_label] in rules_dict:
            self._has_proof_tree = True
            # print("A tree was found! :)")
            _, proof_tree = proof_tree_bfs(rules_dict, root=self.equivdb[self.start_label])
            # print(proof_tree)
            self.tree_search_time += time.time() - start
            self._time_taken += time.time() - start
            return proof_tree
        else:
            self.tree_search_time += time.time() - start
            # print("No tree was found. :(")
        self._time_taken += time.time() - start

    def get_proof_tree(self, count=False):
        """
        Return proof tree if one exists.

        If count=True, then will return proof_tree, generating function where
        possible.
        """
        proof_tree_node = self.find_tree()
        if proof_tree_node is not None:
            proof_tree = ProofTree(self._get_proof_tree(proof_tree_node))
            # print(proof_tree.to_json())
            if count:
                function = proof_tree.get_genf()
                # print(f)
                return proof_tree, function
            return proof_tree
        else:
            pass
            # print("There is no proof tree yet.")

    def _get_proof_tree(self, proof_tree_node, in_label=None):
        """Recursive function for returning the root node of the proof tree."""
        label = proof_tree_node.label
        children_labels = sorted([x.label for x in proof_tree_node.children])
        if in_label is not None:
            in_object = self.objectdb.get_object(in_label)
        if children_labels:
            for rule in self.ruledb:
                start, ends = rule
                if self.equivdb.equivalent(start, label):
                    equiv_labels = [self.equivdb[x] for x in ends]
                    if sorted(equiv_labels) == children_labels:
                        # we have a match!
                        formal_step = self.ruledb.explanation(start, ends)
                        out_object = self.objectdb.get_object(start)
                        if in_label is None:
                            in_label = start
                            in_object = out_object
                        relation = self.equivdb.get_explanation(in_label, start)
                        identifier = label
                        children = []
                        for next_label in ends:
                            for child in proof_tree_node.children:
                                if self.equivdb.equivalent(next_label, child.label):
                                    children.append(self._get_proof_tree(child, next_label))
                                    break
                        back_maps = None
                        if start in self.ruledb.back_maps:
                            ends = tuple(sorted(ends))
                            if ends in self.ruledb.back_maps[start]:
                                back_maps = self.ruledb.back_maps[start][ends]
                        return ProofTreeNode(formal_step,
                                             in_object,
                                             out_object,
                                             relation,
                                             identifier,
                                             children=children,
                                             recurse=back_maps,
                                             strategy_verified=False)
        else:
            # we are verified by strategy or recursion
            for oth_label in self.objectdb:
                if (self.equivdb.equivalent(oth_label, label)
                        and self.objectdb.is_strategy_verified(oth_label)):
                    formal_step = self.objectdb.verification_reason(oth_label)
                    children = []
                    if in_label is None:
                        in_label = oth_label
                        in_object = out_object
                    relation = self.equivdb.get_explanation(in_label, oth_label)
                    out_object = self.objectdb.get_object(oth_label)
                    identifier = label
                    return ProofTreeNode(formal_step,
                                         in_object,
                                         out_object,
                                         relation,
                                         identifier,
                                         children=children,
                                         recurse=None,
                                         strategy_verified=True)
            # else we are recursively verified
            formal_step = "recurse" # this formal step is needed as hard coded in Arnar's code.
            if in_label is None:
                in_object = self.objectdb.get_object(in_label)
                out_object = in_object
            else:
                in_object = self.objectdb.get_object(in_label)
                out_object = in_object
            identifier = label
            relation = self.equivdb.get_explanation(in_label, in_label)
            return ProofTreeNode(formal_step,
                                 in_object,
                                 out_object,
                                 relation,
                                 identifier,
                                 children=None,
                                 recurse=None,
                                 strategy_verified=False)
