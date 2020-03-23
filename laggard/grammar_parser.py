import string

from laggard.buffer import Buffer
from laggard.exceptions import ParseException
from laggard.grammar_asts import Combined, Choice, Rule, ModifiedRuleExpression, LabelledRuleExpression, Grammar, \
    Identifier, Literal
from laggard.helpers import expectManyOutOf, expect, parseMultipleOf, expectOneOf, parseUntil


class Parser:
    def __init__(self, source: str):
        self.buffer = Buffer(source, skip=[" ", "\n", "\t"])

    def parse(self):
        retval = []
        try:
            while True:
                retval.append(self.parse_rule())
        except ParseException:
            if self.buffer.is_eof():
                return Grammar(retval)
            raise

    def parse_rule(self):
        with self.buffer:
            x = []
            x.append(self.parse_identifier())
            expect(self.buffer, "=")
            x.append(self.parse_righthand())
            expect(self.buffer, ";")
            return Rule(*x)

    def parse_lefthand(self):
        with self.buffer:
            name = self.parse_identifier()
            try:
                expect(self.buffer, ":")
                transformer = self.parse_identifier()
                return
            except ParseException:
                return name

    def parse_righthand(self):
        with self.buffer:
            return self.parse_choice()

    def parse_choice(self):
        with self.buffer:
            x = self.parse_combination()
            try:
                y = parseMultipleOf(self.buffer, self.parse_choice_fragment)
                return Choice([x] + y)
            except ParseException:
                return x

    def parse_choice_fragment(self):
        with self.buffer:
            expect(self.buffer, "|")
            return self.parse_combination()

    def parse_combination(self):
        with self.buffer:
            x = self.parse_modified_rule_expression()
            try:
                y = parseMultipleOf(self.buffer, self.parse_modified_rule_expression)
                return Combined([x] + y)
            except ParseException:
                return x

    def parse_modified_rule_expression(self):
        with self.buffer:
            expr = self.parse_rule_match_expression()
            try:
                sym = expectOneOf(self.buffer, ["*", "+", "?"], skip=False)
                return ModifiedRuleExpression(expr, sym)
            except:
                return expr



    def parse_rule_match_expression(self):
        with self.buffer:
            try:
                expect(self.buffer, "(")
                x = self.parse_choice()
                expect(self.buffer, ")")
                return x
            except ParseException:
                try:
                    name = self.parse_identifier()
                    try:
                        expect(self.buffer, ":")
                        expr = self.parse_modified_rule_expression()
                        return LabelledRuleExpression(name, expr)
                    except ParseException:
                        return name
                except ParseException:
                    return self.parse_string()

    def parse_identifier(self):
        return Identifier(expectManyOutOf(self.buffer, list(string.ascii_letters + string.digits)))

    def parse_string(self):
        with self.buffer:
            x = expectOneOf(self.buffer, ["'", '"'])
            return Literal(parseUntil(self.buffer, [x]))
