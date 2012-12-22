# encoding: utf-8
from __future__ import unicode_literals, print_function

__all__ = ['run', 'eval']

import os
import sys
from collections import defaultdict, namedtuple

memory = [0] * 1024 * 1024

# Instruction implementations
def write(stack):
    '''Write TOS to stdout as ascii'''
    x = stack.pop()
    sys.stdout.write(chr(x))

def read(stack):
    '''Push one value from stdin or -1 on EOF'''
    try:
        stack.append(ord(os.read(sys.stdin.fileno(), 1)))
    except:
        stack.append(-1)

def save(stack):
    '''Save value at TOS-1 in address at TOS'''
    addr = stack.pop()
    value = stack.pop()
    memory[addr] = value

def load(stack):
    '''Load value from address at TOS'''
    addr = stack.pop()
    stack.append(memory[addr])

def add(stack):
    '''Push (TOS-1) + TOS'''
    y = stack.pop()
    x = stack.pop()
    stack.append(x + y)

def sub(stack):
    '''Push (TOS-1) - TOS'''
    y = stack.pop()
    x = stack.pop()
    stack.append(x - y)

def eql(stack):
    '''Push (TOS-1) == TOS'''
    y = stack.pop()
    x = stack.pop()
    stack.append(int(x == y))

# Instructions are referred to be their index in the
# instruction list
__idx = 0
def idx():
    global __idx
    value = __idx
    __idx += 1
    return value

# Instruction contains its symbol, index, # popped values, # pushed values,
# C-code, and Python function implementation
Instruction = namedtuple('Instruction', 'sym idx pop push code impl')

# We can derive the index and C-code
def ins(sym, pop, push, impl):
    code = 'PSYM("{}"); {}();'.format(sym, impl.__name__.upper())
    return Instruction(sym, idx(), pop, push, code, impl)

# Instructions in index order
instructions = [
    ins('.', 1, 0, write),
    ins(',', 0, 1, read),
    ins('$', 2, 0, save),
    ins('&', 1, 1, load),
    ins('+', 2, 1, add),
    ins('-', 2, 1, sub),
    ins('=', 2, 1, eql),
]

# Encode literals by adding len(instructions)
lastIndex = idx()

# Map instruction symbols to instructions for lexer and parser
symbols = {
    ins.sym: ins for ins in instructions
}

def literal(value):
    '''Encode literal'''
    return value + lastIndex

def decode(word):
    '''Get instruction or literal from word'''
    if word < lastIndex:
        return instructions[word]
    else:
        return word - lastIndex

def invoke(stack, x):
    '''Invoke operator or push literal'''
    if hasattr(x, 'impl'):
        x.impl(stack)
    else:
        stack.append(x)

def px(x):
    '''Get string representation for instruction or literal x'''
    if hasattr(x, 'sym'):
        return x.sym
    return str(x)

def pexpr(expr):
    '''Get string representation for complete expression'''
    return 'goto {}'.format(' '.join(px(decode(x)) for x in expr))

def pstack(stack):
    '''Get string representation for stack'''
    return ' '.join(map(str, stack))

def eval(expression, verbose=False):
    '''Evaluate RPN expression and return last value on stack'''
    stack = []
    for word in expression:
        x = decode(word)
        if verbose:
            print('{:>4} | {}'.format(px(x), pstack(stack)), file=sys.stderr)
        invoke(stack, x)
    if verbose:
        print('     | {}'.format(stack[0]), file=sys.stderr)
    return stack[0]

def run(source, verbose=False):
    '''Evaluate expressions and jump to result until result does not appear
       as a label in source.
    '''
    expression = source.get(0)
    while expression is not None:
        if verbose:
            print(pexpr(expression), file=sys.stderr)
        expression = source.get(eval(expression, verbose))

