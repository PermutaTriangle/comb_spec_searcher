from collections import Counter
from unittest.mock import Mock

import pytest
import sympy

from comb_spec_searcher.equation_check import EquationChecker
from comb_spec_searcher.exception import SanityCheckFailure
from comb_spec_searcher.utils import sympy_expr_to_maple


def test_marker_substitution():
    x, a, b = sympy.symbols("x a b")
    f, g = map(sympy.Function, ("F_0", "F_1"))
    parent = Mock(extra_parameters=("a", "b"))
    child = Mock(extra_parameters=("a",))
    parent.get_terms.side_effect = lambda n: Counter({(n, n): 1})
    child.get_terms.side_effect = lambda n: Counter({(n,): 1})
    spec = Mock(rules_dict={parent: None, child: None})
    spec.get_function.side_effect = {parent: f(x, a, b), child: g(x, a)}.__getitem__
    checker = EquationChecker(spec, length=2)
    checker.check(sympy.Eq(f(x, a, b), g(x, a * b)))
    with pytest.raises(SanityCheckFailure, match="size 1"):
        checker.check(sympy.Eq(f(x, a, b), g(x, b)))
    assert child.get_terms.call_count == 3


def test_division_and_unknown_function():
    x = sympy.Symbol("x")
    f = sympy.Function("F_0")(x)
    cls = Mock(extra_parameters=())
    cls.get_terms.side_effect = lambda n: Counter({(): int(n >= 2)})
    spec = Mock(rules_dict={cls: None})
    spec.root.from_genf_name.return_value = None
    spec.get_function.return_value = f
    checker = EquationChecker(spec, length=3)
    checker.check(sympy.Eq(f / x**2, 1 / (1 - x)))
    with pytest.raises(SanityCheckFailure, match="size 3"):
        checker.check(sympy.Eq(f / x**2, 1 + x + x**2))
    with pytest.raises(NotImplementedError, match="NOTIMPLEMENTED"):
        checker.check(sympy.Eq(f, sympy.Function("NOTIMPLEMENTED")(x)))


def test_named_class():
    x, k = sympy.symbols("x k")
    f = sympy.Function("F_0")(x, k)
    g = sympy.Function("G")
    marked = Mock(extra_parameters=("k",))
    marked.get_terms.side_effect = lambda n: Counter({(n,): n + 1})
    ordinary = Mock(extra_parameters=())
    ordinary.get_terms.side_effect = lambda n: Counter({(): n + 1})
    marked.from_genf_name.return_value = ordinary
    spec = Mock(root=marked, rules_dict={marked: None})
    spec.get_function.return_value = f
    checker = EquationChecker(spec, length=3)
    checker.check(sympy.Eq(f, g(x * k)))
    with pytest.raises(SanityCheckFailure, match="size 1"):
        checker.check(sympy.Eq(f, g(x)))
    marked.from_genf_name.assert_called_once_with("G")


def test_named_function_maple_export():
    x, k = sympy.symbols("x k_0")
    f = sympy.Function("F_Av(1234,1324)")
    assert sympy_expr_to_maple(f(x)) == "F[Av(1234,1324), x]"
    assert sympy_expr_to_maple(f(x * k)) == "F[Av(1234,1324), x, k[0]]"


def test_pump_marked_system():
    x, k = sympy.symbols("x k")
    f, g = map(sympy.Function, ("F", "G"))
    root = Mock(extra_parameters=("k",))
    child = Mock(extra_parameters=("k",))
    spec = Mock(root=root, rules_dict={root: None, child: None})
    spec.get_function.side_effect = {root: f(x, k), child: g(x, k)}.__getitem__
    for cls in (root, child):
        cls.minimum_size_of_object.return_value = 0
        cls.possible_parameters.side_effect = lambda n: ({"k": i} for i in range(n + 1))
    counts = [1, 2, 8, 40]
    root.get_terms.side_effect = lambda n: Counter({(n,): counts[n]})
    equations = [
        sympy.Eq(f(x, k), g(k * x, 1)),
        sympy.Eq(g(x, k), (1 - sympy.sqrt(1 - 8 * k * x)) / (4 * k * x)),
    ]
    checker = EquationChecker(spec, length=3)
    checker.check_root(equations)
    child.get_terms.assert_not_called()
    with pytest.raises(SanityCheckFailure, match="size 1"):
        checker.check_root([sympy.Eq(f(x, k), g(x, 1)), equations[1]])


def test_pump_selects_algebraic_branch():
    x = sympy.Symbol("x")
    f = sympy.Function("F")(x)
    root = Mock(extra_parameters=())
    root.minimum_size_of_object.return_value = 0
    counts = [1, 1, 2, 5, 14]
    root.get_terms.side_effect = lambda n: Counter({(): counts[n]})
    spec = Mock(root=root, rules_dict={root: None})
    spec.get_function.return_value = f
    checker = EquationChecker(spec, length=4)
    checker.check_root([sympy.Eq(f**2 - f, x * f**3)])


def test_pump_undetermined_root():
    x = sympy.Symbol("x")
    f = sympy.Function("F")(x)
    root = Mock(extra_parameters=())
    root.minimum_size_of_object.return_value = 0
    spec = Mock(root=root, rules_dict={root: None})
    spec.get_function.return_value = f
    checker = EquationChecker(spec, length=2)
    checker.check(sympy.Eq(f, f))
    with pytest.raises(NotImplementedError, match="determine"):
        checker.check_root([sympy.Eq(f, f)])


def test_pump_named_class_and_shifted_equation():
    x = sympy.Symbol("x")
    f, h, named = (sympy.Function(name)(x) for name in ("F", "H", "Named"))
    root, child, known = (Mock(extra_parameters=()) for _ in range(3))
    root.minimum_size_of_object.return_value = 0
    child.minimum_size_of_object.return_value = 1
    root.from_genf_name.return_value = known
    root.get_terms.side_effect = known.get_terms.side_effect = lambda n: Counter(
        {(): n + 1}
    )
    spec = Mock(root=root, rules_dict={root: None, child: None})
    spec.get_function.side_effect = {root: f, child: h}.__getitem__
    checker = EquationChecker(spec, length=3)
    checker.check_root([sympy.Eq(h, x * f), sympy.Eq(h, x * named)])
    child.get_terms.assert_not_called()


def test_pump_allows_free_auxiliary_series():
    x = sympy.Symbol("x")
    f, g = (sympy.Function(name)(x) for name in ("F", "G"))
    root, child = (Mock(extra_parameters=()) for _ in range(2))
    for cls in (root, child):
        cls.minimum_size_of_object.return_value = 0
    root.get_terms.side_effect = lambda n: Counter({(): n + 1})
    spec = Mock(root=root, rules_dict={root: None, child: None})
    spec.get_function.side_effect = {root: f, child: g}.__getitem__
    checker = EquationChecker(spec, length=3)
    checker.check_root([sympy.Eq(f, 1 / (1 - x) ** 2), sympy.Eq(g, g)])
