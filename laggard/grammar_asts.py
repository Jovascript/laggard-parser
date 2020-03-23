from laggard.ast import ASTNode


class Combined(ASTNode): pass


class Choice(ASTNode): pass


class Rule(ASTNode):
    def __init__(self, name, content):
        super().__init__([content])
        self.name = name

    def get_name(self):
        return "{}: {}".format(super().get_name(), self.name)


class ModifiedRuleExpression(ASTNode):
    def __init__(self, expr:ASTNode, modifier:str):
        super().__init__([expr, modifier])
        self.expr = expr
        self.modifier = modifier


class LabelledRuleExpression(ASTNode):
    def __init__(self, name: str, expr: ASTNode):
        super().__init__([name, expr])
        self.label = name
        self.expr = expr


class RuleLeftHand(ASTNode):
    def __init__(self, name: str, transformer: str = None):
        super().__init__([name, transformer])
        self.name = name
        self.transformer = transformer

class Literal(ASTNode):
    def __init__(self, value):
        super(Literal, self).__init__([value])
        self.value = value

class Identifier(ASTNode):
    def __init__(self, name):
        super(Identifier, self).__init__([name])
        self.name = name

class Grammar(ASTNode): pass