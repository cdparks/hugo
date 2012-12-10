# encoding: utf-8
from __future__ import unicode_literals, print_function

__all__ = ['parse']

from collections import namedtuple

from src.vm import operators

Token = namedtuple('Token', 'tag value')
EOL, OPERATOR, INTEGER, OTHER = range(4)

def tokenize(line):
    for word in line.split():
        if word in operators:
            yield Token(OPERATOR, operators[word])
        elif word.isdigit():
            yield Token(INTEGER, int(word))
        else:
            yield Token(OTHER, word)
    yield Token(EOL, '<EOL>')

def parseExpr(line, maxstack, label, stream):
    expression = [label]
    stack = 1
    for token in stream:
        if token.tag == INTEGER:
            stack += 1
            maxstack = max(stack, maxstack)
            expression.append(token.value)
        elif token.tag == OPERATOR:
            function = token.value
            if stack < function.pop:
                raise SyntaxError("{}: Too few arguments to {} at label {}".format(line, function.sym, label))
            stack -= function.pop
            stack += function.add
            maxstack = max(stack, maxstack)
            expression.append(function.sym)
        elif token.tag == EOL:
            break
        else:
            raise SyntaxError("{}: Unexpected token '{}' in expression at label {}".format(line, token.value, label))
    if stack != 1:
        raise SyntaxError("{}: Malformed expression at label {}".format(line, label))
    return maxstack, expression

def parse(filename):
    source = {}
    maxstack = 1
    for i, line in enumerate(open(filename)):
        stream = tokenize(line.strip())
        token = next(stream)
        if token.tag == INTEGER:
            maxstack, source[token.value] = parseExpr(i, maxstack, token.value, stream)
    return maxstack, source

