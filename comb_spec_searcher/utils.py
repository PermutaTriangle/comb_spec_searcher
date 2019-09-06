from functools import partial

import sympy
from logzero import logger


def get_func_name(f, warn=False,
                  logger_kwargs={'processname': 'utils'}):
    """Return a string that is the name of the function f."""
    if not callable(f):
        raise TypeError("Function given is not callable.")
    if isinstance(f, partial):
        f = f.func
        if warn:
            logger.warn(("forgetting kwargs given to partial function "
                         "using strategy" + f.__name__),
                        extra=logger_kwargs)
    return f.__name__


def get_module_and_func_names(f, warn=False,
                              logger_kwargs={'processname': 'utils'}):
    """Return the module and name of a function f."""
    if isinstance(f, partial):
        f = f.func
        if warn:
            logger.warn(("forgetting kwargs given to partial function "
                         "using strategy" + f.__name__),
                        extra=logger_kwargs)
    return (f.__module__, f.__name__)


def get_func(module_name, func_name, warn=False,
             logger_kwargs={'processname': 'utils'}):
    """Return the function with given module and function names."""
    import importlib
    try:
        module = importlib.import_module(module_name)
        try:
            func = getattr(module, func_name)
            assert callable(func)
            return func
        except Exception:
            if warn:
                logger.warn(("No function named " + func_name +
                            " in module " + module_name),
                            extra=logger_kwargs)
    except Exception as e:
        if warn:
            logger.warn("No module named " + module_name,
                        extra=logger_kwargs)


def check_poly(min_poly, initial, root_initial=None, root_func=None):
    """Return True if this is a minimum polynomial for the generating
    function F with the given initial terms. Input is a polynomial in F,
    and initial terms."""
    F = sympy.Symbol("F")
    x = sympy.abc.x
    init_poly = 0
    for i, coeff in enumerate(initial):
        init_poly += coeff * x**i
    if root_initial is not None:
        root_poly = 0
        for i, coeff in enumerate(root_initial):
            root_poly += coeff * x**i
    verification = min_poly.subs({F: init_poly})
    if root_initial is not None:
        verification = verification.subs({root_func: root_poly})
    verification = verification.expand()
    verification = verification.series(x, n=len(initial)).removeO()
    verification = (verification +
                    sympy.O(sympy.abc.x**(len(initial) - 1))).removeO()
    return verification == 0


def check_equation(equation, initial, root_initial=None, root_func=None):
    """Return True if an equation in terms of the generating function F and x
    is satisfied."""
    F = sympy.Symbol("F")
    solutions = sympy.solve(equation, F, dict=True,
                            cubics=False, quartics=False, quintics=False)
    for solution in solutions:
        genf = solution[F]
        try:
            expansion = taylor_expand(genf, len(initial) - 1)
        except Exception:
            continue
        if initial == expansion:
            return True
    return False


def get_solution(equation, initial):
    """Return solution of equation in F and x with the given initial
    conditions."""
    F = sympy.Symbol("F")
    solutions = sympy.solve(equation, F, dict=True,
                            cubics=False, quartics=False, quintics=False)
    for solution in solutions:
        genf = solution[F]
        try:
            expansion = taylor_expand(genf, len(initial) - 1)
        except Exception as e:
            continue
        if initial == expansion:
            return genf


def taylor_expand(genf, n=10):
    num, den = genf.as_numer_denom()
    num = num.expand()
    den = den.expand()
    genf = num/den
    ser = sympy.Poly(genf.series(n=n+1).removeO(), sympy.abc.x)
    res = ser.all_coeffs()
    res = res[::-1] + [0]*(n+1-len(res))
    return res


def maple_equations(root_func, root_class, eqs):
    s = "The system of {} equations\n".format(len(eqs))
    s += "root_func := {}:\n".format(str(root_func)).replace("(x)", "")
    s += "eqs := [\n"
    s += ",\n".join("{} = {}".format(str(eq.lhs), str(eq.rhs))
                    for eq in eqs).replace("(x)", "")
    s += "\n]:\n"
    s += "count := {}:".format([len(list(root_class.objects_of_length(i)))
                                for i in range(6)])
    return s


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
    a = [0]*k
    a[0] = n
    yield tuple(a)
    while a[k-1] != n:
        if t != 1:
            h = 0
        t = a[h]
        a[h] = 0
        a[0] = t-1
        a[h+1] += 1
        h += 1
        yield tuple(a)
