# encoding: utf-8
from __future__ import unicode_literals, print_function

__all__ = ['gen']

from string import Template

from src.parse import parse
from src.vm import operators

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
    fprintf(stderr, "goto %s\\n", expr);
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
void PTOP() {
    fprintf(stderr, "     | %d\\n", stack[sp - 1]);
}
#else
#define PEXPR(x)
#define PSTACK(x)
#define PNUM(x)
#define PSYM(x)
#define PTOP(x)
#endif

int main() {
  register int x, y, label = 0;
  while(1) {
    switch(label) {
''')

epilogue = '''default:
        goto halt;
    }
    PTOP();
    label = POP();
  }
halt:
  return 0;
}
'''


class Writer(object):
    def __init__(self, content=None, level=0, indentstr='  '):
        self.io = StringIO()
        self.level = level
        self.indentstr = indentstr
        if content is not None:
            self.io.write(content)

    def write(self, value):
        self.io.write('{}{}'.format(self.indentstr * self.level, value))
        return self

    def writeln(self, line):
        return self.write(line + '\n')

    def indent(self, levels=1):
        self.level += levels
        return self

    def dedent(self, levels=1):
        self.level = max(0, self.level - levels)
        return self

    def value(self):
        return self.io.getvalue()

def gen(maxstack, source):
    out = Writer(prologue.substitute(maxstack=maxstack))
    out.indent(3)
    for label, expression in sorted(source.items()):
        out.writeln('case {}:'.format(label)).indent()
        out.writeln('PEXPR("{}");'.format(' '.join(map(str, expression))))
        for word in expression:
            function = operators.get(word)
            if function is not None:
                out.writeln('PSYM("{}"); {}();'.format(function.sym, function.__name__.upper()))
            else:
                out.writeln('PNUM({0}); PUSH({0});'.format(word))
        out.writeln("break;").dedent()
    return out.write(epilogue).value()

