import pytest

from laggard.buffer import Buffer
from laggard.exceptions import ParseException
from laggard.rule import makeRule


def test_basic_parse():
    buf = Buffer("helloworld")
    helloworldRule = makeRule("hello") & makeRule("world")
    assert helloworldRule.parse(buf) == ["hello", "world"]

def test_failed_basic_parse():
    buf = Buffer("helloworld")
    hellogoodbyeRule = makeRule("hello") & makeRule("goodbye")
    with pytest.raises(ParseException):
        hellogoodbyeRule.parse(buf)