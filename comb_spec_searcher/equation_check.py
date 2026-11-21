"""Check a generating-function equation against independently enumerated terms."""

from typing import TYPE_CHECKING

import sympy
from sympy.core.function import AppliedUndef
from sympy.solvers.solveset import NonlinearError

from .exception import SanityCheckFailure

if TYPE_CHECKING:
    from .specification import CombinatorialSpecification


class EquationChecker:
    """Check individual equations and recover the root series of a specification."""

    def __init__(self, spec: "CombinatorialSpecification", length: int = 5):
        if length < 0:
            raise ValueError("length must be nonnegative")
        self.length = length
        self.x = sympy.Symbol("x")
        self.root = spec.root
        self.functions = {spec.get_function(cls): cls for cls in spec.rules_dict}
        self.classes = {f.func: cls for f, cls in self.functions.items()}
        self.symbols = {self.x}.union(*(f.free_symbols for f in self.functions))
        self.terms: dict = {}
        self.series: dict = {}

    def _class_for_call(self, call):
        cls = self.classes.get(call.func)
        if cls is None:
            cls = self.root.from_genf_name(call.func.__name__)
            if cls is None:
                raise NotImplementedError(f"No class terms for {call.func}")
            self.classes[call.func] = cls
        size, *markers = call.args
        if len(markers) != len(cls.extra_parameters):
            raise ValueError(f"Wrong number of parameters in {call}")
        if not size.is_polynomial(self.x) or size.subs(self.x, 0) != 0:
            raise NotImplementedError(f"Unsupported size argument in {call}")
        if any(not mark.is_polynomial(self.x) for mark in markers):
            raise NotImplementedError(f"Unsupported marker argument in {call}")
        for marker, parameter in zip(markers, cls.extra_parameters):
            if marker.has(self.x) and cls.get_minimum_value(parameter) < 0:
                raise NotImplementedError(f"Negative powers of a size marker in {call}")
        return cls

    def _expand_call(self, call, degree):
        key = (call, degree)
        if key in self.series:
            return self.series[key]
        cls = self._class_for_call(call)
        size, *markers = call.args
        total = sympy.S.Zero
        for n in range(degree + 1):
            if (cls, n) not in self.terms:
                self.terms[cls, n] = cls.get_terms(n)
            for powers, count in self.terms[cls, n].items():
                total += (
                    count
                    * size**n
                    * sympy.prod(m**k for m, k in zip(markers, powers, strict=True))
                )
        self.series[key] = total
        return total

    def _polynomial(self, expr, degree):
        calls = expr.atoms(AppliedUndef)
        substitutions = {call: self._expand_call(call, degree) for call in calls}
        value = expr.xreplace(substitutions)
        poly = value.as_poly(self.x, domain="EX")
        if poly is None:
            series = value.series(self.x, 0, degree + 1)
            poly = series.removeO().as_poly(self.x, domain="EX")
        if poly is None or poly.as_expr().has(
            sympy.nan, sympy.zoo, sympy.oo, -sympy.oo
        ):
            raise NotImplementedError(f"No ordinary series for {value}")
        return poly

    def check(self, equation) -> None:
        """Raise SanityCheckFailure on mismatch, NotImplementedError if unchecked."""
        if equation == sympy.true:
            return
        if equation == sympy.false:
            raise SanityCheckFailure("The equation simplifies to False")
        numerator, denominator = self._fraction(equation)

        divisor = self._polynomial(denominator, self.length)
        if divisor.is_zero:
            raise NotImplementedError(f"Unresolved denominator in {equation}")
        (valuation,), leading = divisor.terms()[-1]
        if valuation > self.length and denominator.has(AppliedUndef):
            raise NotImplementedError(f"Unresolved denominator in {equation}")
        # Division by x**valuation consumes that many terms of the numerator.
        degree = self.length + valuation
        poly = self._polynomial(numerator, degree)
        for n in range(degree + 1):
            difference = poly.nth(n)
            if difference != 0 and sympy.simplify(difference) != 0:
                raise SanityCheckFailure(
                    f"Equation {equation} differs at size {n - valuation}: "
                    f"lhs - rhs = {difference / leading}"
                )

    def _fraction(self, equation):
        expr = equation.lhs - equation.rhs
        unknown = expr.free_symbols - self.symbols
        if unknown:
            raise NotImplementedError(f"Unknown symbols: {unknown}")
        calls = expr.atoms(AppliedUndef)
        numerator, denominator = expr, sympy.S.One
        if not expr.is_polynomial(self.x, *calls):
            numerator, denominator = sympy.together(expr).as_numer_denom()
            for part in (numerator, denominator):
                if calls and not part.is_polynomial(*calls):
                    raise NotImplementedError(f"Nonpolynomial function calls in {part}")
                # The function coefficients must be regular at the origin.
                coefficients = part.as_poly(*calls).coeffs() if calls else [part]
                if any(c.subs(self.x, 0).is_finite is False for c in coefficients):
                    raise NotImplementedError(f"Singular coefficient in {part}")

        return numerator, denominator

    @staticmethod
    def _unknown_coefficient(comb_class, n, unknowns):
        terms = []
        choices = (
            comb_class.possible_parameters(n) if comb_class.extra_parameters else [{}]
        )
        for parameters in choices:
            variable = sympy.Dummy()
            powers = tuple(parameters[k] for k in comb_class.extra_parameters)
            unknowns[variable] = (comb_class, n, powers)
            terms.append(
                variable
                * sympy.prod(sympy.Symbol(k) ** v for k, v in parameters.items())
            )
        return sympy.Add(*terms)

    def _coefficient_equations(self, expr, substitutions, markers, degree):
        residual = expr.xreplace(substitutions).expand()
        order = residual.getO()
        if order is not None:
            degree = int(order.getn()) - 1
        if degree < 0:
            return
        poly = self._polynomial(residual.removeO(), degree)
        for (n,), coefficient in poly.terms():
            if n > degree or coefficient == 0:
                continue
            if not markers:
                yield coefficient
                continue
            poly_in_markers = coefficient.as_poly(*markers, domain="EX")
            if poly_in_markers is None:
                numerator, _ = sympy.together(coefficient).as_numer_denom()
                poly_in_markers = numerator.as_poly(*markers, domain="EX")
            if poly_in_markers is None:
                raise NotImplementedError(
                    f"Nonpolynomial marker coefficient: {coefficient}"
                )
            yield from poly_in_markers.coeffs()

    def check_root(self, equations) -> None:
        """Recover the root series and compare its coefficients, including markers.

        Named classes supply external terms. A size-zero count may select the
        branch of an algebraic equation.
        """
        root = next(f for f, cls in self.functions.items() if cls == self.root)
        residuals = []
        for eq in equations:
            if eq == sympy.false:
                raise SanityCheckFailure("The equation simplifies to False")
            if eq != sympy.true:
                numerator, _ = self._fraction(eq)
                residuals.append(numerator)
        prefix, unknowns = self._pump(root, residuals)
        actual = prefix.as_poly(self.x)
        for n in range(self.length + 1):
            if actual.nth(n).free_symbols.intersection(unknowns):
                raise NotImplementedError(
                    f"Equations do not determine the root at size {n}"
                )
        expected = self._expand_call(root, self.length).as_poly(self.x)
        for n in range(self.length + 1):
            if sympy.simplify(actual.nth(n) - expected.nth(n)) != 0:
                raise SanityCheckFailure(
                    f"Pumped root differs at size {n}: equations give {actual.nth(n)}, "
                    f"enumeration gives {expected.nth(n)}"
                )

    def _pump(self, root, residuals):
        functions = {f.func: f for f in self.functions}
        internal = {}
        for call in {call for expr in residuals for call in expr.atoms(AppliedUndef)}:
            self._class_for_call(call)
            if call.func in functions:
                internal[call] = functions[call.func]
        markers = sorted(self.symbols - {self.x}, key=str)
        prefix = dict.fromkeys(self.functions, sympy.S.Zero)
        minimum = {}
        for f, cls in self.functions.items():
            try:
                minimum[f] = cls.minimum_size_of_object()
            except NotImplementedError:
                minimum[f] = 0
        max_minimum = max(minimum.values())

        # Classes can start in different degrees, as in H(x) = x * G(x).
        unknowns: dict = {}
        for step in range(max(0, self.length - minimum[root]) + 1):
            degree = {f: m + step for f, m in minimum.items()}
            trial = {
                f: prefix[f]
                + self._unknown_coefficient(cls, degree[f], unknowns)
                * self.x ** degree[f]
                for f, cls in self.functions.items()
            }
            # Keep the unknown tail when a substitution or product shifts the size.
            substitutions = {
                call: trial[f].xreplace(dict(zip(f.args, call.args, strict=True)))
                + sympy.O(call.args[0] ** (degree[f] + 1), self.x)
                for call, f in internal.items()
            }
            constraints = [
                coefficient
                for expr in residuals
                for coefficient in self._coefficient_equations(
                    expr, substitutions, markers, max_minimum + step
                )
            ]
            values = self._solve_coefficients(constraints, unknowns)
            prefix = {f: series.xreplace(values) for f, series in trial.items()}
            unknowns = {u: term for u, term in unknowns.items() if u not in values}
        return prefix[root], unknowns

    def _solve_coefficients(self, constraints, unknowns):
        """Solve linear constraints, then substitute their solutions into products."""
        result: dict = {}
        while constraints:
            linear, nonlinear = [], []
            for c in constraints:
                local = c.free_symbols & unknowns.keys()
                if not local:
                    if c != 0 and sympy.simplify(c) != 0:
                        raise SanityCheckFailure("Inconsistent equation coefficients")
                else:
                    try:
                        sympy.linear_eq_to_matrix([c], list(local))
                    except NonlinearError:
                        nonlinear.append(c)
                    else:
                        linear.append(c)

            values = {}
            if linear:
                variables = sorted(
                    set.union(*(c.free_symbols for c in linear)) & unknowns.keys(),
                    key=sympy.default_sort_key,
                )
                solutions = sympy.linsolve(linear, variables)
                if solutions is sympy.EmptySet:
                    raise SanityCheckFailure("Inconsistent equation coefficients")
                (solution,) = solutions
                values = {
                    u: v for u, v in zip(variables, solution, strict=True) if u != v
                }
            if nonlinear and not values:
                # Only size-zero enumeration may select an algebraic branch.
                for u in (
                    set.union(*(c.free_symbols for c in nonlinear)) & unknowns.keys()
                ):
                    cls, n, powers = unknowns[u]
                    if n == 0:
                        if (cls, n) not in self.terms:
                            self.terms[cls, n] = cls.get_terms(n)
                        values[u] = sympy.Integer(self.terms[cls, n].get(powers, 0))
                if not values:
                    raise NotImplementedError("Unresolved nonlinear coefficient system")
            result = {u: v.xreplace(values) for u, v in result.items()}
            result.update(values)
            constraints = [c.xreplace(values) for c in nonlinear]
        return result
