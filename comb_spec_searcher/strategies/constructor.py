from sympy import Eq, Function
from typing import Any, Callable, Tuple
import abc


class Constructor(abc.ABC):
    """The constructor is akin to the 'counting function' in the comb exp paper."""

    @abc.abstractmethod
    def get_equation(self, lhs_func: Function, rhs_funcs: Tuple[Function, ...]) -> Eq:
        pass

    @abc.abstractmethod
    def get_recurrence(
        self,
        subrecs: Callable[[Any], int],
        get_subrule: Callable,
        **lhs_parameters: Any
    ) -> int:
        """The 'get_subrule' method should be passed to each recurrence as the first argument."""
        pass
