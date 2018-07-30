import pytest

from laggard.buffer import Buffer
from laggard.exceptions import ParseException
from laggard.helpers import expect_literal


def test_expect_literal():
    buf = Buffer("hellogoodbye")
    expect_literal(buf, "hello")
    assert expect_literal(buf, "goodbye") == "goodbye"

def test_expect_literal_errors():
    buf = Buffer("hellogoodbye")
    expect_literal(buf, "hello")
    with pytest.raises(ParseException):
        expect_literal(buf, "world")