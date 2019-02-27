from functools import partial
from logzero import logger

import sympy


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
        except:
            if warn:
                logger.warn(("No function named " + func_name +
                            " in module " + module_name),
                            extra=logger_kwargs)
    except Exception as e:
        if warn:
            logger.warn("No module named " + module_name,
                        extra=logger_kwargs)


def check_poly(min_poly, initial):
    """Return True if this is a minimum polynomial for the generating
    function F with the given initial terms. Input is a polynomial in F,
    and initial terms."""
    F = sympy.Symbol("F")
    x = sympy.abc.x
    init_poly = 0
    for i, coeff in enumerate(initial):
        init_poly += coeff * x**i
    verification = min_poly.subs({F: init_poly}).expand()
    verification = (verification +
                    sympy.O(sympy.abc.x**(len(initial) - 1))).removeO()
    return verification == 0


def check_equation(equation, initial):
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