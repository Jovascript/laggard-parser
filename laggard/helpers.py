from collections import Callable
from typing import List, Any

from laggard.rulebuilders import RuleBuilder


def multiple(rule: RuleBuilder, **kwargs):
    return RuleBuilder.create(rule, multiple=True, **kwargs)

def optional(rule: RuleBuilder, **kwargs):
    return RuleBuilder.create(rule, optional=True, **kwargs)

def none_or_more(rule: RuleBuilder, **kwargs):
    return RuleBuilder.create(rule, optional=True, multiple=True, **kwargs)

class RulePlaceholder:
    """When a rule cannot be resolved, becuase its subrule might not exist yet, this is put in its place.
    It also has an inbuilt decorator to create rule interpreters(functions to produce ASTs etc.)"""

    def __init__(self, rule_resolver: Callable, **kwargs):
        self.resolver = rule_resolver
        self._options = {
            "name": self.resolver.__qualname__,
        }
        self._options.update(kwargs)
        self._transformer = None

    def invoke(self, **kwargs):
        return RuleBuilder.create(self.resolver(), **dict(self._options, **kwargs))

    def transformer(self, f):
        self._options["transformer"] = f

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
    """Acts like a dictionary and a list(tuple) to allow reference to labelled and unlabelled items"""

    def __init__(self, names: List[str], results: List[Any]):
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
        return self._results
