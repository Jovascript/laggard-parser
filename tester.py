from laggard import *
from laggard.constants import ALPHA


@rule
def phrase():
    return multiple(word("word") & space)("initial") & word("last")

@phrase.transformer
def phrasetransformer(x):
    res = ""
    for n in x["initial"]:
        res += n["word"] + " "
    res += x["last"]
    return res

@rule
def word():
    return multiple(ALPHA)

@rule
def space():
    return ' '

@word.transformer
def wordtransformer(result):
    return ''.join(result)

x = phrase.invoke()

buf = Buffer("Hello World")

parser = x.generate_complete_parser()
y = parser(buf)
print(y)