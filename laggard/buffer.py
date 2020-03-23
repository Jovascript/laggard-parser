from collections import namedtuple
from typing import List, Union

from laggard.exceptions import ParseException
from laggard.infoholders import TextPosition

StackEntry = namedtuple("StackEntry", ["pos", "name"])


class Buffer:
    """
    Represents the incoming stream of characters for the parser, provided by a source string.
    An instance of :class:`Buffer` is a `context manager <http://book.pythontips.com/en/latest/context_managers.html#context-managers>`_.

    Examples:
        To parse the string "hello"::

            buf = Buffer("hello")
            # Execute a parser with buf now

        In a parsing function, to make the buffer revert if a :class:`~laggard.exceptions.ParseException` occurs, simply use buffer as a context manager::

            with buffer:
                if is_bad_text():
                    raise ParseException
                else:
                    return "good text :)"

        If the function returns successfully, the buffer will be moved forward(:meth:`commit`), otherwise it will :meth:`abandon`.

    """

    def __init__(self, source: str, skip: List = []):
        """
        Args:
            source: A string, which is used as the text to be parsed.
            skip: A list of the characters which the buffer will skip; they will not appear in the results of :meth:`fetch`.
        """
        self.source = source
        self.stack: List[int] = []
        self.current_index = 0
        self.skip = skip

    def _get_position_from_index(self, index):
        # Line number should start at 1
        line_number = self.source.count("\n", 0, index) + 1
        column_number = index - self.source.rfind("\n", 0, index)
        return TextPosition(line_number, column_number)

    @property
    def last_pos(self) -> TextPosition:
        """The last position the stack was located."""
        if len(self.stack):
            return self._get_position_from_index(self.stack[-1])
        else:
            return TextPosition(0, 0)

    @property
    def current_pos(self) -> TextPosition:
        """The current position of the buffer, as a tuple (line number, column number)"""
        return self._get_position_from_index(self.current_index)

    def fetch_char(self, skip=True) -> str:
        try:
            while True:
                x = self.source[self.current_index]
                self.current_index += 1
                if x not in self.skip or (not skip):
                    return x
        except IndexError:
            return "[EOF]"

    def fetch(self, count: int = 1, skip: Union[str, bool] = True) -> str:
        """
        Fetches the next section from the buffer

        Args:
            count: Length of required string
            skip: Whether the Buffer's skip property should be respected.

        Returns:
            A string of specified length

        """
        retval = ""
        # Skip until the first char
        if skip == "initial":
            retval += self.fetch_char(True)
            count -= 1
            skip = False

        for i in range(count):
            retval += self.fetch_char(skip)
        return retval

    def peek(self, count: int = 1, skip: bool = True) -> str:
        self.mark()
        try:
            return self.fetch(count, skip)
        finally:
            self.abandon()

    def mark(self):
        """
        Adds the current location to the stack.
        """
        self.stack.append(self.current_index)
        print(len(self.stack))

    def abandon(self):
        """
        Reverts to last recorded position on the stack
        """
        self.current_index = self.stack.pop()

    def commit(self):
        """
        Progresses on the buffer.
        """
        self.stack.pop()

    def cry(self, message: str):
        """Raises a parse error with the location detailed.

        Args:
            message: The simple parse message, not a full sentence.
        """
        raise ParseException("Failed to parse: {} at {}".format(message, self.last_pos))

    def __enter__(self):
        self.mark()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.abandon()
        else:
            self.commit()

    def is_eof(self):
        print(self.current_index)
        return self.current_index + 1 >= len(self.source)
