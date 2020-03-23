from laggard.grammar_parser import Parser
from laggard.codegen import CodeGenerator

source = """
start = kitty;
kitty = "hello" "world";
"""
x = Parser(source)

m = x.parse()
print(m)

y = CodeGenerator(m)

print(y.generate())

exec(y.generate())

x = MyParser("helloworld")

print(x.parse())
