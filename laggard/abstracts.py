from typing import List, Callable

from laggard import Buffer
from laggard.exceptions import ParseException
from laggard import helpers

class Parser:
    def __init__(self, source: str):
        self.source = source
        self.buffer = self._get_buffer(source)
        self.stack: List[str] = []
        self.error_stack: List[ParseException] = []
        self._mark_name: str = None

    def _get_buffer(self, source:str) -> Buffer:
        return Buffer(source)

    def parse(self):
        """
        Begin the parse.
        If the parse is unsuccessful, it will throw ParseException.
        Ensures that the end of the string provided is reached.

        Returns:
            The result of the start rule.
        """
        result = self.parse_start()
        if not self.buffer.is_eof():
            raise ParseException("Did not consume whole file.")
        return result

    def parse_start(self):
        raise NotImplementedError

    def expect(self, literal:str):
        """
        Attempts to parse the given literal. Will skip until the first char, and then no more.

        Args:
            literal: The literal to match

        Returns:
            The literal matched
        """
        return helpers.expect(self.buffer, literal)

    def expectOneOf(self, charset: List[str], skip: bool = True):
        """
        Attempts to parse a character from charset.

        Args:
            charset: The characters to accept
            skip: Whether it should skip the specified characters in buffer.

        Returns:
            The char matched
        """
        return helpers.expectOneOf(self.buffer, charset, skip)

    def expectManyOutOf(self, charset: List[str]):
        """
        Attempts to greedily parse characters from charset. It will parse at least one, or error.
        It will skip the specified chars until the first matching character, and then it will cease skipping.

        Args:
            charset: The characters to accept

        Returns:
            A string of the characters it managed to parse.
        """
        return helpers.expectManyOutOf(self.buffer, charset)

    def parseMultipleOf(self, parser: Callable, accept_none: bool = False):
        """
        Attempts to parse many of the provided parser rule.

        Args:
            parser: The callable which parses the rule
            accept_none: Whether it raises if it cannot parse even 1 of the rule

        Returns:
            A list of the parses it managed to do
        """
        return helpers.parseMultipleOf(self.buffer, parser, accept_none)

    def parseUntil(self, charset: List[str]):
        """
        Parses characters until it finds a character in charset
        Args:
            charset: The characters to look out for

        Returns:
            A string of all characters parsed
        """
        return helpers.parseUntil(self.buffer, charset)

    def __call__(self, name: str):
        """
        Allows the context manager setion to be marked with the name of the rule, for easier debugging.

        Args:
            name: The marker name

        Returns:
            Self
        """
        self._mark_name = name
        return self

    def __enter__(self):
        self.stack.append(self._mark_name)
        self.buffer.mark()
        self._mark_name = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error_stack.append()
            self.buffer.abandon()
        else:
            self.buffer.commit()

