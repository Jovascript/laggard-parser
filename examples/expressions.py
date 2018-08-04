"""
Parses simple mathematical expressions

Equivalent PEG grammar:
Arithmetic:
    Expr     <- Factor AddExpr*
    AddExpr  <- ('+'/'-') Factor
    Factor   <- Primary MulExpr*
    MulExpr  <- ('*'/'/') Primary
    Primary  <- '(' Expr ')'
              / Number
              / Variable
              / '-' Primary

    Number   <- [0-9]+
    Variable <- identifier
"""

import laggard
from laggard.constants import ALPHA, DIGIT

@laggard.rule
def expr():
    return factor & laggard.none_or_more(add_expr)

@expr.transformer
def exprt(res):
    return res[0] + ''.join(res[1])

@laggard.rule
def add_expr():
    return (laggard.RuleBuilder.create("+") | "-") & factor

@add_expr.transformer
def addt(res):
    return ''.join(res)

@laggard.rule
def factor():
    return primary & laggard.none_or_more(mul_expr)

@factor.transformer
def factt(res):
    return res[0] + ''.join(res[1])

@laggard.rule
def mul_expr():
    return (laggard.RuleBuilder.create("*") | "/")("x") & primary("y")

@mul_expr.transformer
def mult(res):
    return ''.join(res)

@laggard.rule
def primary():
    return number | variable

@laggard.rule
def number():
    return laggard.multiple(DIGIT)

@number.transformer
def ntrans(res):
    return ''.join(res)

@laggard.rule
def variable():
    return laggard.multiple(ALPHA)

buf = laggard.Buffer("5+5*2")

invoked = expr.invoke()

parser = invoked.generate_complete_parser()

print(parser(buf))