from collections import Callable
from typing import List, Any

from laggard.rulebuilders import RuleBuilder


def multiple(rule: RuleBuilder, **kwargs):
    """
    Will attempt to parse the provided rule at least once.

    Args:
        rule: The :class:`~laggard.rulebuilders.RuleBuilder` to parse.
        **kwargs: Passed onto :class:`~laggard.rulebuilders.RuleBuilder`

    Returns:
        :class:`~laggard.functionalrulebuilders.MultipleRule`: The RuleBuilder that will parse appropriately.
    """
    return RuleBuilder.create(rule, multiple=True, **kwargs)

def optional(rule: RuleBuilder, **kwargs):
    """
    Generates a parser which will attempt to parse the provided rule, and return None if it fails.

    Args:
        rule: The :class:`~laggard.rulebuilders.RuleBuilder` to parse.
        **kwargs: Passed onto :class:`~laggard.rulebuilders.RuleBuilder`

    Returns:
        :class:`~laggard.functionalrulebuilders.OptionalRule`: The RuleBuilder that will parse appropriately.
    """
    return RuleBuilder.create(rule, optional=True, **kwargs)

def none_or_more(rule: RuleBuilder, **kwargs):
    """
    Generates a parser which will attempted to parse the provided rule 0 or more times, returning a List of all the parses it could do.

    Args:
        rule: The :class:`~laggard.rulebuilders.RuleBuilder` to parse.
        **kwargs: Passed onto :class:`~laggard.rulebuilders.RuleBuilder`

    Returns:
        :class:`~laggard.functionalrulebuilders.SomeOrNoneRule`: The RuleBuilder that will parse appropriately.
    """
    return RuleBuilder.create(rule, optional=True, multiple=True, **kwargs)

class RulePlaceholder:
    """
    When a rule cannot be resolved, because its subrule might not exist yet, this is put in its place.
    This is what a function decorated with :function:`~laggard.decorations.rule` become.
    It also has an inbuilt decorator to create rule interpreters(functions to produce ASTs etc.)

    It has all the magic methods implemented in :class:`~laggard.rulebuilders.RuleBuilder`, so you can treat it like a :class:`~laggard.rulebuilders.RuleBuilder` almost all the time.

    Examples:
        To specify a transformer for a rule::

            @rule
            def myrule():
                return myotherrule | mysecondrule

            @myrule.transformer
            def myruletransformer(result):
                # Do things here
                return result

    Warnings:
        This class **should not** be initialised directly. Instead, use :function:`~laggard.decorations.rule`
    """

    def __init__(self, rule_resolver: Callable, **kwargs):

        self.resolver = rule_resolver
        self._options = {
            "name": self.resolver.__qualname__,
        }
        self._options.update(kwargs)
        self._transformer = None

    def invoke(self, **kwargs):
        """
        Creates a :class:`~laggard.rulebuilders.RuleBuilder` by executing the provided function.

        Args:
            **kwargs: Passed onto :class:`~laggard.rulebuilders.RuleBuilder`

        Returns:
            :class:`~laggard.rulebuilders.RuleBuilder`: The RuleBuilder described in the function.

        """
        return RuleBuilder.create(self.resolver(), **dict(self._options, **kwargs))

    def transformer(self, f):
        """
        Use this as a decorator for a function which takes the raw parse result, and returns the new, transformed result.

        Args:
            f: The decorated function of signature (Any) -> Any

        Returns:
            f
        """
        self._options["transformer"] = f
        return f

    def __or__(self, other):
        return self.invoke() | other
    def __ror__(self, other):
        return other | self.invoke()
    def __and__(self, other):
        return self.invoke() & other
    def __rand__(self, other):
        return other & self.invoke()

    def __call__(self, *args, **kwargs):
        return self.invoke()(*args, **kwargs)


class OptionallyNamedTuple:
    """
    Acts like both a tuple, and a dictionary, depending on the type of the keys.
    The return type of a :class:`~laggard.rulebuilders.Combined` parser.

    """

    def __init__(self, names: List[str], results: List[Any]):
        """

        Args:
            names: A list of the keys, for the dictionary component. An item can be None if that position does not have a name.
            results: The list/tuple of actual data. The length must be equal to the length of `names`.
        """
        if len(names) != len(results):
            raise ValueError("The number of names and items must be equal.")
        self._results = results
        self._mappings = {}
        for i, name in enumerate(names):
            if name is not None:
                self._mappings[name] = i

    @classmethod
    def create(cls, names):
        def f(results: List[Any]):
            return cls(names, results)

        return f

    def __len__(self):
        return len(self._results)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._results[self._mappings[item]]
        else:
            return self._results[item]

    def __iter__(self):
        return iter(self._results)
