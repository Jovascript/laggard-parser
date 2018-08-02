from copy import copy
from functools import wraps
from typing import List, Callable, Any

from laggard.buffer import Buffer
from laggard.exceptions import ParseException


class RuleBuilder:
    """Builds rules, can be *named*(defined by user) or anonymous(part of generation annoyances, will get flattened
    in optimisation stage) """

    @staticmethod
    def create(source, **kwargs):
        # These things call this function
        from laggard.helpers import RulePlaceholder
        from laggard.functionalrulebuilders import LiteralExpecter, CharsetExpecter, SomeOrNoneRule, MultipleRule, OptionalRule
        if kwargs.pop("multiple", False):
            if kwargs.pop("optional", False):
                return SomeOrNoneRule(RuleBuilder.create(source), **kwargs)
            else:
                return MultipleRule(RuleBuilder.create(source), **kwargs)
        elif kwargs.get("optional", False):
            return OptionalRule(RuleBuilder.create(source), **kwargs)
        else:
            if isinstance(source, RuleBuilder):
                source.reconfigure(**kwargs)
                return source
            elif isinstance(source, RulePlaceholder):
                return source.invoke(**kwargs)
            elif isinstance(source, str):
                return LiteralExpecter(source, **kwargs)
            elif isinstance(source, (list, set, tuple)):
                return CharsetExpecter(source, **kwargs)

    def __init__(self, **kwargs):
        self.name: str = None
        self.transformer: Callable = None

        self.reconfigure(**kwargs)

        self.alias = None

    def reconfigure(self, **kwargs):
        self.name = kwargs.get("name", self.name)
        self.transformer = kwargs.get("transformer", self.transformer)

    @property
    def anonymous(self):
        return self.name is None and self.alias is None

    def __or__(self, other):
        if isinstance(other, RuleBuilder):
            return Choice(self, other)
        else:
            return Choice(self, RuleBuilder.create(other))

    def __ror__(self, other):
        return Choice(RuleBuilder.create(other), self)

    def __and__(self, other):
        if isinstance(other, RuleBuilder):
            return Combined(self, other)
        else:
            return Combined(self, RuleBuilder.create(other))

    def __rand__(self, other):
        return Choice(RuleBuilder.create(other), self)

    def __call__(self, alias):
        """Allows a rule to be labelled locally"""
        x = copy(self)
        x.alias = alias
        return x

    def flatten(self):
        pass

    def generate_parser(self) -> Callable[[Buffer], Any]:
        '''Creates the function which receives the buffer, and returns the *raw* parsing result.'''
        pass

    def generate_complete_parser(self) -> Callable[[Buffer], Any]:
        '''Creates the function which receives the buffer, and returns the *processed* parsing result(if user specified a transformation).'''
        self.flatten()
        parse = self.generate_parser()
        if self.transformer is not None:
            transform = self.transformer

            @wraps(parse)
            def wrapper(buffer: Buffer):
                result = parse(buffer)
                return transform(result)

            return wrapper
        else:
            @wraps(parse)
            def wrapper(buffer: Buffer):
                return parse(buffer)

            return wrapper


class Choice(RuleBuilder):
    """Defines a rule which requires one of many subrules to be matched."""

    def __init__(self, *args):
        super().__init__()
        self._choices: List[RuleBuilder] = list(args)

    @property
    def choices(self):
        return self._choices

    def flatten(self):
        for i, rule in enumerate(self._choices):
            rule.flatten()
            if isinstance(rule, Choice) and rule.anonymous:
                rule: Choice
                self._choices[i: i + 1] = rule.choices

    def generate_parser(self):
        parsers = [rule.generate_complete_parser() for rule in self._choices]

        def _(buffer: Buffer):
            with buffer:
                for i, parser in enumerate(parsers):
                    try:
                        return parser(buffer)
                    except ParseException:
                        if (i + 1) == len(parsers):
                            raise

        return _


class Combined(RuleBuilder):
    """Defines a rule which requires the sequential matching of several subrules."""

    def __init__(self, *args):
        super().__init__()
        self._combined = list(args)

    @property
    def combined(self):
        return self._combined

    def flatten(self):
        for i, rule in enumerate(self._combined):
            rule.flatten()
            if isinstance(rule, Combined) and rule.anonymous:
                rule: Combined
                self._combined[i: i + 1] = rule.combined

    def generate_parser(self):
        parsers = [rule.generate_complete_parser() for rule in self._combined]
        from laggard.helpers import OptionallyNamedTuple
        result_formatter = OptionallyNamedTuple.create(list(map(lambda x: x.alias, self._combined)))

        def _(buffer: Buffer):
            with buffer:
                results = list(map(lambda x: x(buffer), parsers))
                return result_formatter(results)

        return _
