# !/usr/bin/env python
# encoding: utf-8

# author: Chris Parks
# email: christopher.daniel.parks@gmail.com
# copyright: 2012, Chris Parks
# license: MIT

'''
Hugo Uses Gotos Only!

hugo.py - an interpreter and compiler for the Hugo programming
language. For more information run:
    $ python hugo.py --help
    $ python hugo.py run --help
    $ python hugo.py gen-c --help
    $ python hugo.py gen-llvm --help
'''

from __future__ import unicode_literals, print_function

import sys
import os
import subprocess

from src.parse import parse
from src.vm import run
from src.gen import gen

def shell(command, silent=False):
    '''Run a command and suppress output'''
    if isinstance(command, list):
        command = ' '.join(map(str, command))
    stream = subprocess.PIPE if silent else None
    return subprocess.call(
        command,
        shell=True,
        stdout=stream,
        stderr=stream,
    )

def die(filename, e):
    '''Print exception and quit'''
    print("{}: {}: {}".format(filename, e.__class__.__name__, e))
    sys.exit(1)

def getName(filename):
    '''Do the bare minimum to keep the user from overwriting their source
       file.'''
    name, ext = os.path.splitext(os.path.basename(filename))
    if ext != '.hugo':
        raise Exception("Expected extension .hugo on filename '{}'.".format(filename))
    return name

def checkLLVM():
    '''Check to see if we can use the LLVM backend'''
    error = (
        'To use LLVM backend, please install Clang, LLVM 3.2, and llvmpy\n'
        'See http://www.llvmpy.org/'
    )
    try:
        import llvm
        import llvmpy
    except:
        print(error)
        sys.exit()
    if shell('which llc', silent=True):
        print('Missing llc')
        print(error)
        sys.exit()
    if shell('which clang', silent=True):
        print('Missing clang')
        print(error)
        sys.exit()

def interpret(options):
    '''Parse and run source file'''
    try:
        maxstack, source = parse(options.filename)
        run(maxstack, source, options.verbose)
    except Exception as e:
        die(options.filename, e)

def compile(options):
    '''Parse and compile source file to C'''
    try:
        # Parse file into mapping of labels to instructions
        name = getName(options.filename)
        maxstack, source = parse(options.filename)

        # Generate and write C source
        cfilename = name + '.c'
        with open(cfilename, 'w') as stream:
            stream.write(gen(maxstack, source))

        # Compile using default or specified compiler
        shell([
            options.compiler,
            cfilename,
            options.args if options.args else '-O2 -o{}'.format(name),
            '-DVERBOSE_EXECUTION' if options.verbose else ''
        ])
    except Exception as e:
        die(options.filename, e)

def llvm(options):
    '''Parse and compile source file to LLVM'''
    checkLLVM()
    from src.genllvm import buildModule

    try:
        # Parse file into mapping of labels to instructions
        name = getName(options.filename)
        maxstack, source = parse(options.filename)

        # Generate and write LLVM IR
        module = buildModule(name, source, maxstack)
        irFilename = name + '.ll'
        with open(irFilename, 'w') as stream:
            stream.write(str(module))

        # Generate assembly with llc
        asmFilename = name + '.s'
        shell([
            'llc',
            irFilename,
            '-o ' + asmFilename,
            '-O' + options.O,
        ])

        # Assemble executable with clang
        # GCC doesn't like the assembly llc produces
        shell([
            'clang',
            asmFilename,
            '-o ' + name,
        ])
    except Exception as e:
        die(options.filename, e)

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Hugo interpreter and compiler',
    )

    subparsers = parser.add_subparsers(
        description='Run the Hugo interpreter or compiler',
        help='Available subcommands',
    )

    # Subcommand for generating llvm
    llvmparser = subparsers.add_parser(
        'gen-llvm',
        description='Compile source to LLVM IR and use llc and clang to produce executable',
        help='Compile source to LLVM IR and use llc and clang to produce executable',
    )
    llvmparser.add_argument(
        'filename',
        metavar='FILENAME',
        help='Source file to compile',
    )
    llvmparser.add_argument(
        '-O',
        choices='0123',
        default='2',
        help='Optimization level for llc. Default is -O2',
    )
    llvmparser.set_defaults(command=llvm)

    # Subcommand for compilation
    cparser = subparsers.add_parser(
        'gen-c',
        description='Compile source to C and use C-compiler to produce executable',
        help='Compile source to C and use C-compiler to produce executable',
    )
    cparser.add_argument(
        'filename',
        metavar='FILENAME',
        help='Source file to compile',
    )
    cparser.add_argument(
        '--compiler',
        default='clang',
        help='Specify another C-compiler. Default compiler is clang.'
    )
    cparser.add_argument(
        '--args',
        metavar='ARGS',
        default=None,
        help="Arguments to pass on to compiler. Default is just '-O2 -oBaseName'",
    )
    cparser.add_argument(
        '--verbose',
        action='store_true',
        help='Print current expression and stack during execution',
    )
    cparser.set_defaults(command=compile)

    # Subcommand for interpretation
    rparser = subparsers.add_parser(
        'run',
        description='Interpret Hugo source directly',
        help='Interpret Hugo source directly',
    )
    rparser.add_argument(
        'filename',
        metavar='FILENAME',
        help='Source file to interpret',
    )
    rparser.add_argument(
        '--verbose',
        action='store_true',
        help='Print current expression and stack during execution',
    )
    rparser.set_defaults(command=interpret)

    options = parser.parse_args()
    if hasattr(options, 'command'):
        options.command(options)
    else:
        parser.error('Must specify compile or run')

if __name__ == '__main__':
    main()

