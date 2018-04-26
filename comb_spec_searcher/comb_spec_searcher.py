
import sys
import time
from collections import defaultdict
from logzero import logger
import json

from .equivdb import EquivalenceDB
from .LRUCache import LRUCache
from .objectdb import ObjectDB
from .objectdb_compress import CompressedObjectDB
from .objectqueue import ObjectQueue
from .objectqueuedf import ObjectQueueDF
from .proof_tree import ProofTree as ProofTree
from .ruledb import RuleDB
from .strategies import (InferralStrategy, Strategy, StrategyPack,
                         VerificationStrategy)
from .tree_searcher import (proof_tree_bfs, prune, iterative_prune,
                            iterative_proof_tree_bfs)


class CombinatorialSpecificationSearcher(object):
    """
    An instance of CombinatorialSpecificationSearcher is used to build up
    knowledge about an object with respect to the given strategies.
    """
    def __init__(self,
                 start_object=None,
                 strategy_pack=None,
                 symmetry=False,
                 compress=False,
                 forward_equivalence=False,
                 complement_verify=True,
                 objectqueue=ObjectQueue,
                 is_empty_strategy=None,
                 function_kwargs=dict(),
                 logger_kwargs=dict()):
        """Initialise CombinatorialSpecificationSearcher."""
        if start_object is None:
            raise ValueError("CombinatorialSpecificationSearcher requires a start object.")

        self.equivdb = EquivalenceDB()
        self.ruledb = RuleDB()
        if compress:
            self.objectdb = CompressedObjectDB(type(start_object))
        else:
            self.objectdb = ObjectDB()

        self.objectdb.add(start_object, expandable=True)
        self.start_label = self.objectdb.get_label(start_object)

        self._inferral_cache = LRUCache(100000, compress=compress, obj_type=type(start_object))
        self._has_proof_tree = False
        if symmetry:
            # A list of symmetry functions of objects.
            if not isinstance(symmetry, list) or any(not callable(f) for f in symmetry):
                raise ValueError("To use symmetries need to give a list of symmetry functions.")
            self.symmetry = symmetry
        else:
            self.symmetry = []

        self.forward_equivalence = (strategy_pack.forward_equivalence
                                    or forward_equivalence)
        self.complement_verify = complement_verify

        if complement_verify:
            logger.warn("WARNING: COMPLEMENT VERIFY CAN LEAD TO TAUTOLOGIES!", extra=self.logger_kwargs)

        if strategy_pack is not None:
            if not isinstance(strategy_pack, StrategyPack):
                raise TypeError("Strategy pack given not instance of strategy pack.")
            else:
                self.equivalence_strategy_generators = strategy_pack.eq_strats
                self.strategy_generators = strategy_pack.other_strats
                self.inferral_strategies = strategy_pack.inf_strats
                self.verification_strategies = strategy_pack.ver_strats
                self.iterative = strategy_pack.iterative

        self.kwargs = function_kwargs

        if not callable(is_empty_strategy):
            raise ValueError("CombinatorialSpecificationSearcher requires a strategy that tests if an object is the empty set.")
        else:
            self.is_empty_strategy = is_empty_strategy

        self.post_expand_objects_functions = []

        if objectqueue == ObjectQueue:
            self.objectqueue = ObjectQueue()
        elif objectqueue == ObjectQueueDF:
            self.objectqueue = ObjectQueueDF(rules_dict=self.ruledb.rules_dict,
                                             root=self.start_label,
                                             equivalent_set=self.equivdb.equivalent_set)
        else:
            # Default if it does not recognize queue class
            # Give it a reference to the searcher
            self.objectqueue = objectqueue(self)


        self.objectqueue.add_to_working(self.start_label)

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
        self._cache_misses = 0  # this for status and should be updated if you use a cache
        self.logger_kwargs = logger_kwargs



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
        for verification_strategy in self.verification_strategies:
            strategy = verification_strategy(obj, **self.kwargs)
            if strategy is not None:
                if not isinstance(strategy, VerificationStrategy):
                    raise TypeError("Attempting to verify with non VerificationStrategy.")
                formal_step = strategy.formal_step
                self.objectdb.set_verified(obj, formal_step)
                self.objectdb.set_strategy_verified(obj)
                self.equivdb.update_verified(label)
                break
        self.verification_time += time.time() - start


    def is_empty(self, obj):
        """Return True if a object contains no objects, False otherwise"""
        start = time.time()
        if self.objectdb.is_empty(obj) is not None:
            self.verification_time += time.time() - start
            return self.objectdb.is_empty(obj)
        if self.is_empty_strategy(obj, **self.kwargs):
            self._add_empty_rule(self.objectdb.get_label(obj))
            self.verification_time += time.time() - start
            return True
        self.objectdb.set_empty(obj, empty=False)
        self.verification_time += time.time() - start
        return False

    def _inferral(self, obj):
        """Return fully inferred object, along with an explanation."""
        origin = obj
        start = time.time()
        inferred_object = self._inferral_cache.get(obj)
        if inferred_object is not None:
            return inferred_object
        explanation = ""
        semi_inferred = [[obj, ""]]

        for inferral_strategy in self.inferral_strategies:
            strategy = inferral_strategy(obj, **self.kwargs)
            if strategy is None:
                continue
            if not isinstance(strategy, InferralStrategy):
                raise TypeError("Attempted to infer on a non InferralStrategy")
            # TODO: Where should the inferral formal step go?
            if obj != strategy.object:
                for pair in semi_inferred:
                    pair[1] = pair[1] + strategy.formal_step
                obj = strategy.object
                inferred_object = self._inferral_cache.get(obj)
                if inferred_object is not None:
                    explanation = explanation + inferred_object[1]
                    for pair in semi_inferred:
                        pair[1] = pair[1] + inferred_object[1]
                    obj = inferred_object[0]
                    break
                semi_inferred.append([obj, ""])

        for pair in semi_inferred:
            self._inferral_cache.set(pair[0], (obj, pair[1]))

        if not semi_inferred[0][1]:
            # TODO: remove when sure it is good.
            assert origin == obj

        self.inferral_time += time.time() - start
        return obj, semi_inferred[0][1]

    def _symmetric_objects(self, obj, ordered=False, explanation=False):
        """Return all symmetries of an object.

        This function only works if symmetry strategies have been given to the
        CombinatorialSpecificationSearcher. Sometimes, the order symmetries are
        appied are important. Therefore, if order=True, this will return a list
        with each symmetry applied (this functionality is needed for inferral).
        """
        if ordered:
            return [sym(obj) for sym in self.symmetry]
        else:
            symmetric_objects = []
            for sym in self.symmetry:
                symmetric_object = sym(obj)
                if symmetric_object != obj:
                    if explanation:
                        if all(x != symmetric_object for x, _ in symmetric_objects):
                            symmetric_objects.append((symmetric_object,
                                                      str(sym).split(' ')[1]))
                    else:
                        if all(x != symmetric_object for x in symmetric_objects):
                            symmetric_object.append(symmetric_object)
        return symmetric_objects

    def expand(self, label):
        """
        Will expand the object with given label.

        The first time function called with label, it will expand with the
        first set of other strategies, second time the second set etc.
        """
        start = time.time()
        obj = self.objectdb.get_object(label)
        self.queue_time += time.time() - start
        expanding = self.objectdb.number_times_expanded(label)
        strategies = self.strategy_generators[expanding]

        total_time = 0
        for strategy_generator in strategies:
            # function returns time it took.
            total_time += self._expand_object_with_strategy(obj,
                                                            strategy_generator,
                                                            label)

        if not self.is_expanded(label):
            self.objectdb.increment_expanded(label)
            self.expanded_objects[expanding] += 1
            self.expansion_times[expanding] += total_time
            if not self.is_expanded(label):
                self.objectqueue.add_to_curr(label)

    def _expand_object_with_strategy(self, obj, strategy_generator, label, equivalent=False):
        """
        Will expand the object with given strategy.

        If equivalent, then only allow equivalent strategies to be applied and
        return objects found.
        """
        start = time.time()
        if equivalent:
            equivalent_objects = []
        for strategy in strategy_generator(obj, **self.kwargs):
            if not isinstance(strategy, Strategy):
                raise TypeError("Attempting to add non strategy type.")
            if equivalent and len(strategy.objects) != 1:
                raise TypeError("Attempting to combine non equivalent strategy.")
            start -= time.time()
            objects, formal_step = self._strategy_cleanup(strategy)
            start += time.time()
            end_labels = [self.objectdb.get_label(o) for o in objects]

            if strategy.decomposition:
                if all(self.objectdb.is_expandable(x) for x in end_labels):
                    self.objectdb.set_workably_decomposed(label)

            if not end_labels:
                # all the objects are empty so the object itself must be empty!
                self._add_empty_rule(label, "batch empty")
                break
            elif not self.forward_equivalence and len(end_labels) == 1:
                # If we have an equivalent strategy
                self._add_equivalent_rule(label, end_labels[0],
                                          formal_step, not equivalent)
                if equivalent:
                    equivalent_objects.append(objects[0])
            else:
                self._add_rule(label, end_labels,
                               strategy.back_maps, formal_step)

        # this return statements only purpose if for timing.
        if equivalent:
            return time.time() - start, equivalent_objects
        return time.time() - start

    def _add_equivalent_rule(self, start, end, explanation=None, working=False):
        """Add equivalent strategy to equivdb and equivalent object to queue"""
        if explanation is None:
            explanation = "They are equivalent."
        self.equivdb.union(start, end, explanation)
        if not (self.is_expanded(end)
                or self.objectdb.is_expanding_other_sym(end)):
            if working:
                self.objectqueue.add_to_working(end)
            else:
                self.objectqueue.add_to_next(end)

    def _add_rule(self, start, ends, back_maps=None, explanation=None):
        """Add rule to the rule database and end labels to queue."""
        if explanation is None:
            explanation = "Some strategy."
        self.ruledb.add(start,
                        ends,
                        explanation,
                        back_maps)
        for end_label in ends:
            if (self.is_expanded(end_label)
                or self.objectdb.is_expanding_other_sym(end_label)):
                continue
            self.objectqueue.add_to_next(end_label)
            obj = self.objectdb.get_object(end_label)

    def _add_empty_rule(self, label, explanation=None):
        """Mark label as empty. Treated as verified as can count empty set."""
        if self.objectdb.is_empty(label):
            return
        self.objectdb.set_empty(label)
        self.objectdb.set_verified(label, "Contains no avoiding objects.")
        self.objectdb.set_strategy_verified(label)
        self.equivdb.update_verified(label)

    def _strategy_cleanup(self, strategy):
        """
        Return cleaned strategy.

        - infer objects
        - try to verify objects
        - set workability of objects
        - remove empty objects
        - symmetry expand objects
        - equivalent expand objects.
        """
        end_objects = []
        inferral_steps = []
        for ob, work in zip(strategy.objects, strategy.workable):
            inferral_step = ""
            if not strategy.decomposition:
                ob, inferral_step = self._inferral(ob)
            else:
                inferral_step = ""

            self.try_verify(ob)

            if self.symmetry:
                self._symmetry_expand(ob)

            if not strategy.decomposition:
                if self.is_empty(ob):
                    inferral_steps.append(inferral_step + "Object is empty.")
                    continue
            if work:
                self.objectdb.set_expandable(ob)
                self._equivalent_expand(ob)

            end_objects.append(ob)
            inferral_steps.append(inferral_step)

        inferral_step = "~"
        for i, s in enumerate(inferral_steps):
            inferral_step = inferral_step + "[" + str(i) + ": " + s + "]"
        inferral_step = inferral_step + "~"
        formal_step = strategy.formal_step + inferral_step

        return end_objects, formal_step


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
            for sym_o, formal_step in self._symmetric_objects(obj,
                                                              explanation=True):
                self.objectdb.add(sym_o,
                                  expanding_other_sym=True,
                                  symmetry_expanded=True)
                self.equivdb.union(self.objectdb.get_label(obj),
                                   self.objectdb.get_label(sym_o),
                                   formal_step)
        self.symmetry_time += time.time() - start

    def _equivalent_expand(self, obj):
        """
        Equivalent expand object with given label and equivalent strategies.

        It will apply the equivalence strategies as often as possible to
        find as many equivalent objects as possible.
        """
        if (not self.objectdb.is_expandable(obj)
                or self.objectdb.is_equivalent_expanded(obj)
                    or self.objectdb.is_expanding_other_sym(obj)):
            return
        total_time = 0
        label = self.objectdb.get_label(obj)
        objects_to_expand = set()
        for strategy_generator in self.equivalence_strategy_generators:
            t, eq_objs = self._expand_object_with_strategy(obj,
                                                           strategy_generator,
                                                           label,
                                                           equivalent=True)
            total_time += t
            objects_to_expand.update(eq_objs)

        self.objectdb.set_equivalent_expanded(obj)
        self.equivalent_time += total_time

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
            if self.is_empty_strategy(self.objectdb.get_object(label)):
                continue
            count += 1
            queue_start -= time.time()
            self.expand(label)
            queue_start += time.time()
        # TODO: Maybe you don't want timing to be affected by this
        for function, args, kwargs in self.post_expand_objects_functions:
            function(*args, **kwargs)
        self.queue_time += time.time() - queue_start
        self._time_taken += time.time() - start

    def status(self):
        """
        Return a string of the current status of the tilescope.

        It includes:
        - number of objects, and information about verification
        - the times spent in each of the main functions
        """
        status = ""
        status += "Currently on 'level' {}\n".format(str(self.objectqueue.levels_completed + 1))
        status += "Time spent searching so far: {} seconds\n".format(self._time_taken)
        for i, expanded in enumerate(self.expanded_objects):
            status += "Number of objects expanded by Set {} is {}\n".format(str(i+1),   str(expanded))
        status += "The size of the working queue is {}\n".format(self.objectqueue.working.qsize())
        status += "The size of the current queue is {}\n".format(self.objectqueue.curr_level.qsize())
        status += "The size of the next queue is {}\n".format(self.objectqueue.next_level.qsize())
        status += "There were {} cache misses\n".format(str(self._cache_misses))



        all_labels = self.objectdb.label_to_info.keys()
        status += "Total number of objects is {}\n".format(str(len(all_labels)))
        expandable = 0
        verified = 0
        strategy_verified = 0
        empty = 0
        equivalent_sets = set()
        for label in all_labels:
            if self.objectdb.is_expandable(label):
                expandable += 1
            if self.equivdb.is_verified(label):
                verified += 1
            if self.objectdb.is_strategy_verified(label):
                strategy_verified += 1
            if self.objectdb.is_empty(label):
                empty += 1
            equivalent_sets.add(self.equivdb[label])

        status += "Total number of equivalent sets is {}\n".format(str(len(equivalent_sets)))
        status += "Total number of expandable objects is {}\n".format(str(expandable))
        status += "Total number of verified objects is {}\n".format(str(verified))
        status += "Total number of strategy verified objects is {}\n".format(str(strategy_verified))
        status += "Total number of empty objects is {}\n".format(str(empty))

        equiv_perc = int(self.equivalent_time/self._time_taken * 100)
        verif_perc = int(self.verification_time/self._time_taken * 100)
        infer_perc = int(self.inferral_time/self._time_taken * 100)
        symme_perc = int(self.symmetry_time/self._time_taken * 100)

        status += "Time spent equivalent expanding: {} seconds, ~{}%\n".format(str(self.equivalent_time), equiv_perc)
        status += "Time spent strategy verifying: {} seconds, ~{}%\n".format(str(self.verification_time), verif_perc)
        status += "Time spent inferring: {} seconds, ~{}%\n".format(str(self.inferral_time), infer_perc)

        if self.symmetry:
            status += "Time spent symmetry expanding: {} seconds, ~{}%\n".format(str(self.symmetry_time), symme_perc)

        for i, exp_time in enumerate(self.expansion_times):
            expand_perc = str(int(exp_time/self._time_taken * 100))
            status += "Time spent expanding Set {}: {} seconds, ~{}%\n".format(str(i+1), str(exp_time), expand_perc)

        queue_perc = int(self.queue_time/self._time_taken * 100)
        prep_time = self.prepping_for_tree_search_time
        prpts_perc = int(prep_time/self._time_taken * 100)
        tsrch_perc = int(self.tree_search_time/self._time_taken * 100)

        status += "Time spent queueing: {} seconds, ~{}%\n".format(str(self.queue_time), queue_perc)
        status += "Time spent prepping for tree search: {} seconds, ~{}%\n".format(str(prep_time), prpts_perc)
        status += "Time spent searching for tree: {} seconds, ~{}%\n".format(str(self.tree_search_time), tsrch_perc)

        total_perc = equiv_perc+verif_perc+infer_perc+symme_perc+queue_perc+prpts_perc+tsrch_perc
        for i, exp_time in enumerate(self.expansion_times):
            total_perc += int(exp_time/self._time_taken * 100)
        status += "Total of ~{}% accounted for.\n".format(str(total_perc))
        return status

    def _strategies_to_str(self, strategies):
        """Return names of strategies/functions."""
        if not strategies:
            return ""
        output = str(strategies[0]).split(' ')[1]
        for strategy in strategies[1:]:
            output = output + ", " + str(strategy).split(' ')[1]
        return output

    def auto_search(self, cap=100, verbose=False, status_update=None, max_time=None):
        """
        An automatic search function.

        It will expand objects until cap*(tree search time) has passed and then
        search for a tree.

        If verbose=True, a status update is given when a tree is found and
        after status_update many seconds have passed. It will also print
        the proof tree, in json formats.
        """
        if verbose:
            if status_update:
                status_start = time.time()
            start_string = ""
            start_string += "Auto search started {}\n".format(time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()))
            start_string += "Looking for {} combinatorial specification for:\n".format('iterative' if self.iterative else 'recursive')
            start_string += self.objectdb.get_object(self.start_label).__repr__()
            start_string += "\n"
            start_string += "The strategies being used are:\n"
            equiv_strats = self._strategies_to_str(self.equivalence_strategy_generators)
            infer_strats = self._strategies_to_str(self.inferral_strategies)
            verif_strats = self._strategies_to_str(self.verification_strategies)
            start_string += "Equivalent: {}\n".format(equiv_strats)
            start_string += "Inferral: {}\n".format(infer_strats)
            start_string += "Verification: {}\n".format(verif_strats)
            if self.forward_equivalence:
                start_string += "Using forward equivalence only.\n"
            if self.symmetry:
                symme_strats = self._strategies_to_str(self.symmetry)
                start_string += "Symmetries: {}\n".format(symme_strats)
            for i, strategies in enumerate(self.strategy_generators):
                strats = self._strategies_to_str(strategies)
                start_string += "Set {}: {}\n".format(str(i+1), strats)
            logger.info(start_string, extra=self.logger_kwargs)

        max_search_time = 0
        expanding = True
        while expanding:
            start = time.time() + 0.00001
            while time.time() - start < max_search_time:
                if status_update is not None and verbose:
                    if time.time() - status_start > status_update:
                        status = self.status()
                        logger.info(status, extra=self.logger_kwargs)
                        status_start = time.time()
                if self.expand_objects(1):
                    expanding = False
                    break


            # TODO: if the above functions does nothing, it returns True,
            #       need to catch this in a better way.
            start = time.time()
            logger.debug("Searching for tree", extra=self.logger_kwargs)
            proof_tree = self.get_proof_tree()
            max_search_time = min(cap*(time.time() - start), 3600) #worst case, search every hour!
            if proof_tree is not None:
                if verbose:
                    found_string = "Proof tree found {}\n".format(time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()))
                    found_string += "Time taken was {} seconds\n\n".format(self._time_taken)
                    found_string += self.status()
                    found_string += json.dumps(proof_tree.to_jsonable())
                    logger.info(found_string, extra=self.logger_kwargs)
                return proof_tree
            if max_time is not None:
                if self._time_taken > max_time:
                    self.status()
                    logger.warn("Exceeded maximum time. Aborting auto search.", extra=self.logger_kwargs)
                    return



    def has_proof_tree(self):
        """Return True if a proof tree has been found, false otherwise."""
        return self._has_proof_tree

    def tree_search_prep(self, complement=False):
        """
        Return rule dictionary ready for tree searcher.

        Also adds complement verified rules when applicable. If empty preps to
        search for empty proof trees.
        """
        start_time = time.time()
        rules_dict = defaultdict(set)

        rules_to_add = []
        for rule in self.ruledb:
            if self.complement_verify:
                complement_rule = self.complement_verified(rule)
                if complement_rule is not None:
                    rules_to_add.append((complement_rule, rule))
                    self._add_rule_to_rules_dict(complement_rule, rules_dict)
                else:
                    self._add_rule_to_rules_dict(rule, rules_dict)
            else:
                self._add_rule_to_rules_dict(rule, rules_dict)

        for rules in rules_to_add:
            good_rule, old_rule = rules
            start, ends = good_rule
            self._add_rule(start, ends, explanation="Complement verified.")
            self.ruledb.remove(*old_rule)


        for label in self.objectdb.verified_labels():
            verified_label = self.equivdb[label]
            rules_dict[verified_label] |= set(((),))

        self.prepping_for_tree_search_time += time.time() - start_time
        return rules_dict

    def _add_rule_to_rules_dict(self, rule, rules_dict):
        """Add a rule to given dictionary."""
        first, rest = rule
        eqv_first = self.equivdb[first]
        eqv_rest = tuple(sorted(self.equivdb[x] for x in rest))
        rules_dict[eqv_first] |= set((tuple(eqv_rest),))

    def complement_verified(self, rule):
        """Return complement verified rule if exists due to rule, else None"""
        first, rest = rule
        if self.equivdb.is_verified(first):
            unverified_labels = [l for l in rest if not self.equivdb.is_verified(l)]
            if len(unverified_labels) == 1:
                complement_first = unverified_labels[0]
                return (complement_first,
                        (first, ) + tuple(l for l in rest if l != complement_first))

    def equivalent_strategy_verified_label(self, label):
        """Return equivalent strategy verified label if one exists, else None"""
        for eqv_label in self.equivdb.equivalent_set(label):
            if self.objectdb.is_strategy_verified(eqv_label):
                return eqv_label

    def rule_from_equivence_rule(self, eqv_start, eqv_ends):
        for rule in self.ruledb:
            start, ends = rule
            if not self.equivdb.equivalent(start, eqv_start):
                continue
            if tuple(sorted(eqv_ends)) == tuple(sorted(self.equivdb[l] for l in ends)):
                return start, ends

    def find_tree(self):
        """Search for a tree based on current data found."""
        start = time.time()

        rules_dict = self.tree_search_prep()
        # Prune all unverified labels (recursively)
        if self.iterative:
            rules_dict = iterative_prune(rules_dict,
                                         root=self.equivdb[self.start_label])
        else:
            rules_dict = prune(rules_dict)

        # only verified labels in rules_dict, in particular, there is an proof
        # tree if the start label is in the rules_dict
        for label in rules_dict.keys():
            self.equivdb.update_verified(label)

        if self.equivdb[self.start_label] in rules_dict:
            self._has_proof_tree = True
            if self.iterative:
                proof_tree = iterative_proof_tree_bfs(rules_dict,
                                        root=self.equivdb[self.start_label])
            else:
                _, proof_tree = proof_tree_bfs(rules_dict,
                                        root=self.equivdb[self.start_label])
        else:
            proof_tree = None

        self.tree_search_time += time.time() - start
        self._time_taken += time.time() - start
        return proof_tree


    def get_proof_tree(self, count=False):
        """
        Return proof tree if one exists.
        """
        proof_tree_node = self.find_tree()
        if proof_tree_node is not None:
            proof_tree = ProofTree.from_comb_spec_searcher(proof_tree_node, self)
            assert proof_tree is not None
            return proof_tree
