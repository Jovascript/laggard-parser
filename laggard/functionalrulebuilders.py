"""
This module contains :class:`~laggard.rulebuilders.RuleBuilder` subclasses, which perform certain matches on certain types.
You should **not** be instantiating these manually, but instead should use :meth:`~laggard.rulebuilders.RuleBuilder.create`
"""
from typing import Callable, List

from laggard.buffer import Buffer
from laggard.exceptions import ParseException
from laggard.rulebuilders import RuleBuilder


class FunctionalRuleBuilder(RuleBuilder):
    """
    A :class:`~laggard.rulebuilders.RuleBuilder` whose parser consists of a simple function.
    The provided function will be called with the instance of :class:`~laggard.buffer.Buffer`, and should return the parse result(or :class:`~laggard.exceptions.ParseException`)
    """
    def __init__(self, fun: Callable, **kwargs):
        """

        Args:
            fun: The callable, of signature (:class:`~laggard.buffer.Buffer`) -> Any
            **kwargs: Passed onto :class:`~laggard.rulebuilders.RuleBuilder`
        """
        super().__init__(**kwargs)
        self.fun = fun

    def generate_parser(self):
        return self.fun


class LiteralExpecter(RuleBuilder):
    """
    A :class:`~laggard.rulebuilders.RuleBuilder` which parses the provided literal.
    """
    def __init__(self, literal: str, **kwargs):
        """

        Args:
            literal: The literal to match
            **kwargs: Passed onto :class:`~laggard.rulebuilders.RuleBuilder`
        """
        super().__init__(**kwargs)
        self.literal = literal

    def generate_parser(self):
        def _(buffer: Buffer):
            with buffer:
                x = buffer.fetch(len(self.literal))
                if x == self.literal:
                    return self.literal
                else:
                    buffer.cry("expected '{}', got '{}'".format(self.literal, x))

        return _


class CharsetExpecter(RuleBuilder):
    """
    A :class:`~laggard.rulebuilders.RuleBuilder` which parses the provided charset.
    It will attempt to match any character from the provided list, once.
    """
    def __init__(self, charset: List[str], **kwargs):
        """

        Args:
            charset: The list of characters to attempt to match.
            **kwargs: Passed onto :class:`~laggard.rulebuilders.RuleBuilder`
        """
        super().__init__(**kwargs)
        self.charset = charset

    def generate_parser(self):
        def _(buffer: Buffer):
            with buffer:
                x = buffer.fetch()
                if x in self.charset:
                    return x
                else:
                    buffer.cry("expected one of {}, got '{}'".format(', '.join(self.charset), x))

        return _


class OptionalRule(RuleBuilder):
    """
    A :class:`~laggard.rulebuilders.RuleBuilder` which attempts to parse the provided :class:`~laggard.rulebuilders.RuleBuilder`, but returns `None` if it fails.
    """
    def __init__(self, rule: RuleBuilder, **kwargs):
        """

        Args:
            rule: The :class:`~laggard.rulebuilders.RuleBuilder` to parse.
            **kwargs: Passed onto :class:`~laggard.rulebuilders.RuleBuilder`
        """
        super().__init__(**kwargs)
        self.rule = rule

    def generate_parser(self):
        parse = self.rule.generate_complete_parser()

        def _(buffer: Buffer):
            with buffer:
                try:
                    return parse(buffer)
                except ParseException:
                    return None

        return _


class MultipleRule(RuleBuilder):
    """
    A :class:`~laggard.rulebuilders.RuleBuilder` which attempts to parse the provided :class:`~laggard.rulebuilders.RuleBuilder` as many times as possible.
    It must succeed at least once, or it will fail.
    It returns a list of all the parses it managed to do.
    """
    def __init__(self, rule: RuleBuilder, **kwargs):
        """

        Args:
            rule: The :class:`~laggard.rulebuilders.RuleBuilder` to parse.
            **kwargs: Passed onto :class:`~laggard.rulebuilders.RuleBuilder`
        """
        super().__init__(**kwargs)
        self.rule = rule

    def generate_parser(self):
        parse = self.rule.generate_complete_parser()

        def _(buffer: Buffer):
            with buffer:
                matches = []
                while True:
                    try:
                        matches.append(parse(buffer))
                    except ParseException:
                        if len(matches) > 0:
                            return matches
                        else:
                            raise

        return _


class SomeOrNoneRule(RuleBuilder):
    """
    A :class:`~laggard.rulebuilders.RuleBuilder` which attempts to parse the provided :class:`~laggard.rulebuilders.RuleBuilder` as many times as possible.
    It returns a list of all the parses it managed to do, and will return an empty list if it failed to parse even once.
    """
    def __init__(self, rule: RuleBuilder, **kwargs):
        """

        Args:
            rule: The :class:`~laggard.rulebuilders.RuleBuilder` to parse.
            **kwargs: Passed onto :class:`~laggard.rulebuilders.RuleBuilder`
        """
        super().__init__(**kwargs)
        self.rule = rule

    def generate_parser(self):
        parse = self.rule.generate_complete_parser()

        def _(buffer: Buffer):
            with buffer:
                matches = []
                while True:
                    try:
                        matches.append(parse(buffer))
                    except ParseException:
                        return matches

        return _
