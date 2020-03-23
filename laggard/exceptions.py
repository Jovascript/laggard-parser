from typing import List

from laggard.infoholders import ParseInfo


class ParseException(Exception):
    """
    Raised when the current rule cannot parse the input string.
    This exception is usually non-fatal, and will merely result in the parser backtracking to find the next possible rule to parse.
    It is recommended that this exception be raised with the utility method :meth:`Buffer.cry(message) <laggard.buffer.Buffer.cry>`
    """


class MalformedParserException(Exception):
    """
    Raised when the rule cannot be created because the parser has the incorrect structure.
    This will usually occur during :meth:`~laggard.rulebuilders.RuleBuilder.generate_complete_parser()`.
    """
    pass

class ExpectationException(ParseException):
    pass


