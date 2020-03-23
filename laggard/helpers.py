from typing import List, Any, Callable, Union

from laggard.buffer import Buffer
from laggard.exceptions import ParseException


def expect(buffer: Buffer, literal: str):
    with buffer:
        x = buffer.fetch(len(literal), skip="initial")
        if x == literal:
            return literal
        else:
            buffer.cry("expected '{}', got '{}'".format(literal, x))


def expectOneOf(buffer: Buffer, charset: List[str], skip: bool = True):
    with buffer:
        x = buffer.fetch_char(skip)
        if x in charset:
            return x
        else:
            buffer.cry("expected one of {}, got {}".format(', '.join(charset), x))


def expectManyOutOf(buffer: Buffer, charset: List[str]):
    with buffer:
        v = expectOneOf(buffer, charset, skip=True)
        try:
            while True:
                v += expectOneOf(buffer, charset, skip=False)
        except ParseException:
            return v


def parseMultipleOf(buffer: Buffer, parser: Callable, accept_none: bool = False):
    with buffer:
        parses = []
        try:
            while True:
                parses.append(parser())
        except ParseException:
            if (not accept_none) and len(parses) < 1:
                raise
            else:
                return parses


def parseUntil(buffer: Buffer, charset: List[str]):
    with buffer:
        return_val = ""
        last_char = None
        while last_char not in charset:
            last_char = buffer.fetch_char(False)
            return_val += last_char
        return return_val[:-1]


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
