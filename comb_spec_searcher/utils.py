"""Some useful miscellaneous functions used througout the package."""
import logging
import os
import re
import sys
import time
from typing import TYPE_CHECKING, Any, Callable, TypeVar, cast

import psutil
import sympy

from comb_spec_searcher.exception import TaylorExpansionError

if TYPE_CHECKING:
    from comb_spec_searcher import CombinatorialSpecificationSearcher


Func = TypeVar("Func", bound=Callable[..., Any])


class cssmethodtimer:
    """This is a decorator for counting and timing function calls."""

    def __init__(self, explanation: str):
        self.explanation = explanation

    def __call__(self, func: Func) -> Func:
        def inner(css: "CombinatorialSpecificationSearcher", *args, **kwargs):
            start = time.time()
            res = func(css, *args, **kwargs)
            css.func_times[self.explanation] += time.time() - start
            css.func_calls[self.explanation] += 1
            return res

        return cast(Func, inner)


class cssiteratortimer:
    """This is a decorator for counting and timing function calls."""

    def __init__(self, explanation: str):
        self.explanation = explanation

    def __call__(self, func: Func) -> Func:
        def inner(css: "CombinatorialSpecificationSearcher", *args, **kwargs):
            key = self.explanation
            if self.explanation == "_expand_class_with_strategy":
                key = str(args[1])
            css.func_calls[key] += 1
            start = time.time()
            for res in func(css, *args, **kwargs):
                css.func_times[key] += time.time() - start
                yield res
                start = time.time()
            css.func_times[key] += time.time() - start

        return cast(Func, inner)


class RecursionLimit:
    """
    A context manager to momentarily increase the recursion limit.
    """

    def __init__(self, limit: int):
        self.curr_limit = sys.getrecursionlimit()
        if self.curr_limit < limit:
            self.limit = limit
        else:
            self.limit = self.curr_limit

    def __enter__(self) -> None:
        sys.setrecursionlimit(self.limit)

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        sys.setrecursionlimit(self.curr_limit)


class DisableLogging:
    """
    Disable all logging calls of severity level and below
    """

    def __init__(self, level: int):
        self.level = level

    def __enter__(self) -> None:
        logging.disable(self.level)

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        logging.disable(logging.NOTSET)


def check_poly(min_poly, initial, root_initial=None, root_func=None):
    """Return True if this is a minimum polynomial for the generating
    function F with the given initial terms. Input is a polynomial in F,
    and initial terms."""
    F = sympy.Symbol("F")
    x = sympy.var("x")
    init_poly = 0
    for i, coeff in enumerate(initial):
        init_poly += coeff * x ** i
    if root_initial is not None:
        root_poly = 0
        for i, coeff in enumerate(root_initial):
            root_poly += coeff * x ** i
    verification = min_poly.subs({F: init_poly})
    if root_initial is not None:
        verification = verification.subs({root_func: root_poly})
    verification = verification.expand()
    verification = verification.series(x, n=len(initial)).removeO()
    verification = (verification + sympy.O(x ** (len(initial) - 1))).removeO()
    return verification == 0


def check_equation(equation, initial, root_initial=None, root_func=None):
    """Return True if an equation in terms of the generating function F and x
    is satisfied."""
    F = sympy.Symbol("F")
    solutions = sympy.solve(
        equation, F, dict=True, cubics=False, quartics=False, quintics=False
    )
    for solution in solutions:
        genf = solution[F]
        try:
            expansion = taylor_expand(genf, len(initial) - 1)
        except TaylorExpansionError:
            continue
        if initial == expansion:
            return True
    return False


def get_solution(equation, initial):
    """Return solution of equation in F and x with the given initial
    conditions."""
    F = sympy.Symbol("F")
    solutions = sympy.solve(
        equation, F, dict=True, cubics=False, quartics=False, quintics=False
    )
    for solution in solutions:
        genf = solution[F]
        try:
            expansion = taylor_expand(genf, len(initial) - 1)
        except TaylorExpansionError:
            continue
        if initial == expansion:
            return genf


def taylor_expand(genf, n: int = 10):
    x = sympy.var("x")
    try:
        num, den = genf.as_numer_denom()
        num = num.expand()
        den = den.expand()
        genf = num / den
        ser = sympy.Poly(genf.series(n=n + 1).removeO(), x)
        res = ser.all_coeffs()
        res = res[::-1] + [0] * (n + 1 - len(res))
    except Exception:
        raise TaylorExpansionError
    return res


def pretty_print_equations(root_func, count, eqs) -> str:
    s = "The system of {} equations\n".format(len(eqs))
    s += "root_func := {}:\n".format(str(root_func))
    s += "eqs := [\n"
    s += ",\n".join("{} = {}".format(str(eq.lhs), str(eq.rhs)) for eq in eqs)
    s += "\n]:\n"
    s += "count := {}:".format(list(count))
    if all(len(eq.lhs.args) == 1 for eq in eqs):
        s = s.replace("(x)", "")
    return s


def maple_equations(root_func, count, eqs) -> str:
    """
    Convert a systems of equations to version that can be copy pasted to maple.
    """
    s = f"root_func := {sympy_expr_to_maple(root_func)}:\n"
    s += "eqs := [\n"
    s += ",\n".join(map(sympy_expr_to_maple, eqs))
    s += "\n]:\n"
    s += "count := {}:".format(list(count))
    return s


def sympy_expr_to_maple(expr):
    """
    Convert a sympy expression to a maple string.
    """
    if isinstance(expr, sympy.Eq):
        return f"{sympy_expr_to_maple(expr.lhs)} = {sympy_expr_to_maple(expr.rhs)}"
    if isinstance(expr, sympy.core.add.Add):
        head, tail = expr.as_two_terms()
        return f"({sympy_expr_to_maple(head)} + {sympy_expr_to_maple(tail)})"
    if isinstance(expr, sympy.core.add.Mul):
        head, tail = expr.as_two_terms()
        return f"({sympy_expr_to_maple(head)} * {sympy_expr_to_maple(tail)})"
    if isinstance(expr, sympy.core.power.Pow):
        base, exp = expr.as_base_exp()
        return f"({sympy_expr_to_maple(base)}**{sympy_expr_to_maple(exp)})"
    if isinstance(expr.__class__, sympy.core.function.UndefinedFunction):
        if "NOTIMPLEMENTED" in str(expr):
            return "NOTIMPLEMENTED"
        split = re.compile(r"F_([0-9]+)\((.*)\)")
        assert split.match(repr(expr)) is not None, expr
        label = split.match(repr(expr)).group(1)
        args = map(sympy.sympify, split.match(repr(expr)).group(2).split(", "))
        content = f"{label}, " + ", ".join(map(sympy_expr_to_maple, args))
        return f"F[{content}]"
    if isinstance(expr, sympy.core.symbol.Symbol):
        symb = str(expr)
        if "_" in symb:
            var, label = symb.split("_")
            return f"{var}[{label}]"
        return symb
    if expr.is_number:
        return f"({expr})"
    raise NotImplementedError(str(expr))


def compositions(n, k):
    # Credit to:
    # https://pythonhosted.org/combalg-py/_modules/combalg/combalg.html
    """
    Iterator over all the composition of n into k parts.

    Composition of are tuple of k integers that are greater of equals to 0 such
    that the sum of the k integers is n.

    >>> sorted(compositions(2,3))
    [(0, 0, 2), (0, 1, 1), (0, 2, 0), (1, 0, 1), (1, 1, 0), (2, 0, 0)]
    >>> sorted(compositions(2,2))
    [(0, 2), (1, 1), (2, 0)]
    >>> list(compositions(2, 1))
    [(2,)]
    >>> list(compositions(0, 1))
    [(0,)]
    >>> list(compositions(-1, 1))
    []
    >>> list(compositions(1, -1))
    []
    >>> list(compositions(1, -1))
    []
    """
    if n < 0 or k < 0 or k == 0:
        return
    t = n
    h = 0
    a = [0] * k
    a[0] = n
    yield tuple(a)
    while a[k - 1] != n:
        if t != 1:
            h = 0
        t = a[h]
        a[h] = 0
        a[0] = t - 1
        a[h + 1] += 1
        h += 1
        yield tuple(a)


def nice_pypy_mem(mem: str) -> str:
    """Improves formatting of the memory statistics produced by pypy's
    garbage collector (which are provided as strings)"""
    return mem.replace("KB", " KiB").replace("MB", " MiB").replace("GB", " GiB")


def get_mem() -> int:
    """Return memory used by CombSpecSearcher - note this is actually the
    memory usage of the process that the instance of CombSpecSearcher was
    invoked."""
    return int(psutil.Process(os.getpid()).memory_info().rss)


def size_to_readable(size: int) -> str:
    """Convert a size in bytes to a human readable value in KiB, MiB, or
    GiB"""
    if size / 1024 ** 2 < 1:
        return str(round(size / 1024)) + " KiB"
    if size / 1024 ** 3 < 1:
        return str(round(size / 1024 ** 2, 1)) + " MiB"
    return str(round(size / 1024 ** 3, 3)) + " GiB"


def time_to_readable(seconds: int) -> str:
    """Convert a time in seconds to a human readable time in seconds / minutes /
    hours"""
    if seconds < 60:
        return "{} seconds".format(round(seconds))
    if seconds < 3600:
        return "{} minutes".format(round(seconds / 60, 1))
    return "{} hours".format(round(seconds / 60 / 60, 2))
