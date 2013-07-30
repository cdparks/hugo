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

def num(x, bits=32):
    '''Helper for building integers'''
    return Constant.int(Type.int(bits=bits), x)

def eql(builder, x, y):
    '''Helper for performing equality on integers'''
    cmp = builder.icmp(ICMP_EQ, x, y)
    return builder.zext(cmp, Type.int())

def array(ls):
    '''Helper for building arrays'''
    return Constant.array(Type.int(), ls)

def buildMemory(module, maxmem):
    '''Build memory array'''
    memoryType = Type.array(Type.int(), maxmem)
    memory = GlobalVariable.new(module, memoryType, 'memory')
    memory.initializer = array([num(0)] * maxmem)
    return memory

def buildPutchar(module):
    '''Build forward declaration to putchar'''
    putcharType = Type.function(Type.int(), [Type.int()], False)
    putchar = Function.new(module, putcharType, 'putchar')

def buildGetchar(module):
    '''Build forward declaration to getchar'''
    getcharType = Type.function(Type.int(), [], False)
    getchar = Function.new(module, getcharType, 'getchar')

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
    builder.store(value, builder.gep(memory, [num(0), addr64]))

    # Exit function
    builder.ret_void()
    save.verify()

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
    value = builder.load(builder.gep(memory, [num(0), addr]))

    # Return value
    builder.ret(value)
    load.verify()

def buildMain(module, source):
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
        stack = []
        case = main.append_basic_block('case-{}'.format(label))
        builder = Builder.new(case)
        for instruction in expression:
            instruction.gen(module, builder, stack)
        builder.store(stack.pop(), next)
        builder.branch(loop)
        switch.add_case(num(label), case)
    return main

def buildModule(filename, source, maxstack, maxmem=1024 * 1024):
    '''Generate LLVM-IR for module'''

    # Build module
    module = Module.new(filename)

    # Build memory
    memory = buildMemory(module, maxmem)

    # Build functions
    buildGetchar(module),
    buildPutchar(module),
    buildSave(module, memory),
    buildLoad(module, memory),

    # Build main
    main = buildMain(module, source)
    main.verify()
    module.verify()
    return module

