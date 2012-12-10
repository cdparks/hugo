# Hugo

## Overview

**Hugo** **U**ses **G**otos **O**nly!

**Hugo** is _The Language of the Future!_

**Hugo** is for programmers who feel _too constrained_ by the implicit sequencing of more _pedestrian_ programming languages!

**Hugo** is designed and developed by your friends at **LAMBDA HEAVY INDUSTRIES&copy;™**

## A Short Example
---
The shortest non-terminating Hugo program is:

	0

Our trained research scientists at **LAMBDA HEAVY INDUSTRIES&copy;™** call this _Looping Nullary Zero Combinator Prime_.[^1]
	
## Syntax
---

A Hugo program is a set of statements.

1. A statement begins with a decimal number. This is the statement's label. Lines that do not begin with decimal number are comments.
2. A statement is an expression in reverse Polish notation. The label is a part of the expression.
3. A statement evaluates to the label of the next statement to execute. If no such statement exists, execution halts.

With that knowledge in hand, we can better explain how _Looping Nullary Zero Combinator Prime_ works:

	Start at label 0, evalute 0 (to 0), and jump to 0.
	0

A slightly more interesting program echos input to the screen until EOF is reached:

	Read a value into memory cell 0
  	0 1 , 0 $ +
  	
  	Compare value to -1
  	1 1 0 & 0 1 - = + +
  
  	If value is not -1, print it and jump to beginning
  	2 2 0 & . -
  	
 	Otherwise, halt
 	3 1 +
 	
This program is called _echo_.[^2]

Since every statement is both a label and a goto, the statements comprising _echo_ can be put in any order.
	
  	Compare value to -1
  	1 1 0 & 0 1 - = + +
  	
 	Otherwise, halt
 	3 1 +
 	
  	If value is not -1, print it and jump to beginning
  	2 2 0 & . -
  	
	Read a value into memory cell 0
  	0 1 , 0 $ +
  	
At **LAMBDA HEAVY INDUSTRIES&copy;™**, we have found this to be a huge win for programmer ~~productivity~~ ~~satisfaction~~ job retention.

## Reverse Polish Notation Operators
---

As _echo_ hinted above, the following RPN operators are supported:

Name      | Syntax  | Effect
----------|---------|-------
`literal` | `X`     | `push(X)`
`save`    | `X Y $` | `Y = pop(); X = pop(); mem[Y] = X;`
`load`    | `X &`   | `push(mem[X])`
`read`    | `,`     | `push(getchar())`
`write`   | `X .`   | `putchar(pop())`
`add`     | `X Y +` | `Y = pop(); X = pop(); push(X + Y)`
`sub`     | `X Y -` | `Y = pop(); X = pop(); push(X - Y)`
`eql`     | `X Y =` | `Y = pop(); X = pop(); push(X == Y)`

## Execution Details
---

The Hugo execution model may use any appropriate word size[^3] but should have at least 1048576 memory cells.[^4]

When `read` encounters EOF, the value pushed to the stack should be -1. 

Hugo can be interpreted or compiled, but should not be orally consumed in any significant quantity.[^5]

## Completeness
---

According to our trained research scientists, Hugo is Turing Complete. Included in the reference implementation is a Hugo program `bf.hugo` which implements an interpreter for a [programming language with an extremely rude name](http://en.wikipedia.org/wiki/Brainfuck)[^6]. Since the rudely-named language has been proven Turing Complete, and Hugo can implement it, we can say that Hugo is Turing Complete.[^7]

## Reference Implementation
---

Here at **LAMBDA HEAVY INDUSTRIES&copy;™**, our trained research scientists are so committed to theoretical purity, that they have elected _not_ to implement Hugo. We have therefore contracted with a local high school student named Marvin[^8] to produce a reference implementation.

Marvin's implementation (hereafter referred to as "Marvin's Implementation") includes an interpreter and a compiler.

The following commands show how to run `bf.hugo`:

	# Via interpretation
	$ python hugo.py run examples/bf.hugo < examples/hello.bf
	Hello World!
	
	# Via compilation
	$ python hugo.py compile examples/bf.hugo
	$ ./examples/bf < examples/hello.bf
	Hello World!
		
For more information, run:

	$ python hugo.py --help
	$ python hugo.py run --help
	$ python hugo.py compile --help

## Final Remarks
---

**LAMBDA HEAVY INDUSTRIES&copy;™** is copyright and trademark of **LAMBDA HEAVY INDUSTRIES&copy;™**.

Hugo and "Marvin's Implementation" were created by [Chris Parks](mailto:christopher.daniel.parks@gmail.com)[^9] for the PLT Games [Turing Tarpit Competition](http://www.pltgames.com/competition/2012/12) of December 2012.[^10]

This document and all associated code is released under the [MIT license](http://opensource.org/licenses/MIT).

[^1]: Patents pending, all rights reserved.

[^2]: _echo_ was named by a different, less excitable group of trained research scientists.

[^3]: 37 bits, for example, would be inappropriate. Negative sizes would be inappropriate, offensive, and impractical.

[^4]: For reasons why, see Guyton and Hall Textbook of Medical Physiology, 12th edition. The short answer is "_performance_".

[^5]: See footnote 4.

[^6]: Our trained research scientists were positively aghast.

[^7]: Proof by sufficiently complicated example.

[^8]: Not his real name.

[^9]: Who is emphatically not a high school student or known to anyone as Marvin.

[^10]: Not that that's any kind of excuse.

