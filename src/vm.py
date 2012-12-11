# encoding: utf-8
from __future__ import unicode_literals, print_function

__all__ = ['run', 'eval']

import os
import sys
from collections import defaultdict
memory = [0] * 1024 * 1024

def attributes(**kwargs):
    '''Add arbitrary attributes to a function'''
    def decorator(function):
        for k, v in kwargs.items():
            setattr(function, k, v)
        return function
    return decorator

@attributes(sym='.', pop=1, add=0)
def write(stack):
    '''Write TOS to stdout as ascii'''
    x = stack.pop()
    sys.stdout.write(chr(x))

@attributes(sym=',', pop=0, add=1)
def read(stack):
    '''Push one value from stdin or -1 on EOF'''
    try:
        stack.append(ord(os.read(sys.stdin.fileno(), 1)))
    except:
        stack.append(-1)

@attributes(sym='$', pop=2, add=0)
def save(stack):
    '''Save value at TOS-1 in address at TOS'''
    addr = stack.pop()
    value = stack.pop()
    memory[addr] = value

@attributes(sym='&', pop=1, add=1)
def load(stack):
    '''Load value from address at TOS'''
    addr = stack.pop()
    stack.append(memory[addr])

@attributes(sym='+', pop=2, add=1)
def add(stack):
    '''Push (TOS-1) + TOS'''
    y = stack.pop()
    x = stack.pop()
    stack.append(x + y)

@attributes(sym='-', pop=2, add=1)
def sub(stack):
    '''Push (TOS-1) - TOS'''
    y = stack.pop()
    x = stack.pop()
    stack.append(x - y)

@attributes(sym='=', pop=2, add=1)
def eql(stack):
    '''Push (TOS-1) == TOS'''
    y = stack.pop()
    x = stack.pop()
    stack.append(int(x == y))

# Map string representation to function
operators = {
    write.sym: write,
    read.sym: read,
    save.sym: save,
    load.sym: load,
    add.sym: add,
    sub.sym: sub,
    eql.sym: eql,
}

def pushes(value):
    '''Return a function that pushes the specified value to the stack'''
    def push(stack):
        stack.append(value)
    return push

def eval(expression, verbose=False):
    '''Evaluate RPN expression and return last value on stack'''
    stack = []
    for word in expression:
        if verbose:
            print('{:>4} | {}'.format(word, ' '.join(map(str, stack))), file=sys.stderr)
        operators.get(word, pushes(word))(stack)
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
            print('goto {}'.format(' '.join(map(str, expression))), file=sys.stderr)
        expression = source.get(eval(expression, verbose))

