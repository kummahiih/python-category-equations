# python-category-equations

Create category like equations for the given operator in which
the underlaying '+' and '-' operations are basic set operations called union and discard.
The multiplication operator '*' connects sources to sinks. The equation system also has
a Identity 'I' and zerO 'O' terms. For futher details search 'category theory'
from the Wikipedia and do your own maths.

Here our connector operation is print function called 'debug'

    >>> debug('a', 'b')
    a -> b

Get I and O singletons and class C, which use previously defined debug -function.

    >>> I, O, C = from_operator(debug)
    >>> I
    I
    >>> O
    O
    >>> I * I
    I
    >>> O * I
    O
    >>> I * O
    O

The multiplication connects sources to sinks like this:

    >>> (C(1,2) * C(3,4)).evaluate()
    1 -> 3
    1 -> 4
    2 -> 3
    2 -> 4

The identity I works like usual:

    >>> I * C(1)
    C(1)

    >>> C(1) * I
    C(1)

Zero is a bit trickier:

    >>> C(1) * O
    C(1)

But:

    >>> ((C(1) * O) * C(2)).evaluate()

See, no debug prints, no connections being made.
The 'O' works like a terminator, if you need one.

Identity 'I' works as a tool for equation simplifying.
For example use see these two equations:

    >>> (C(1,2) * C( C(3,4), I ) * C(5)).evaluate()
    1 -> 3
    1 -> 4
    1 -> 5
    2 -> 3
    2 -> 4
    2 -> 5
    3 -> 5
    4 -> 5

    >>> (C(1,2) * C(3,4) * C(5) + C(1,2) * C(5)).evaluate()
    1 -> 3
    1 -> 4
    1 -> 5
    2 -> 3
    2 -> 4
    2 -> 5
    3 -> 5
    4 -> 5

Just some random examples more:

    >>> C(1) * C(2)
    C(C(1),'*',C(2))

    >>> C(0)*( C(1,2,3)*C(4,5) - C(1,2)*C(4) ) *C(6)
    C(C(C(0),'*',C(C(C(1,2,3),'*',C(4,5)),'-',C(C(1,2),'*',C(4)))),'*',C(6))

    >>> C(1,2) + C(1,4)
    C(C(1,2),'+',C(1,4))

    >>> C(1,2) - C(1,4)
    C(C(1,2),'-',C(1,4))

    >>> C(0)*( C(1,2,3)*C(4,5) - C(1,2)*C(4) ) *C(6)
    C(C(C(0),'*',C(C(C(1,2,3),'*',C(4,5)),'-',C(C(1,2),'*',C(4)))),'*',C(6))


    >>> (C(1,2) * C( C(I), I ) * C(5)).evaluate()
    1 -> 5
    2 -> 5

    >>> C( C(1)* C( O * C(2), C(3), C(4) * O ) * C(5)).evaluate()
    1 -> 3
    1 -> 4
    2 -> 5
    3 -> 5

    >>> (C( C(1)* C( O * C(2), C(3), C(4) * O ) * C(5)) - C(1) * C(3) ).evaluate()
    1 -> 4
    2 -> 5
    3 -> 5


    >>> ( C(0)*( C(1,2,3)*C(4,5) - C(1,2)*C(4) ) *C(6)).evaluate()
    0 -> 3
    1 -> 5
    2 -> 5
    3 -> 4
    3 -> 5
    5 -> 6
