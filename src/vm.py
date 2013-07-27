# encoding: utf-8
from __future__ import unicode_literals, print_function

__all__ = ['run']

import os
import sys
import operator

def binop(op, vm):
    '''Pop two operands off stack, apply operator, push result'''
    y = vm.pop()
    x = vm.pop()
    vm.push(op(x, y))

class Instruction(object):
    def __init__(self, sym, pop, push):
        '''Each instruction (except Push) has a symbol and
           pushes or pops some number of operands from the stack'''
        self.sym = sym
        self.pop = pop
        self.push = push

    def __repr__(self):
        '''Print evaluable representation of instruction'''
        return '{}("{}", {}, {})'.format(
            self.__class__.__name__,
            self.sym,
            self.push,
            self.pop,
        )

    def pprint(self):
        '''Return source-equivalent string'''
        return self.sym

    def ccode(self):
        '''Generate C-code for instruction'''
        return 'PSYM("{}"); {}();'.format(
            self.sym,
            self.__class__.__name__.upper(),
        )

    def gen(self, context):
        '''Generate llvm code for instruction'''
        raise NotImplemented

    def run(self, vm):
        '''Run instruction on virtual machine'''
        raise notImplemented

class Write(Instruction):
    def gen(self, context):
        pass

    def run(self, vm):
        '''Write TOS to stdout as ascii'''
        x = vm.pop()
        sys.stdout.write(chr(x))

class Read(Instruction):
    def gen(self, context):
        pass

    def run(self, vm):
        '''Push one value from stdin or -1 on EOF'''
        try:
            vm.push(ord(os.read(sys.stdin.fileno(), 1)))
        except:
            vm.push(-1)

class Save(Instruction):
    def gen(self, context):
        pass

    def run(self, vm):
        '''Save value at TOS-1 in address at TOS'''
        addr = vm.pop()
        value = vm.pop()
        vm.save(value, addr)

class Load(Instruction):
    def gen(self, context):
        pass

    def run(self, vm):
        '''Load value from address at TOS'''
        vm.push(vm.load(vm.pop()))

class Add(Instruction):
    def gen(self, context):
        pass

    def run(self, vm):
        '''Push (TOS-1) + TOS'''
        binop(operator.add, vm)

class Sub(Instruction):
    def gen(self, context):
        pass

    def run(self, vm):
        '''Push (TOS-1) - TOS'''
        binop(operator.sub, vm)

class Eql(Instruction):
    def gen(self, context):
        pass

    def run(self, vm):
        '''Push (TOS-1) == TOS'''
        eqint = lambda x, y: int(x == y)
        binop(eqint, vm)

class Push(Instruction):
    def __init__(self, value):
        '''Push instruction just pushes int on stack'''
        self.value = value

    def __repr__(self):
        '''Print evaluable representation for Push'''
        return 'Push({})'.format(self.value)

    def pprint(self):
        return str(self.value)

    def ccode(self):
        '''Generate C-code to push int on stack'''
        return 'PNUM({0}); PUSH({0});'.format(self.value)

    def gen(self, context):
        pass

    def run(self, vm):
        '''Push value on stack'''
        vm.push(self.value)

# Only need one instance of each of these
instructions = [
    Write('.', 1, 0),
    Read(',', 0, 1),
    Save('$', 2, 0),
    Load('&', 1, 1),
    Add('+', 2, 1),
    Sub('-', 2, 1),
    Eql('=', 2, 1),
]

# Map instruction symbols to instructions for lexer and parser
symbols = {
    ins.sym: ins
    for ins in instructions
}

class VM(object):
    def __init__(self, maxstack, maxmem=1024 * 1024):
        '''VM tracks stack and memory and evaluates instructions'''
        assert maxstack > 0, "Stack size must be greater than zero"
        assert maxmem > 0, "Memory size must be greater than zero"
        self.maxstack = maxstack
        self.maxmem = maxmem
        self.reset()

    def reset(self):
        '''Reset virtual machine to initial configuration'''
        self.sp = 0
        self.stack = [0] * self.maxstack
        self.memory = [0] * self.maxmem

    def tos(self):
        '''Return value on top-of-stack'''
        return self.stack[self.sp - 1]

    def push(self, x):
        '''Push value on stack'''
        self.stack[self.sp] = x
        self.sp += 1

    def pop(self):
        '''Pop value off of stack'''
        self.sp -= 1
        return self.stack[self.sp]

    def load(self, addr):
        '''Load value from memory at address'''
        return self.memory[addr]

    def save(self, value, addr):
        '''Store value in memory at address'''
        self.memory[addr] = value

    def getStack(self):
        '''Get stack up to stack pointer'''
        return self.stack[:self.sp]

    def run(self, source, verbose=False):
        '''Run source mapping { label: [instruction] } on machine'''
        expression = source.get(0)
        while expression:
            if verbose:
                print(pExpr(expression), file=sys.stderr)
            for instruction in expression:
                if verbose:
                    print(pState(instruction, self), file=sys.stderr)
                instruction.run(self)
            if verbose:
                print(pLast(self.tos()), file=sys.stderr)
            expression = source.get(self.pop())

def pExpr(expression):
    '''Print expression for debugging'''
    instructions = ' '.join(instruction.pprint() for instruction in expression)
    return 'goto ({})'.format(instructions)

def pState(instruction, vm):
    '''Print current VM state'''
    stack = ' '.join(map(str, vm.getStack()))
    return '{:>4} | {}'.format(instruction.pprint(), stack)

def pLast(value):
    return '     | {}'.format(value)

def run(maxstack, source, verbose=False):
    '''Evaluate expressions and jump to result until result does not appear
       as a label in source'''
    VM(maxstack).run(source, verbose)

