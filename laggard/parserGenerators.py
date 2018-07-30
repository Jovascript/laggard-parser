from typing import List

from laggard.buffer import Buffer
from laggard.exceptions import ParseException


def generateAnd(rule1, rule2):
    def _(buffer:Buffer):
        with buffer:
            return [rule1.parse(buffer), rule2.parse(buffer)]
    return _


def generateOr(rule1, rule2):
    def _(buffer:Buffer):
        with buffer:
            try:
                with buffer:
                    return rule1.parse(buffer)
            except ParseException:
                with buffer:
                    return rule2.parse(buffer)

def generate_literal_expecter(literal:str):
    def _(buffer:Buffer):
        with buffer:
            x = buffer.fetch(len(literal))
            if x == literal:
                return literal
            else:
                buffer.cry("expected '{}', got '{}'".format(literal, x))
    _.__name__ = literal
    return _

def generate_charset_expecter(charset: List[str], name:str=None):
    def _(buffer:Buffer):
        with buffer:
            x = buffer.fetch()
            if x in charset:
                return x
            else:
                if name:
                    buffer.cry("expected {}, got '{}'".format(name, x))
                else:
                    buffer.cry("expected one of {}, got '{}'".format(charset, x))
    _.__name__ = name if name else ''.join(charset)
    return _

def generate_optional_rule(rule):
    name = rule.__name__ + "?"
    parse = rule.parser
    def _(buffer:Buffer):
        with buffer:
            try:
                 return parse(buffer)
            except ParseException:
                return None
    _.__name__ = name
    return _

def generate_multiple_rule(rule):
    name = rule.__name__ + "+"
    parse = rule.parser
    def _(buffer:Buffer):
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
    _.__name__ = name
    return _

def generate_some_or_none_rule(rule):
    name = rule.__name__ + "*"
    parse = rule.parser
    def _(buffer:Buffer):
        with buffer:
            matches = []
            while True:
                try:
                    matches.append(parse(buffer))
                except ParseException:
                    return matches
    _.__name__ = name
    return _


