"""
@copyright: 2010 - 2018 by Pauli Rikula <pauli.rikula@gmail.com>

@license: MIT <http://www.opensource.org/licenses/mit-license.php>


"""

from .operation import FreezedOperation, OperationsSet
from .category import Category
from .processed_term import IPrintableTerm, CategoryOperations, ProcessedTerm

from .term import(
    IEquationTerm,
    EquationTerm,
    Identity,
    Zero,
    Adder)



from .analysis import (
    TermIs,
    Get,
    Equal,
    EquationMap,
    simplify,
    get_route)

def debug(source, sink):
    print(source, '->', sink)

def get_I_and_O(operator): return Identity(operator), Zero(operator)

def from_operator(operation=debug):
    """
# python-category-equations

With the tools provided here you can create category like equations for the given operator.
On the equations the underlaying '+' and '-' operations are basic set operations
called union and discard  and the multiplication operator '*' connects sources to sinks.
The equation system also has a Identity 'I' term and zerO -like termination term 'O'.
For futher details go https://en.wikipedia.org/wiki/Category_(mathematics)#Definition

## Usage


Here our connector operation is print function called 'debug' which
prints an arrow between two objects:

    >>> debug('a', 'b')
    a -> b

    >>> debug('b', 'a')
    b -> a

    >>> debug('a', 'a')
    a -> a

Get I and O singletons and class C, which use previously defined debug -function.

    >>> I, O, C = from_operator(debug)
    >>> I == I
    True
    >>> O == I
    False
    >>> C(1)
    C(1)

The items do have differing sinks and sources:

    >>> I.sinks
    {I}
    >>> I.sources
    {I}

    >>> O.sinks
    set()
    >>> O.sources
    set()

    >>> C(1).sinks
    {1}
    >>> C(1).sources
    {1}


You can write additions also with this notation

    >>> C(1,2) == C(1) + C(2)
    True


The multiplication connects sources to sinks like this:

    >>> (C(1,2) * C(3,4)).evaluate()
    1 -> 3
    1 -> 4
    2 -> 3
    2 -> 4

    >>> (C(3,4) * C(1,2)).sinks
    {3, 4}

    >>> (C(3,4) * C(1,2)).sources
    {1, 2}

Or

    >>> C(1) * C(2, I) == C(1) + C(1) * C(2)
    True

    >>> (C(1) * C(2, I)).evaluate()
    1 -> 2

    >>> (C(1) * C(2, I)).sinks
    {1}

    >>> (C(1) * C(2, I)).sources
    {1, 2}

And writing C(1,2) instead of C(1) + C(2) works with multiplication too:

    >>> C(1,2) * C(3,4) == (C(1) + C(2)) * (C(3) + C(4))
    True

The order inside C(...) does not matter:

    >>> (C(1,2) * C(3,4)) == (C(2,1) * C(4,3))
    True

On the other hand you can not swap the terms like:

    >>> (C(1,2) * C(3,4)) == (C(3,4) * C(1,2))
    False

Because:

    >>> (C(3,4) * C(1,2)).evaluate()
    3 -> 1
    3 -> 2
    4 -> 1
    4 -> 2

The discard operation works like this:

    >>> (C(3,4) * C(1,2) - C(4) * C(1)).evaluate()
    3 -> 1
    3 -> 2
    4 -> 2

But

    >>> (C(3,4) * C(1,2) - C(4) * C(1)) == C(3) * C(1,2) + C(4) * C(2)
    False

Because sinks and sources differ:

    >>> (C(3,4) * C(1,2) - C(4) * C(1)).sinks
    {3}
    >>> (C(3) * C(1,2) + C(4) * C(2)).sinks
    {3, 4}

The right form would have been:

    >>> (C(3,4) * C(1,2) - C(4) * C(1)) == C(3) * C(1,2) + C(4) * C(2) - C(4) * O - O * C(1)
    True


The identity I and zero O work together like usual:

    >>> I * I == I
    True
    >>> O * I * O == O
    True


Identity 'I' works as a tool for equation simplifying.
For example:

    >>> C(1,2) * C(3,4) * C(5) + C(1,2) * C(5) == C(1,2) * ( C(3,4) + I ) * C(5)
    True

Because:

    >>> (C(1,2) * C(3,4) * C(5) + C(1,2) * C(5)).evaluate()
    1 -> 3
    1 -> 4
    1 -> 5
    2 -> 3
    2 -> 4
    2 -> 5
    3 -> 5
    4 -> 5

and

    >>> (C(1,2) * ( C(3,4) + I ) * C(5)).evaluate()
    1 -> 3
    1 -> 4
    1 -> 5
    2 -> 3
    2 -> 4
    2 -> 5
    3 -> 5
    4 -> 5

If two terms have the same middle part you can simplify equations
via terminating loose sinks or sources with O:
For example:

    >>> (C(1) * C(2) * C(4) + C(3) * C(4)).evaluate()
    1 -> 2
    2 -> 4
    3 -> 4

    >>> (C(1) * C(2) * C(4) + O * C(3) * C(4)).evaluate()
    1 -> 2
    2 -> 4
    3 -> 4

    >>> (C(1) * ( C(2) + O * C(3) ) * C(4)).evaluate()
    1 -> 2
    2 -> 4
    3 -> 4

    >>> C(1) * C(2) * C(4) + O * C(3) * C(4) == C(1) * ( C(2) + O * C(3) ) * C(4)
    True


Note that the comparison wont work without the O -term because the sinks differ:

    >>> C(1) * C(2) * C(4) +  C(3) * C(4) == C(1) * ( C(2) + O * C(3) ) * C(4)
    False

## Equation solving and minimizations

The module contains also (quite unefficient) simplify -method, which can be used to expression minimization:

    >>> I, O, C = from_operator(debug)
    >>> m = EquationMap(I, O, C)
    >>> a = C(1) + C(2)
    >>> simplify(a, 300, m)
    (C(1, 2), [C(1) + C(2), C(1, 2)])

    >>> b = C(1) * C(3) + C(2) * C(3)
    >>> simplified, path = simplify(b, 100, m)
    >>> simplified
    C(1, 2) * C(3)
    >>> for p in path:
    ...    print(p)
    C(1) * C(3) + C(2) * C(3)
    (C(1) * I + C(2) * I) * C(3)
    (C(1) + C(2) * I) * C(3)
    (C(1) + C(2)) * C(3)
    C(1, 2) * C(3)


For proofs use the get_route:

    >>> I, O, C = from_operator(debug)
    >>> m = EquationMap(I, O, C)
    >>> a = C(1) * C(3) + C(2) * C(3)
    >>> b = C(1, 2) * C(3)
    >>> shortest, path = get_route(a,b, 100, m)
    >>> for p in path:
    ...    print(p)
    C(1) * C(3) + C(2) * C(3)
    C(1) * C(3) + C(2) * I * C(3)
    (C(1) * I + C(2) * I) * C(3)
    (C(1) + C(2) * I) * C(3)
    (C(1) + C(2)) * C(3)
    C(1, 2) * C(3)


    """

    _I, _O = get_I_and_O(operation)


    def _C(*things):
        return Adder(operator=operation, items=set(things))

    return _I, _O, _C


__all__ = [
    'debug',
    'from_operator',
    'Category',
    'CategoryOperations',
    'IPrintableTerm',
    'ProcessedTerm',
    'IEquationTerm',
    'EquationTerm',
    'Identity',
    'Zero',
    'Adder',
    'TermIs',
    'Get',
    'Equal',
    'EquationMap',
    'simplify',
    'get_route',
    'OperationsSet',
    'FreezedOperation']
