# encoding: utf-8
from __future__ import unicode_literals, print_function

__all__ = ['parse']

from collections import namedtuple
from src.vm import symbols, literal

Token = namedtuple('Token', 'tag value')
EOL, OPERATOR, INTEGER, OTHER = range(4)

def tokenize(line):
    '''This was much more interesting when the language used S-Expressions
       instead of RPN.
    '''
    for word in line.split():
        if word in symbols:
            yield Token(OPERATOR, symbols[word])
        elif word.isdigit():
            yield Token(INTEGER, int(word))
        else:
            yield Token(OTHER, word)
    yield Token(EOL, '<EOL>')

def parseExpr(line, maxstack, label, stream):
    '''Verify that current line is a valid RPN expression. Return maximum
       stack size and expression as a list of symbols.
    '''
    expression = [literal(label)]
    stack = 1
    for token in stream:
        if token.tag == INTEGER:
            stack += 1
            maxstack = max(stack, maxstack)
            expression.append(literal(token.value))
        elif token.tag == OPERATOR:
            instruction = token.value
            if stack < instruction.pop:
                raise SyntaxError("{}: Too few arguments to {} at label {}".format(line, instruction.sym, label))
            stack -= instruction.pop
            stack += instruction.push
            maxstack = max(stack, maxstack)
            expression.append(instruction.idx)
        elif token.tag == EOL:
            break
        else:
            raise SyntaxError("{}: Unexpected token '{}' in expression at label {}".format(line, token.value, label))
    if stack != 1:
        raise SyntaxError("{}: Malformed expression at label {}".format(line, label))
    return maxstack, expression

def parse(filename):
    '''Parse file and return a dictionary mapping labels to expressions.'''
    source = {}
    maxstack = 1
    for i, line in enumerate(open(filename)):
        stream = tokenize(line.strip())
        token = next(stream)
        if token.tag == INTEGER:
            maxstack, source[token.value] = parseExpr(i, maxstack, token.value, stream)
    return maxstack, source

