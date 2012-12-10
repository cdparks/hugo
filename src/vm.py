# encoding: utf-8
from __future__ import unicode_literals, print_function

__all__ = ['run', 'eval']

import os
import sys
from collections import defaultdict
memory = [0] * 1024 * 1024

def attributes(**kwargs):
    def decorator(function):
        for k, v in kwargs.items():
            setattr(function, k, v)
        return function
    return decorator

@attributes(sym='.', pop=1, add=0)
def write(stack):
    x = stack.pop()
    sys.stdout.write(chr(x))

@attributes(sym=',', pop=0, add=1)
def read(stack):
    try:
        stack.append(ord(os.read(sys.stdin.fileno(), 1)))
    except:
        stack.append(-1)

@attributes(sym='$', pop=2, add=0)
def save(stack):
    addr = stack.pop()
    value = stack.pop()
    memory[addr] = value

@attributes(sym='&', pop=1, add=1)
def load(stack):
    addr = stack.pop()
    stack.append(memory[addr])

@attributes(sym='+', pop=2, add=1)
def add(stack):
    y = stack.pop()
    x = stack.pop()
    stack.append(x + y)

@attributes(sym='-', pop=2, add=1)
def sub(stack):
    y = stack.pop()
    x = stack.pop()
    stack.append(x - y)

@attributes(sym='=', pop=2, add=1)
def eql(stack):
    y = stack.pop()
    x = stack.pop()
    stack.append(int(x == y))

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
    def push(stack):
        stack.append(value)
    return push

def eval(expression, verbose=False):
    stack = []
    for word in expression:
        if verbose:
            print('{:>4} | {}'.format(word, ' '.join(map(str, stack))), file=sys.stderr)
        operators.get(word, pushes(word))(stack)
    if verbose:
        print('     | {}'.format(stack[0]), file=sys.stderr)
    return stack[0]

def run(source, verbose=False):
    expression = source.get(0)
    while expression is not None:
        if verbose:
            print('goto {}'.format(' '.join(map(str, expression))), file=sys.stderr)
        expression = source.get(eval(expression, verbose))

