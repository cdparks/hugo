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
    $ python hugo.py compile --help
'''

from __future__ import unicode_literals, print_function

import sys
import os
import subprocess

from src.parse import parse
from src.vm import run
from src.gen import gen

def interpret(options):
    '''Parse and run each file in options.filenames'''
    for filename in options.filenames:
        try:
            maxstack, source = parse(filename)
            run(maxstack, source, options.verbose)
        except Exception as e:
            print("{}: {}: {}".format(filename, e.__class__.__name__, e))
            sys.exit(1)

def compile(options):
    '''Parse and compile each file in options.filenames'''
    for filename in options.filenames:
        try:
            maxstack, source = parse(filename)

            # Do the bare minimum to keep the user from overwriting their source file.
            name, ext = os.path.splitext(filename)
            if ext != '.hugo':
                raise Exception("Expected extension .hugo on filename '{}'.".format(filename))

            # Generate and write C source
            cfilename = name + '.c'
            with open(cfilename, 'w') as stream:
                stream.write(gen(maxstack, source))

            # Compile using default or specified compiler
            command = [
                options.compiler,
                cfilename,
                '-o ' + name,
                '-O' + options.O,
            ]

            if options.g:
                command.append('-g')
            if options.verbose:
                command.append('-DVERBOSE_EXECUTION')

            # Running w/o shell=True seems to confuse ld on OS X
            subprocess.call(' '.join(command), shell=True)
        except Exception as e:
            print("{}: {}: {}".format(filename, e.__class__.__name__, e))
            sys.exit(1)

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Hugo interpreter and compiler',
    )

    subparsers = parser.add_subparsers(
        description='Run the Hugo interpreter or compiler',
        help='Available subcommands',
    )

    # Subcommand for compilation
    cparser = subparsers.add_parser(
        'compile',
        description='Compile source to C and use C-compiler to produce executable',
        help='Compile source to C and use C-compiler to produce executable',
    )
    cparser.add_argument(
        'filenames',
        metavar='FILENAME',
        nargs='+',
        help='Source files to compile',
    )
    cparser.add_argument(
        '-O',
        metavar='LEVEL',
        choices='01234',
        default='0',
        help='Optimization level passed on to the C-compiler',
    )
    cparser.add_argument(
        '-g',
        action='store_true',
        help='Build executable with debug symbols',
    )
    cparser.add_argument(
        '--compiler',
        default='gcc',
        help='Specify another C-compiler. Default compiler is gcc.'
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
        'filenames',
        metavar='FILENAME',
        nargs='+',
        help='Source files to interpret',
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

