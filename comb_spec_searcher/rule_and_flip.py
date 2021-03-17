"""
A module that create the rule key and the shifts for a given rule.

TODO: Do not merge with this. Should be delegated to the rule class.
"""
from typing import Any, Callable, Iterator, Tuple

from comb_spec_searcher.strategies.constructor import CartesianProduct, DisjointUnion
from comb_spec_searcher.strategies.rule import AbstractRule, Rule, VerificationRule
from comb_spec_searcher.typing import RuleKey

RFIt = Iterator[Tuple[RuleKey, Tuple[int, ...]]]

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
        assert not end_labels
        yield rule_key, tuple()
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
    yield rule_key, shifts
    for i, l in enumerate(rule_key[1]):
        children = (rule_key[0],) + rule_key[1][:i] + rule_key[1][i + 1 :]
        yield (l, children), shifts


def _all_cartesian_flips(rule_key: RuleKey, rule: Rule) -> RFIt:
    min_points = tuple(len(next(c.minimal_gridded_perms())) for c in rule.children)
    point_sum = sum(min_points)
    shifts = tuple(point_sum - mpoint for mpoint in min_points)
    yield rule_key, shifts
    for i, l in enumerate(rule_key[1]):
        children = (rule_key[0],) + rule_key[1][:i] + rule_key[1][i + 1 :]
        nshifts = (-shifts[i],) + tuple(
            s - shifts[i] for s in shifts[:i] + shifts[i + 1 :]
        )
        yield (l, children), nshifts


def _all_fusion_flips(rule_key: RuleKey, rule: Rule) -> RFIt:
    yield rule_key, (0,)
    if rule.is_two_way():
        parent = rule_key[0]
        child = rule_key[1][0]
        yield (child, (parent,)), (0,)


def _all_add_assumption_flips(rule_key: RuleKey) -> RFIt:
    yield rule_key, (0,)


def _all_rearrange_flips(rule_key: RuleKey) -> RFIt:
    yield rule_key, (0,)
    parent = rule_key[0]
    child = rule_key[1][0]
    yield (child, (parent,)), (0,)
