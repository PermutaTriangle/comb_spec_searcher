"""
A module that create the rule key and the shifts for a given rule.

TODO: Do not merge with this. Should be delegated to the rule class.
"""
import itertools
import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, Optional, Set, Tuple

from logzero import logger

from comb_spec_searcher.rule_db.forest import RuleBucket
from comb_spec_searcher.strategies.constructor import CartesianProduct, DisjointUnion
from comb_spec_searcher.strategies.rule import AbstractRule, Rule, VerificationRule
from comb_spec_searcher.typing import RuleKey
from permuta import Basis

if TYPE_CHECKING:
    from tilings import GriddedPerm, Tiling

    from comb_spec_searcher import CombinatorialSpecification

RFIt = Iterator[Tuple[RuleKey, Tuple[int, ...], RuleBucket]]

__all__ = ["all_flips"]


def all_flips(rule: AbstractRule, labeller: Callable[[Any], int]) -> RFIt:
    """
    Return all the possible rulekey and shifts for this rule.

    It considers all the possible flips.
    """
    start_label = labeller(rule.comb_class)
    end_labels = tuple(map(labeller, rule.children))
    rule_key = (start_label, end_labels)
    if isinstance(rule, VerificationRule):
        if not end_labels:
            yield rule_key, tuple(), RuleBucket.VERIFICATION
        elif len(end_labels) == 1:
            yield rule_key, (
                LocallyFactorableShift(rule).shift(),
            ), RuleBucket.VERIFICATION
        else:
            raise NotImplementedError("Verification rule with many children")
    elif isinstance(rule, Rule):
        if isinstance(rule.constructor, DisjointUnion):
            yield from _all_union_flips(rule_key)
        elif isinstance(rule.constructor, CartesianProduct):
            yield from _all_cartesian_flips(rule_key, rule)
        elif "fuse" in rule.formal_step:
            yield from _all_fusion_flips(rule_key, rule)
        elif "adding the assumption" in rule.formal_step:
            yield from _all_add_assumption_flips(rule_key)
        elif "rearranging the assumption" in rule.formal_step:
            yield from _all_rearrange_flips(rule_key)
        else:
            raise NotImplementedError(rule)
    else:
        raise NotImplementedError


def _all_union_flips(rule_key: RuleKey) -> RFIt:
    shifts = tuple(0 for _ in rule_key[1])
    yield rule_key, shifts, RuleBucket.NORMAL
    for i, l in enumerate(rule_key[1]):
        children = (rule_key[0],) + rule_key[1][:i] + rule_key[1][i + 1 :]
        yield (l, children), shifts, RuleBucket.REVERSE


def _all_cartesian_flips(rule_key: RuleKey, rule: Rule) -> RFIt:
    min_points = tuple(len(next(c.minimal_gridded_perms())) for c in rule.children)
    point_sum = sum(min_points)
    shifts = tuple(point_sum - mpoint for mpoint in min_points)
    yield rule_key, shifts, RuleBucket.NORMAL
    for i, l in enumerate(rule_key[1]):
        children = (rule_key[0],) + rule_key[1][:i] + rule_key[1][i + 1 :]
        nshifts = (-shifts[i],) + tuple(
            s - shifts[i] for s in shifts[:i] + shifts[i + 1 :]
        )
        yield (l, children), nshifts, RuleBucket.REVERSE


def _all_fusion_flips(rule_key: RuleKey, rule: Rule) -> RFIt:
    yield rule_key, (0,), RuleBucket.NORMAL
    if rule.is_two_way():
        parent = rule_key[0]
        child = rule_key[1][0]
        yield (child, (parent,)), (0,), RuleBucket.REVERSE


def _all_add_assumption_flips(rule_key: RuleKey) -> RFIt:
    yield rule_key, (0,), RuleBucket.NORMAL


def _all_rearrange_flips(rule_key: RuleKey) -> RFIt:
    yield rule_key, (0,), RuleBucket.NORMAL
    parent = rule_key[0]
    child = rule_key[1][0]
    yield (child, (parent,)), (0,), RuleBucket.REVERSE


class LocallyFactorableShift:
    def __init__(self, rule: VerificationRule, basis: Optional[Basis] = None) -> None:
        self.rule = rule
        if basis is None:
            assert len(rule.children) == 1
            t = rule.children[0]
            assert t.dimensions == (1, 1)
            self.basis = self.cell_basis(t).pop()
        else:
            self.basis = basis
        self.spec = self._get_spec()
        self.traverse_cache: Dict[Tiling, Optional[int]] = {}

    def _get_spec(self) -> "CombinatorialSpecification[Tiling, GriddedPerm]":
        from comb_spec_searcher import CombinatorialSpecificationSearcher

        pack = self.rule.pack()
        logger.setLevel(logging.WARN)
        css = CombinatorialSpecificationSearcher(self.rule.comb_class, pack)
        spec = css.auto_search()
        logger.setLevel(logging.INFO)
        return spec

    @staticmethod
    def cell_basis(t: "Tiling") -> Set[Basis]:
        """
        Return the one by one classes in the cells.
        """
        all_bases: Set[Basis] = set()
        for obs, _ in t.cell_basis().values():
            b = Basis.from_iterable(obs)
            all_bases.add(b)
        return all_bases

    def _reliance(self, t: "Tiling") -> Optional[int]:
        """
        Return the reliance of the tiling on the basis according to the spec.
        """
        rule = self.spec.rules_dict[t]
        if t in self.traverse_cache:
            return self.traverse_cache[t]
        if self.basis not in self.cell_basis(t):
            res = None
        elif t.dimensions == (1, 1):
            res = 0
        elif isinstance(rule, VerificationRule):
            res = LocallyFactorableShift(rule, self.basis).shift()
        elif isinstance(rule, Rule) and isinstance(rule.constructor, DisjointUnion):
            children_reliance = [self._reliance(c) for c in rule.children]
            res = min([r for r in children_reliance if r is not None], default=None)
        elif isinstance(rule, Rule) and isinstance(rule.constructor, CartesianProduct):
            min_points = [len(next(c.minimal_gridded_perms())) for c in rule.children]
            point_sum = sum(min_points)
            shifts = [point_sum - mpoint for mpoint in min_points]
            children_reliance = [self._reliance(c) for c in rule.children]
            res = min(
                [r + s for r, s in zip(children_reliance, shifts) if r is not None],
                default=None,
            )
        else:
            raise NotImplementedError(rule)
        self.traverse_cache[t] = res
        return res

    def shift_from_spec(self) -> int:
        res = self._reliance(self.rule.comb_class)
        assert res is not None
        return res

    def shift_from_theory(self) -> int:
        """
        The shift from the conjectured formula.
        """
        min_gps = self.rule.comb_class.minimal_gridded_perms()
        cells_with_basis = [
            cell
            for cell, (obs, _) in self.rule.comb_class.cell_basis().items()
            if Basis.from_iterable(obs) == self.basis
        ]
        return min(
            sum(1 for c in gp.pos if c != cell)
            for cell, gp in itertools.product(cells_with_basis, min_gps)
        )

    def shift(self) -> int:
        from_spec = self.shift_from_spec()
        from_conjecture = self.shift_from_theory()
        if from_spec != from_conjecture:
            err = f"The conjecture failed for the rule:\n{self.rule}\n"
            err += f"The basis was {self.basis}\n"
            err += f"The conjecture gave shift {from_conjecture}\n"
            err += f"The specification gave the shift {from_spec}\n"
            raise RuntimeError(err)
        return from_conjecture
