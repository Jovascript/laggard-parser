from collections import Callable
from typing import List

from laggard.buffer import Buffer
from laggard.exceptions import ParseException
from laggard.rulebuilders import RuleBuilder


class FunctionalRuleBuilder(RuleBuilder):
    def __init__(self, fun: Callable, **kwargs):
        super().__init__(**kwargs)
        self.fun = fun

    def generate_parser(self):
        return self.fun


class LiteralExpecter(RuleBuilder):
    def __init__(self, literal: str, **kwargs):
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
    def __init__(self, charset: List[str], **kwargs):
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
    def __init__(self, rule: RuleBuilder, **kwargs):
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
    def __init__(self, rule: RuleBuilder, **kwargs):
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
    def __init__(self, rule: RuleBuilder, **kwargs):
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
