from sympy import diff, symbols, sympify, Function
from sympy.abc import x
from grids import Tiling, Block, PositiveClass, lex_min, Cell
from permuta import Av
from functools import reduce
from operator import mul
from math import factorial

from pymongo import MongoClient
mongo = MongoClient('mongodb://webapp:c73f12a3@permpal.ru.is:27017/permsdb')

__all__ = ("get_tiling_genf", "genf_from_db", "factor_from_db", "permeval", "taylor_expand")


def get_tiling_genf(tiling, identifier, inp_set, root_func, substitutions, fcache):
    factorEqs = []
    for factor in tiling.find_factors():
        eq = None
        for k, v in factor.factor.items():
            if v == Block.point_or_empty:
                with_point = {kk: vv for kk, vv in factor.factor.items()}
                with_point[k] = Block.point
                with_point = Tiling(with_point)
                empty = Tiling({kk: vv for kk, vv in factor.factor.items() if kk != k})
                eq = (get_tiling_genf(with_point, identifier, inp_set, root_func, substitutions, fcache)
                      + get_tiling_genf(empty, identifier, inp_set, root_func, substitutions, fcache))
                factorEqs.append(eq)
                break
            if v is not Block.point and isinstance(v, PositiveClass):
                non_positive = {kk: vv for kk, vv in factor.factor.items()}
                non_positive[k] = v.perm_class
                non_positive = Tiling(non_positive)
                empty = Tiling({kk: vv for kk, vv in factor.factor.items() if kk != k})
                eq = (get_tiling_genf(non_positive, identifier, inp_set, root_func, substitutions, fcache)
                      - get_tiling_genf(empty, identifier, inp_set, root_func, substitutions, fcache))
                factorEqs.append(eq)
                break
        else:
            minfac = factor.minimum()
            facstr = str(minfac)
            if facstr in fcache:
                factorEqs.append(fcache[facstr])
                continue
            eq = factor_from_db(factor)
            new_symbol = symbols('C_'+str(len(substitutions)))
            fcache[facstr] = new_symbol
            factorEqs.append(new_symbol)
            if eq:
                substitutions[new_symbol] = eq
                continue
            func = 0
            sets = 0
            xs, ys = set(),set()
            for k, v in factor.factor.items():
                xs.add(k[0])
                ys.add(k[1])
                if len(factor) == 1:
                    if v == inp_set:
                        factorEqs[-1] = root_func
                        del fcache[facstr]
                        break
                    if v is Block.point:
                        continue
                    ext_genf = genf_from_db(v)
                    if ext_genf is None:
                        raise RuntimeError("Cannot find generating function for " + str(identifier)
                                           + " because generating function for " + repr(v) + " is unknown")
                    substitutions[new_symbol] = ext_genf
                    break
                if v is not Block.point:
                    ext_genf = genf_from_db(v)
                    if ext_genf is None:
                        raise RuntimeError("Cannot find generating function for " + str(identifier)
                                           + " because generating function for " + repr(v) + " is unknown")
                    func = ext_genf
                    sets += 1
            else:
                if sets > 1 or (len(xs) > 1 and len(ys) > 1):
                    raise RuntimeError("Unknown factor found \n" + str(factor)
                                       + "\nThe minimum of the factor is \n" + str(factor.minimum()))
                if func:
                    points = len(factor.factor)-1
                    eq = x*diff(x*(func), x)
                    for _ in range(points-1):
                        eq = x*diff(x*eq, x)
                    substitutions[new_symbol] = eq.doit()
                else:
                    points = len(factor.factor)
                    substitutions[new_symbol] = factorial(points)*x**points
    return reduce(mul, factorEqs, 1)


def genf_from_db(inputset):
    permset = Av(lex_min(list(inputset.basis)))
    basis = '_'.join([''.join([str(i+1) for i in perm]) for perm in permset.basis])
    result = mongo.permsdb.av.find_one({'basis': basis})
    if not result or 'atrap_data' not in result or 'sympy_genf' not in result['atrap_data']:
        return None
    res = result['atrap_data']['sympy_genf']
    #for c in "BCDEFGH":
    #    if c in res:
    #        return None
    return sympify(res)


def factor_from_db(factor):
    key = factor.minimum()
    result = mongo.permsdb.factor.find_one({'factor': str(key)})
    if not result:
        # TODO: Add in those needed for database verification.
        return None
    return sympify(result['genf'])


def taylor_expand(gen_func, terms=10):
    num,den = gen_func.as_numer_denom()
    num = num.expand()
    den = den.expand()
    gen_func = num/den
    expansion = gen_func.series(n=None)
    return [next(expansion)/(x**i) for i in range(terms+1)]

def permeval(text):
    if text.startswith("Av+"):
        return PositiveClass(eval("Av([" + text[4:-1]+"])"))
    elif text.startswith("Av"):
        return eval("Av([" + text[3:-1]+"])")
    else:
        return Block.point
