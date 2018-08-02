import inspect
from functools import update_wrapper, wraps

from laggard.helpers import RulePlaceholder
from laggard.rulebuilders import RuleBuilder


def performs_match(f):
    return update_wrapper(RuleBuilder.create(f, name=f.__qualname__, ), f)

def rule(f):
    sig = inspect.signature(f)
    if len(sig.parameters) == 0:
        return RulePlaceholder(f)
    else:
        return performs_match(f)


