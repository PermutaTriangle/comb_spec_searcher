"""
A proof tree class.

This can be used to get the generating function for the class.

The class is only used for reverse compatibility with ComboPal. You should use
the Specification class.
"""
import json
import warnings
from typing import Iterable, List, Optional

from .combinatorial_class import CombinatorialClass
from .specification import CombinatorialSpecification
from .strategies.constructor import CartesianProduct, Constructor, DisjointUnion
from .strategies.rule import EquivalencePathRule, Rule, VerificationRule

__all__ = ("ProofTree",)


class ProofTreeNode:
    """Class is deprecated - use CombinatorialSpecification."""

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        label: int,
        eqv_path_labels: Iterable[int],
        eqv_path_comb_classes: Iterable[CombinatorialClass],
        eqv_explanations: Iterable[str] = None,
        children: Iterable["ProofTreeNode"] = None,
        strategy_verified: bool = False,
        decomposition: bool = False,
        disjoint_union: bool = False,
        recursion: bool = False,
        formal_step: str = "",
    ):
        self.label = label
        self.eqv_path_labels = list(eqv_path_labels)
        self.eqv_path_comb_classes = list(eqv_path_comb_classes)
        if eqv_explanations is not None:
            self.eqv_explanations = list(eqv_explanations)
        else:
            self.eqv_explanations = []
        self.children = list(children) if children is not None else []
        self.strategy_verified = strategy_verified
        self.decomposition = decomposition
        self.disjoint_union = disjoint_union
        self.recursion = recursion
        self.formal_step = formal_step

    def to_jsonable(self):
        """Class is deprecated - use CombinatorialSpecification."""
        output = dict()
        output["label"] = self.label
        output["eqv_path_labels"] = list(self.eqv_path_labels)
        output["eqv_path_comb_classes"] = [
            x.to_jsonable() for x in self.eqv_path_comb_classes
        ]
        output["eqv_explanations"] = list(self.eqv_explanations)
        output["children"] = [child.to_jsonable() for child in self.children]
        output["strategy_verified"] = self.strategy_verified
        output["decomposition"] = self.decomposition
        output["disjoint_union"] = self.disjoint_union
        output["recursion"] = self.recursion
        output["formal_step"] = self.formal_step
        return output

    @classmethod
    def from_dict(cls, combclass, jsondict):
        """Class is deprecated - use CombinatorialSpecification."""
        if "eqv_path_objects" in jsondict:
            warnings.warn(
                (
                    "The 'eqv_path_objects' label is deprecated. You "
                    "should change this to 'eqv_path_comb_classes"
                    " in the future."
                ),
                DeprecationWarning,
                stacklevel=2,
            )
            jsondict["eqv_path_comb_classes"] = jsondict["eqv_path_objects"]
        return cls(
            label=jsondict["label"],
            eqv_path_labels=jsondict["eqv_path_labels"],
            eqv_path_comb_classes=[
                combclass.from_dict(x) for x in jsondict["eqv_path_comb_classes"]
            ],
            eqv_explanations=jsondict["eqv_explanations"],
            children=[
                ProofTreeNode.from_dict(combclass, child)
                for child in jsondict["children"]
            ],
            strategy_verified=jsondict["strategy_verified"],
            decomposition=jsondict["decomposition"],
            disjoint_union=jsondict["disjoint_union"],
            recursion=jsondict["recursion"],
            formal_step=jsondict["formal_step"],
        )

    @classmethod
    def from_json(cls, combclass, jsonstr):
        """Class is deprecated - use CombinatorialSpecification."""
        warnings.warn("ProofTreeNode is deprecated, use CombinatorialSpecification")
        jsondict = json.loads(jsonstr)
        return cls.from_dict(combclass, jsondict)


class ProofTree:
    """Class is deprecated - use CombinatorialSpecification."""

    def __init__(self, root):
        warnings.warn(
            (
                "The ProofTree class is deprecated."
                " Use CombinatorialSpecification instead."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        if not isinstance(root, ProofTreeNode):
            raise TypeError("Root must be a ProofTreeNode.")
        self.root = root

    def to_jsonable(self):
        """Class is deprecated - use CombinatorialSpecification."""
        return {"root": self.root.to_jsonable()}

    @classmethod
    def from_dict(cls, combclass, jsondict):
        """Class is deprecated - use CombinatorialSpecification."""
        root = ProofTreeNode.from_dict(combclass, jsondict["root"])
        return cls(root)

    @classmethod
    def from_json(cls, combclass, jsonstr):
        """Class is deprecated - use CombinatorialSpecification."""
        jsondict = json.loads(jsonstr)
        return cls.from_dict(combclass, jsondict)

    @classmethod
    def from_specification(cls, spec: CombinatorialSpecification) -> "ProofTree":
        """Return a ProofTree from a CombinatorialSpecification."""
        seen: List[Rule] = list()

        def proof_tree_node(comb_class: CombinatorialClass) -> ProofTreeNode:
            rule = spec.get_rule(comb_class)
            # Setting up the equivalence path
            if isinstance(rule, EquivalencePathRule):
                eqv_path_labels: List[int] = []
                eqv_path_comb_classes: List[CombinatorialClass] = []
                eqv_explanations: List[str] = []
                for path_class, eqv_rule in rule.eqv_path_rules():
                    eqv_path_labels.append(spec.get_label(path_class))
                    eqv_path_comb_classes.append(path_class)
                    eqv_explanations.append(eqv_rule.formal_step)
                eqv_path_comb_classes.append(rule.children[0])
                rule = spec.rules_dict[rule.children[0]]
            else:
                eqv_path_labels = [spec.get_label(rule.comb_class)]
                eqv_path_comb_classes = [rule.comb_class]
                eqv_explanations = []
            if isinstance(rule, VerificationRule):
                return ProofTreeNode(
                    label=spec.get_label(rule.comb_class),
                    eqv_path_labels=eqv_path_labels,
                    eqv_path_comb_classes=eqv_path_comb_classes,
                    eqv_explanations=eqv_explanations,
                    children=[],
                    strategy_verified=True,
                    formal_step=rule.formal_step,
                )
            if isinstance(rule, Rule):
                if rule in seen:
                    # Setting up recursion node
                    return ProofTreeNode(
                        label=spec.get_label(rule.comb_class),
                        eqv_path_labels=eqv_path_labels,
                        eqv_path_comb_classes=eqv_path_comb_classes,
                        eqv_explanations=eqv_explanations,
                        children=[],
                        strategy_verified=False,
                        recursion=True,
                        formal_step="recurse",
                    )
                seen.append(rule)
                children = [proof_tree_node(c) for c in rule.children]
                try:
                    constructor: Optional[Constructor] = rule.constructor
                except NotImplementedError:
                    constructor = None
                return ProofTreeNode(
                    label=spec.get_label(rule.comb_class),
                    eqv_path_labels=eqv_path_labels,
                    eqv_path_comb_classes=eqv_path_comb_classes,
                    eqv_explanations=eqv_explanations,
                    children=children,
                    decomposition=isinstance(constructor, CartesianProduct),
                    disjoint_union=isinstance(constructor, DisjointUnion),
                    strategy_verified=False,
                    formal_step=rule.formal_step,
                )
            raise ValueError(f"Don't know what to do with the rule class of {rule}")

        return ProofTree(proof_tree_node(spec.root))
