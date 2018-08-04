from typing import Callable
from functools import update_wrapper, wraps

from laggard.helpers import RulePlaceholder
from laggard.rulebuilders import RuleBuilder


def performs_match(f: Callable) -> RuleBuilder:
    """
    Decorates a function which takes the buffer directly, and performs a custom parsing.

    Args:
        f: A function which takes a single argument of type :class:`~laggard.buffer.Buffer` and returns the parse's result(any object).

    Returns:
        A :class:`~laggard.rulebuilders.RuleBuilder` which can be used in other rules.

    """
    return update_wrapper(RuleBuilder.create(f, name=f.__qualname__, ), f)


def rule(f: Callable) -> RulePlaceholder:
    """
    Decorates functions which return Rule compositions, allowing delayed execution so that all rules are in scope.

    Examples:
        To define a rule which parses any number of the letter 'a'::

            @rule
            def lots_of_a():
                return multiple("a")

    Args:
        f: The callable to decorate, should return :class:`~laggard.rulebuilders.RuleBuilder`

    Returns:
        A :class:`~laggard.helpers.RulePlaceholder`, which will become a :class:`~laggard.rulebuilders.RuleBuilder` when invoked.

    """
    return RulePlaceholder(f)

