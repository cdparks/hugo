# encoding: utf-8
from __future__ import unicode_literals, print_function

__all__ = ['gen']

from string import Template

from src.parse import parse
from src.vm import instructions, pExpr

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

prologue = Template('''#include <stdio.h>
static int memory[1024 * 1024];
static int stack[$maxstack];
static size_t sp = 0;

#define PUSH(x) stack[sp++] = (x)
#define POP()   stack[--sp]
#define READ()  PUSH(getchar())
#define WRITE() putchar(POP())
#define SAVE()  x = POP(); memory[x] = POP()
#define LOAD()  x = POP(); PUSH(memory[x])
#define ADD()   y = POP(); x = POP(); PUSH(x + y)
#define SUB()   y = POP(); x = POP(); PUSH(x - y)
#define EQL()   y = POP(); x = POP(); PUSH(x == y)

#ifdef VERBOSE_EXECUTION
void PEXPR(char *expr) {
    fprintf(stderr, "%s\\n", expr);
}
void PSTACK() {
    size_t i;
    for(i = 0; i < sp; ++i) {
        fprintf(stderr, "%d ", stack[i]);
    }
    fprintf(stderr, "\\n");
}
void PNUM(int num) {
    fprintf(stderr, "%4d | ", num);
    PSTACK();
}
void PSYM(char *sym) {
    fprintf(stderr, "%4s | ", sym);
    PSTACK();
}
void PTOS() {
    fprintf(stderr, "     | %d\\n", stack[sp - 1]);
}
#else
#define PEXPR(x)
#define PSTACK(x)
#define PNUM(x)
#define PSYM(x)
#define PTOS(x)
#endif

int main() {
  register int x, y, label = 0;
  while(1) {
    switch(label) {
''')

epilogue = '''default:
        goto halt;
    }
    PTOS();
    label = POP();
  }
halt:
  return 0;
}
'''

class Writer(object):
    '''Wrap a StringIO object for easy code generation'''

    def __init__(self, content=None, level=0, indentstr='  '):
        self.io = StringIO()
        self.level = level
        self.indentstr = indentstr
        if content is not None:
            self.io.write(content)

    def write(self, value):
        '''Append indented value to output stream'''
        self.io.write('{}{}'.format(self.indentstr * self.level, value))
        return self

    def writeln(self, line):
        '''Append indented line to output stream'''
        return self.write(line + '\n')

    def indent(self, levels=1):
        '''Increase indent level'''
        self.level += levels
        return self

    def dedent(self, levels=1):
        '''Decrease indent level'''
        self.level = max(0, self.level - levels)
        return self

    def value(self):
        '''Return complete string content'''
        return self.io.getvalue()

def gen(maxstack, source):
    '''Generate C code from source'''
    out = Writer(prologue.substitute(maxstack=maxstack))
    out.indent(3)

    # Each label and expression will be made into a case
    # statement in the C program's main switch statement.
    for label, expression in sorted(source.items()):
        out.writeln('case {}:'.format(label)).indent()
        out.writeln('PEXPR("{}");'.format(pExpr(expression)))
        for instruction in expression:
            out.writeln(instruction.ccode())
        out.writeln("break;").dedent()
    return out.write(epilogue).value()

