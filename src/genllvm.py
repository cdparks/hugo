# encoding: utf-8

# llvm API expects byte-strings for most names, so ignore this for now
# from __future__ import unicode_literals, print_function

__all__ = ['buildModule']

import functools
from llvm.core import (
    Module,
    Constant,
    Type,
    Function,
    Builder,
    GlobalVariable,
    ICMP_EQ,
)

class Context(object):
    '''Store global functions and current builder'''
    def __init__(self, **bindings):
        self.bindings = bindings
        self.builder = None

    def __getattr__(self, attr):
        '''Partially apply function call with builder'''
        if attr in self.bindings:
            return functools.partial(
                self.bindings[attr],
                self.builder,
            )
        raise AttributeError('Context object has no attribute {!r}'.format(attr))

def num(x, bits=32):
    '''Helper for building integers'''
    return Constant.int(Type.int(bits=bits), x)

def array(ls):
    '''Helper for building arrays'''
    return Constant.array(Type.int(), ls)

def buildStack(module, maxstack):
    '''Build stack and stack pointer'''

    # Build stack
    stackType = Type.array(Type.int(), maxstack)
    stack = GlobalVariable.new(module, stackType, 'stack')
    stack.initializer = array([num(0)] * maxstack)

    # Build stack pointer
    sp = GlobalVariable.new(module, Type.int(bits=64), 'sp')
    sp.initializer = num(0, bits=64)
    return stack, sp

def buildMemory(module, maxmem):
    '''Build memory array'''
    memoryType = Type.array(Type.int(), maxmem)
    memory = GlobalVariable.new(module, memoryType, 'memory')
    memory.initializer = array([num(0)] * maxmem)
    return memory

def buildPutchar(module):
    '''Build forward declaration to putchar'''

    # Declare putchar
    putcharType = Type.function(Type.int(), [Type.int()], False)
    putchar = Function.new(module, putcharType, 'putchar')

    # Build function to call putchar
    def _putchar(builder, char):
        builder.call(putchar, [char])
    return _putchar

def buildGetchar(module):
    '''Build forward declaration to getchar'''

    # Declare getchar
    getcharType = Type.function(Type.int(), [], False)
    getchar = Function.new(module, getcharType, 'getchar')

    # Build function to call builder
    def _getchar(builder):
        return builder.call(getchar, [])
    return _getchar

def buildPush(module, stack, sp):
    '''Build function to push value on stack'''

    # Declare push
    pushType = Type.function(Type.void(), [Type.int()], False)
    push = Function.new(module, pushType, 'push')

    # Build body
    body = push.append_basic_block('body')
    builder = Builder.new(body)

    # Load stack pointer
    index = builder.load(sp, 'index')
    ptr = builder.gep(stack, [num(0), index], 'ptr')

    # Store value in stack
    builder.store(push.args[0], ptr)

    # Increment stack pointer
    inc = builder.add(index, num(1, bits=64), 'new-sp')
    builder.store(inc, sp)

    # Exit function
    builder.ret_void()
    push.verify()

    # Build function to call push
    def _push(builder, value):
        # Call push with value
        if isinstance(value, int):
            value = num(value)
        return builder.call(push, [value])
    return _push

def buildPop(module, stack, sp):
    '''Build function to pop value off stack'''

    # Declare pop
    popType = Type.function(Type.int(), [], False)
    pop = Function.new(module, popType, 'pop')

    # Build body
    body = pop.append_basic_block('body')
    builder = Builder.new(body)

    # Load stack pointer
    tmp = builder.load(sp, 'old-sp')

    # Decrement stack pointer
    index = builder.sub(tmp, num(1, bits=64), 'index')
    builder.store(index, sp)

    # Load value from stack
    ptr = builder.gep(stack, [num(0), index], 'ptr')
    tos = builder.load(ptr, 'tos')

    # Return value
    builder.ret(tos)
    pop.verify()

    # Build function to call pop
    def _pop(builder):
        return builder.call(pop, [], 'pop')
    return _pop

def buildSave(module, memory):
    '''Build function to save value to memory at address'''

    # Declare save
    saveType = Type.function(Type.void(), [Type.int(), Type.int()], False)
    save = Function.new(module, saveType, 'save')

    # Build body
    body = save.append_basic_block('body')
    builder = Builder.new(body)

    # Get pointer to memory at address
    value, addr = save.args
    addr64 = builder.sext(addr, Type.int(bits=64))
    mp = builder.gep(memory, [num(0), addr64], 'mp')
    builder.store(value, mp)

    # Exit function
    builder.ret_void()
    save.verify()

    # Build function to call save
    def _save(builder, value, addr):
        return builder.call(save, [value, addr])
    return _save

def buildLoad(module, memory):
    '''Build function load value from memory at address'''

    # Declare load
    loadType = Type.function(Type.int(), [Type.int()], False)
    load = Function.new(module, loadType, 'load')

    # Build body
    body = load.append_basic_block('body')
    builder = Builder.new(body)

    # Get pointer to memory at address
    addr = builder.sext(load.args[0], Type.int(bits=64))
    mp = builder.gep(memory, [num(0), addr], 'mp')
    deref = builder.load(mp, 'deref')

    # Return value
    builder.ret(deref)
    load.verify()

    # Build function to call load
    def _load(builder, addr):
        return builder.call(load, [addr], 'load')
    return _load

def add(builder, x, y):
    '''Generate add instruction'''
    return builder.add(x, y, 'add')

def sub(builder, x, y):
    '''Generate sub instruction'''
    return builder.sub(x, y, 'sub')

def eql(builder, x, y):
    '''Generate icmp instruction'''
    cmp = builder.icmp(ICMP_EQ, x, y, 'cmp')
    return builder.zext(cmp, Type.int(), 'convert')

def buildMain(module, context, source):
    '''Build main function'''

    # Declare main function
    mainType = Type.function(Type.int(), [], False)
    main = Function.new(module, mainType, 'main')

    # Build entry block
    entry = main.append_basic_block('entry')
    builder = Builder.new(entry)
    next = builder.alloca(Type.int(), 'next')
    builder.store(num(0), next)

    # Build exit block
    exit = main.append_basic_block('exit')
    builder = Builder.new(exit)
    builder.ret(num(0))

    # Build block for switch-case
    loop = main.append_basic_block('loop')
    builder = Builder.new(loop)
    jump = builder.load(next, 'jump')
    switch = builder.switch(jump, exit)
    builder = Builder.new(entry)
    builder.branch(loop)

    # For each expression build a block that jumps back up to switch
    # and add label-block pair to switch block
    for label, expression in sorted(source.items()):
        case = main.append_basic_block('case{}'.format(label))
        context.builder = Builder.new(case)
        for instruction in expression:
            instruction.gen(context)
        context.builder.store(context.pop(), next)
        context.builder.branch(loop)
        switch.add_case(num(label), case)
    return main

def buildModule(filename, source, maxstack, maxmem=1024 * 1024):
    '''Generate LLVM-IR for module'''

    # Build module
    module = Module.new(filename)

    # Build stack and stack pointer
    stack, sp = buildStack(module, maxstack)

    # Build memory
    memory = buildMemory(module, maxmem)

    # Build functions
    context = Context(
        read=buildGetchar(module),
        write=buildPutchar(module),
        push=buildPush(module, stack, sp),
        pop=buildPop(module, stack, sp),
        save=buildSave(module, memory),
        load=buildLoad(module, memory),
        add=add,
        sub=sub,
        eql=eql,
    )

    # Build main
    main = buildMain(module, context, source)
    main.verify()
    module.verify()
    return module

