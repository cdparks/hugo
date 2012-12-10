# encoding: utf-8
from __future__ import unicode_literals, print_function

import sys
import os
import subprocess

from src.parse import parse
from src.vm import run
from src.gen import gen

def interpret(options):
    for filename in options.filenames:
        try:
            _, source = parse(filename)
            run(source, options.verbose)
        except Exception as e:
            print("{}: {}: {}".format(filename, e.__class__.__name__, e))
            sys.exit(1)

def compile(options):
    for filename in options.filenames:
        try:
            maxstack, source = parse(filename)
            name, ext = os.path.splitext(filename)
            if ext != '.hugo':
                raise Exception("Expected extension .hugo on filename '{}'.".format(filename))
            cfilename = name + '.c'
            with open(cfilename, 'w') as stream:
                stream.write(gen(maxstack, source))
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
            subprocess.call(' '.join(command), shell=True)
        except Exception as e:
            print("{}: {}: {}".format(filename, e.__class__.__name__, e))
            sys.exit(1)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Hugo interpreter and compiler',
    )

    subparsers = parser.add_subparsers(
        description='Run the Hugo interpreter or compiler',
        help='Available subcommands',
    )

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

