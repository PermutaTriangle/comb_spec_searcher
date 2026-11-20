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
