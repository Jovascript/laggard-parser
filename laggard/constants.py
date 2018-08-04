import string

from laggard.rulebuilders import RuleBuilder

#: Rule which recognises characters A-Z and a-z
ALPHA: RuleBuilder = RuleBuilder.create(list(string.ascii_letters), name="ALPHABET")
#: Rule which recognises characters A-Z, a-z and 0-9
ALPHANUM: RuleBuilder = RuleBuilder.create(list(string.ascii_letters+string.digits), name="ALPHANUMERICS")
#: Rule which recognises most punctuation( _!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~_)
PUNCTUATION = RuleBuilder.create(list(string.punctuation), name="PUNCTUATION")
#: Rule which recognises whitespace
WHITESPACE = RuleBuilder.create(list(string.whitespace), name="WHITESPACE")
#: Rule which recognises characters A-Z, a-z and 0-9
DIGIT: RuleBuilder = RuleBuilder.create(list(string.digits), name="DIGIT")


