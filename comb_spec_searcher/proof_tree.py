"""
A proof tree class.

This can be used to get the generating function for the class.

The class is only used for reverse compatability with ComboPal. You should use
the Specification class.
"""
import json
import warnings

from .specification import CombinatorialSpecification
from .strategies.constructor import CartesianProduct, DisjointUnion
from .strategies.rule import EquivalencePathRule, Rule, VerificationRule

__all__ = ("ProofTree",)


class ProofTreeNode:
    """Class is deprecated - use CombinatorialSpecification."""

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        label,
        eqv_path_labels,
        eqv_path_comb_classes,
        eqv_explanations=None,
        children=None,
        strategy_verified=False,
        decomposition=False,
        disjoint_union=False,
        recursion=False,
        formal_step="",
    ):
        self.label = label
        self.eqv_path_labels = eqv_path_labels
        self.eqv_path_comb_classes = eqv_path_comb_classes
        if eqv_explanations is not None:
            self.eqv_explanations = eqv_explanations
        else:
            self.eqv_explanations = []
        self.children = children if children is not None else []
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
        nodes = dict()
        eqv_paths = dict()
        # find equivalence paths and setup nodes without equivalence and children
        for rule in spec.rules_dict.values():
            if isinstance(rule, EquivalencePathRule):
                eqv_path_labels = []
                eqv_path_comb_classes = []
                eqv_explanations = []
                for comb_class, eqv_rule in rule.eqv_path_rules():
                    eqv_path_labels.append(spec.get_label(comb_class))
                    eqv_path_comb_classes.append(comb_class)
                    eqv_explanations.append(eqv_rule.formal_step)
                eqv_path_comb_classes.append(rule.children[0])
                eqv_paths[rule.comb_class] = (
                    eqv_path_labels,
                    eqv_path_comb_classes,
                    eqv_explanations,
                )
            elif isinstance(rule, VerificationRule):
                nodes[rule.comb_class] = ProofTreeNode(
                    label=spec.get_label(rule.comb_class),
                    eqv_path_labels=[spec.get_label(rule.comb_class)],
                    eqv_path_comb_classes=[rule.comb_class],
                    eqv_explanations=[],
                    children=[],
                    strategy_verified=True,
                    formal_step=rule.formal_step,
                )
            elif isinstance(rule, Rule):
                nodes[rule.comb_class] = ProofTreeNode(
                    label=spec.get_label(rule.comb_class),
                    eqv_path_labels=[spec.get_label(rule.comb_class)],
                    eqv_path_comb_classes=[rule.comb_class],
                    eqv_explanations=[],
                    children=list(rule.children),
                    decomposition=isinstance(rule.constructor, CartesianProduct),
                    disjoint_union=isinstance(rule.constructor, DisjointUnion),
                    strategy_verified=False,
                    formal_step=rule.formal_step,
                )
            else:
                raise ValueError(f"Don't know what to do with the rule class of {rule}")

        # fix equiv paths and children
        for node in list(nodes.values()):
            if node.children:
                new_children = []
                for child in node.children:
                    if child in eqv_paths:
                        (
                            eqv_path_labels,
                            eqv_path_comb_classes,
                            eqv_explanations,
                        ) = eqv_paths[child]
                        eqv_node = nodes[eqv_path_comb_classes[-1]]
                        eqv_node.eqv_path_labels = eqv_path_labels
                        eqv_node.eqv_path_comb_classes = eqv_path_comb_classes
                        eqv_node.eqv_explanations = eqv_explanations
                        new_children.append(nodes[eqv_path_comb_classes[-1]])
                    else:
                        new_children.append(nodes[child])
                node.children = new_children
        # fix root in eqv paths
        if spec.root in eqv_paths:
            (eqv_path_labels, eqv_path_comb_classes, eqv_explanations) = eqv_paths[
                spec.root
            ]

            eqv_node = nodes.pop(eqv_path_comb_classes[-1])
            eqv_node.eqv_path_labels = eqv_path_labels
            eqv_node.eqv_path_comb_classes = eqv_path_comb_classes
            eqv_node.eqv_explanations = eqv_explanations
            nodes[spec.root] = eqv_node

        seen = set()
        queue = [spec.root]
        copy_nodes: dict = {**nodes}
        while copy_nodes and queue:
            curr = queue.pop()
            seen.add(curr)
            node = copy_nodes.pop(curr, None)
            if node is not None:
                node = nodes[curr]
                for i, child in enumerate(node.children):
                    if not child.strategy_verified and any(
                        c in seen for c in child.eqv_path_comb_classes
                    ):
                        node.children[i] = ProofTreeNode(
                            label=child.label,
                            eqv_path_labels=child.eqv_path_labels,
                            eqv_path_comb_classes=child.eqv_path_comb_classes,
                            eqv_explanations=child.eqv_explanations,
                            children=[],
                            strategy_verified=False,
                            recursion=True,
                            formal_step="recurse",
                        )
                    else:
                        queue.append(child.eqv_path_comb_classes[-1])

        return ProofTree(nodes[spec.root])
