"""Check a generating-function equation against independently enumerated terms."""

from typing import TYPE_CHECKING

import sympy
from sympy.core.function import AppliedUndef

from .exception import SanityCheckFailure

if TYPE_CHECKING:
    from .specification import CombinatorialSpecification


class EquationChecker:
    """Reuse class terms while checking the equations of one specification."""

    def __init__(self, spec: "CombinatorialSpecification", length: int = 5):
        if length < 0:
            raise ValueError("length must be nonnegative")
        self.length = length
        self.x = sympy.Symbol("x")
        self.root = spec.root
        functions = {spec.get_function(cls): cls for cls in spec.rules_dict}
        self.classes = {function.func: cls for function, cls in functions.items()}
        self.symbols = {self.x}.union(*(f.free_symbols for f in functions))
        self.terms: dict = {}
        self.series: dict = {}

    def _expand_call(self, call, degree):
        key = (call, degree)
        if key in self.series:
            return self.series[key]
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
        poly = value.as_poly(self.x)
        if poly is None:
            series = value.series(self.x, 0, degree + 1)
            poly = series.removeO().as_poly(self.x)
        if poly is None or poly.as_expr().has(
            sympy.nan, sympy.zoo, sympy.oo, -sympy.oo
        ):
            raise NotImplementedError(f"No ordinary series for {expr}")
        return poly

    def check(self, equation) -> None:
        """Raise SanityCheckFailure on mismatch, NotImplementedError if unchecked."""
        if equation == sympy.true:
            return
        if equation == sympy.false:
            raise SanityCheckFailure("The equation simplifies to False")
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
