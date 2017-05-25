import sys

from permuta import Av
from permuta.permutils import lex_min

from grids import JsonAble, Tiling, Cell
from collections import Counter
from functools import reduce
from operator import add, mul

__all__ = ["ProofTree", "ProofTreeNode"]


class ProofTreeNode(JsonAble):
    def __init__(self,
                 formal_step,
                 in_tiling,
                 out_tiling,
                 relation,
                 identifier,
                 children=None,
                 recurse=None):
        self.formal_step = formal_step
        self.in_tiling = in_tiling
        self.out_tiling = out_tiling
        self.relation = relation
        self.identifier = identifier
        self.children = [] if children is None else list(children)
        self.recurse = [] if children is None else list(recurse)

    @classmethod
    def _from_attr_dict(cls, attr_dict):
        formal_step = attr_dict["formal_step"]
        in_tiling = Tiling._from_attr_dict(attr_dict["in_tiling"])
        out_tiling = Tiling._from_attr_dict(attr_dict["out_tiling"])
        relation = attr_dict["relation"]
        identifier = attr_dict["identifier"]
        children = map(cls._from_attr_dict, attr_dict["children"])
        recurse = eval(attr_dict["recurse"])
        return cls(formal_step,
                   in_tiling,
                   out_tiling,
                   relation,
                   identifier,
                   children,
                   recurse)

    def _get_attr_dict(self):
        attr_dict = {}
        attr_dict["formal_step"] = self.formal_step
        attr_dict["in_tiling"] = self.in_tiling._get_attr_dict()
        attr_dict["out_tiling"] = self.out_tiling._get_attr_dict()
        attr_dict["relation"] = self.relation
        attr_dict["identifier"] = self.identifier
        attr_dict["children"] = [child._get_attr_dict() for child in self.children]
        attr_dict["recurse"] = repr(self.recurse)
        return attr_dict


class ProofTree(JsonAble):
    _NODE_CLASS = ProofTreeNode
    __PRETTY_PRINT_DICT = dict(L="└─────", pipe="│     ", T="├─────", empty="      ")

    def __init__(self, root):
        self.root = root

    @classmethod
    def _from_attr_dict(cls, attr_dict):
        root = cls._NODE_CLASS._from_attr_dict(attr_dict["root"])
        return cls(root)

    def _get_attr_dict(self):
        attr_dict = {}
        attr_dict["root"] = self.root._get_attr_dict()
        return attr_dict

    def get_funcs(self):
        """Creates a dictionary mapping from identifiers to function names"""
        funcs = {}
        self._get_funcs(self.root, funcs)
        return funcs

    def _get_funcs(self, root, funcs):
        from sympy import Function
        if root.identifier not in funcs:
            funcs[root.identifier] = Function("F_"+str(root.identifier))
        for child in root.children:
            self._get_funcs(child, funcs)

    def get_equations(self, funcs, avoid):
        return self._get_equations(self.root, funcs, avoid)

    def _get_equations(self, root, funcs, avoid):
        from .Helpers import get_tiling_genf
        from sympy import Eq
        from sympy.abc import x
        lhs = funcs[root.identifier](x)
        rhs = 0
        if root.formal_step == "recurse":
            return []
        if root.recurse:
            rhs = reduce(mul, [funcs[child.identifier](x) for child in root.children], 1)
        elif root.children:
            rhs = reduce(add, [funcs[child.identifier](x) for child in root.children], 0)
        elif "contains no" in root.formal_step:
            rhs = 0
        else:
            rhs = get_tiling_genf(root.out_tiling, root.identifier, avoid, funcs[self.root.identifier](x))
        return reduce(add, [self._get_equations(child, funcs, avoid) for child in root.children], [Eq(lhs, rhs)])

    def get_genf(self, verify=10, equations=False, expansion=False):
        from .Helpers import taylor_expand
        from sympy import solve
        from sympy.abc import x
        if self.get_recursion_type() > 2:
            raise RuntimeError("Can not find generating function, due to interleaving decomposition. ")
        funcs = self.get_funcs()
        f = funcs[self.root.identifier]
        avoid = self.root.in_tiling[Cell(i=0,j=0)]
        avoid = Av(lex_min(list(avoid.basis)))
        eqs = self.get_equations(funcs, avoid)
        solutions = solve(eqs, tuple([eq.lhs for eq in eqs]), dict=True)
        if solutions:
            coeffs = [len(avoid.of_length(i)) for i in range(verify+1)]
            for solution in solutions:
                expansion = taylor_expand(solution[f(x)], verify)
                if coeffs == expansion:
                    sol = solution[f(x)].expand().simplify()
                    if expansion:
                        if equations:
                            return sol,eqs,expansion
                        return sol,expansion
                    if equations:
                        return sol,eqs
                    return sol
            raise RuntimeError("Incorrect generating function\n" + str(solutions))
        raise RuntimeError("No solution was found for this tree")

    def get_recursion_type(self):
        return self._get_recursion_type(self.root)

    def _get_recursion_type(self, root):
        res = 0
        if root.recurse:
            mixing = False
            x = [{c.i for c in dic.values()} for dic in root.recurse]
            y = [{c.j for c in dic.values()} for dic in root.recurse]
            simple = False
            for i in range(len(root.recurse)):
                if root.children[i].formal_step == "recurse":
                    simple = True
                for j in range(len(root.recurse)):
                    if i != j:
                        if len(x[i] & x[j]) > 0 or len(y[i] & y[j]) > 0:
                            mixing = True
            if mixing:
                return 3
            if simple:
                res = 2
            else:
                res = 1
        if root.children:
            res = max(res, max(self._get_recursion_type(child) for child in root.children))
        return res

    def get_recursion_count(self):
        return self._get_recursion_count(self.root)

    def _get_recursion_count(self, root):
        cnt = Counter()
        if root.recurse:
            found = False
            x = [{c.i for c in dic.values()} for dic in root.recurse]
            y = [{c.j for c in dic.values()} for dic in root.recurse]
            simple = False
            for i in range(len(root.recurse)):
                if root.children[i].formal_step == "recurse":
                    simple = True
                for j in range(len(root.recurse)):
                    if i != j:
                        if len(x[i] & x[j]) > 0 or len(y[i] & y[j]) > 0:
                            found = True
            if found:
                cnt[3] += 1
            elif simple:
                cnt[2] += 1
            else:
                cnt[1] += 1
        if root.children:
            cnt = reduce(add, (self._get_recursion_count(child) for child in root.children), cnt)
        return cnt

    def pretty_print(self, file=sys.stdout):
        legend = [["label counter:", 0]]
        self._pretty_print(self.root, 0, legend, file=file)
        for label, tilings in legend:
            if isinstance(tilings, int):
                continue
            print(file=file)
            print("Label:", label, file=file)
            print(file=file)
            in_tiling, out_tiling = tilings
            print(in_tiling, file=file)
            if out_tiling:
                if out_tiling != in_tiling:
                    print("We use his sibling for the next strategy", file=file)
                    print(out_tiling, file=file)

    def _pretty_print(self, root, depth, legend, prefix="root: ", tail=False, file=sys.stdout):
        tp_L = ProofTree.__PRETTY_PRINT_DICT["L"]
        tp_pipe = ProofTree.__PRETTY_PRINT_DICT["pipe"]
        tp_tee = ProofTree.__PRETTY_PRINT_DICT["T"]
        tp_empty = ProofTree.__PRETTY_PRINT_DICT["empty"]
        label_counter = legend[0][1]
        print(prefix, label_counter, sep="", file=file)
        legend.append([label_counter, (root.in_tiling, root.out_tiling)])
        legend[0][1] += 1
        for subtree_number in range(len(root.children)-1):
            self._pretty_print(root.children[subtree_number],
                               depth+1,
                               legend,
                               prefix[:-6] + (tp_pipe if tail else tp_empty) + tp_tee,
                               True,
                               file)
        if len(root.children) > 1:
            self._pretty_print(root.children[-1],
                               depth+1,
                               legend,
                               prefix[:-6] + (tp_pipe if tail else tp_empty) + tp_L,
                               False,
                               file)

    def set_of_tilings(self, root=None, to_return=set()):
        if root is None:
            root = self.root
        next_return = set(to_return)
        next_return.add(root.in_tiling)
        next_return.add(root.out_tiling)
        for subtree_number in range(len(root.children)):
            next_return = next_return.union(self.set_of_tilings(root.children[subtree_number],
                               next_return))
        return next_return
