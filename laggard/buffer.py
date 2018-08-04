from typing import List

from laggard.exceptions import ParseException


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
    def __init__(self, source: str, skip: List[str] = []):
        """
        Args:
            source: A string, which is used as the text to be parsed.
            skip: A list of the characters which the buffer will skip; they will not appear in the results of :meth:`fetch`.
        """
        self.source = source
        self.stack = []
        self.current_index = 0
        self.skip = skip

    @property
    def last_pos(self) -> tuple:
        """The last position the stack was located."""
        curi = self.stack[-1]
        lineno = self.source.count("\n", 0, curi)
        colno = self.current_index - self.source.rfind("\n", 0, curi)
        return (lineno, colno)

    @property
    def current_pos(self) -> tuple:
        """The current position of the buffer, as a tuple (line number, column number)"""
        lineno = self.source.count("\n", 0, self.current_index)
        colno = self.current_index - self.source.rfind("\n", 0, self.current_index)
        return (lineno, colno)

    def fetch(self, count: int = 1) -> str:
        """
        Fetches the next section from the buffer

        Args:
            count: Length of required string

        Returns:
            A string of specified length

        """
        retval = ""
        while len(retval) < count and self.current_index < len(self.source):
            if self.source[self.current_index] not in self.skip:
                retval += self.source[self.current_index]
            self.current_index += 1
        return retval

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
