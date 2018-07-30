from typing import Union, Callable

from laggard.buffer import Buffer
from laggard.exceptions import MalformedParserException
from laggard.parserGenerators import *


class Rule:
    def __init__(self, parser: Callable, name: str = None):
        self.parser = parser
        if name:
            self.__name__ = name
        else:
            self.__name__ = self.parser.__name__

    def __and__(self, other):
        if isinstance(other, Rule):
            return Rule(generateAnd(self, other))
        else:
            return Rule(generateAnd(self, Rule(other)))

    def __rand__(self, other):
        return Rule(generateAnd(Rule(other), self))

    def __or__(self, other):
        if isinstance(other, Rule):
            return Rule(generateOr(self, other))
        else:
            return Rule(generateOr(self, Rule(other)))
    def __ror__(self, other):
        return Rule(generateOr(Rule(other), self))

    def parse(self, buffer:Buffer):
        return self.parser(buffer)

    def __call__(self, buffer:Buffer):
        return self.parser(buffer)


def makeRule(obj, **kwargs):
    if "optional" in kwargs and "multiple" in kwargs:
        del kwargs["optional"]
        del kwargs["multiple"]
        return generate_some_or_none_rule(makeRule(obj, **kwargs))
    elif "multiple" in kwargs:
        del kwargs["multiple"]
        return generate_multiple_rule(makeRule(obj, **kwargs))
    elif "optional" in kwargs:
        del kwargs["optional"]
        return generate_optional_rule(makeRule(obj, **kwargs))
    else:
        if isinstance(obj, Rule):
            return Rule(obj.parser, **kwargs)
        elif callable(obj):
            return Rule(obj, **kwargs)
        elif isinstance(obj, str):
            return Rule(generate_literal_expecter(obj), **kwargs)
        elif isinstance(obj, (tuple, set, list)):
            return Rule(generate_charset_expecter(obj, name=kwargs.get("name", None)))
        else:
            raise MalformedParserException("Cannot create a rule from {}".format(obj))