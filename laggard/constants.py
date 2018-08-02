import string

from laggard.rulebuilders import RuleBuilder


ALPHA = RuleBuilder.create(list(string.ascii_letters), name="ALPHABET")
ALPHANUM = RuleBuilder.create(list(string.ascii_letters+string.digits), name="ALPHANUMERICS")

PUNCTUATION = RuleBuilder.create(list(string.punctuation), name="PUNCTUATION")

WHITESPACE = RuleBuilder.create(list(string.whitespace), name="WHITESPACE")
