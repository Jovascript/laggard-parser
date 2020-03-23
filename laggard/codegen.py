import textwrap
from typing import List

from laggard.grammar_asts import Grammar, Combined, Choice, ModifiedRuleExpression, LabelledRuleExpression, Identifier, \
    Literal

OPTIONAL_TEMPLATE = """try:
    return {}
except ParseException:
    return None"""

MULTIPLE_TEMPLATE = """try:
    x = []
    while True:
        x.append({})
except ParseException:
    return x"""

MANY_TEMPLATE = """try:
    x = []
    while True:
        x.append({})
except ParseException:
    if not len(x):
        raise
    return x"""

class CodeGenerator:
    def __init__(self, root: Grammar):
        self.root = root
        self.code: str = ""
        self.functions = []
        self.fragment_counts = {}
        self.context: List[str] = []

    def generate(self):
        for rule in self.root.children:
            if isinstance(rule.name, Identifier):
                n = rule.name.name
            else:
                n = rule.name
            self.generate_rule(rule.children[0], n, inline=False)

        content = "\n".join(["from laggard.abstracts import Parser", "from laggard.exceptions import ParseException", "class MyParser(Parser):\n"])
        for f in self.functions:
            content += textwrap.indent(f, " "*4) + "\n"
        return content


    def generate_rule(self, children, name, inline=True):
        if not inline:
            # Reset the name context
            self.context.clear()

        content = ""
        if isinstance(children, Combined):
            if len(children.children) > 1:
                content = "return [\n"
            else:
                content = "return "
            for i, child in enumerate(children.children):
                content += self.generate_rule(child, name)
                if len(children.children) > 1:
                    content += ","
                content += "\n"
            if len(children.children) > 1:
                content += "]"

        elif isinstance(children, Choice):
            for i, child in enumerate(children.children):
                content = "try:"
                content += "\n" + textwrap.indent("return " + self.generate_rule(child, name), " "*4)
                if i+1 < len(children.children):
                    content += "\nexcept ParseException: pass"

        elif isinstance(children, ModifiedRuleExpression):
            template = OPTIONAL_TEMPLATE if children.modifier == "?" else (MANY_TEMPLATE if children.modifier == "+" else MULTIPLE_TEMPLATE)
            content = template.format(self.generate_rule(children.expr, name))
        elif isinstance(children, LabelledRuleExpression):
            content = "return {} # Label: {}".format(self.generate_rule(children.expr,name), children.label)
        elif isinstance(children, Identifier):
            content = "return self.parse_{}()".format(children.name)
        elif isinstance(children, Literal):
            content = "return self.expect(\"{}\")".format(children.value)

        if inline:
            # Always produces a fragment function
            # TODO: Make 100000% more efficient with 1x10^02394823049832 thinks
            name = self.add_fragment(name, content)
        else:
            name = self.add_rule(name, content)

        # Returns the code to call the gen function
        return name


    def add_to_context(self, name=None):
        self.context.append(name)

    def add_function(self, name, content):
        s = "\ndef {}(self):".format(name)
        s += "\n" + textwrap.indent(content, " "*4)
        self.functions.append(s)
        return f"self.{name}()"

    def add_rule(self, rule_name, content):
        return self.add_function(f"parse_{rule_name}", content)

    def add_fragment(self, rule_name, content):
        try:
            self.fragment_counts[rule_name] = self.fragment_counts[rule_name] + 1
        except KeyError:
            self.fragment_counts[rule_name] = 1
        name = "parse_{}_fragment{}".format(rule_name, self.fragment_counts[rule_name])
        return self.add_function(name, content)



