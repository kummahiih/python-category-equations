"""
   @copyright: 2010 - 2018 by Pauli Rikula <pauli.rikula@gmail.com>
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

import copy

class Freezed_fnc:
    def __init__(self, fnc, alist=[], adict={}):
        self.fnc = fnc
        self.alist = tuple(alist)
        self.adict = tuple(adict.items())

    def __repr__(self):
        return 'F %s %s' % (self.alist, self.adict)

    def evaluate(self):
        return self.fnc(*self.alist, **dict(self.adict))

    def __eq__(self, other):
        return isinstance(other, Freezed_fnc) and \
            self.alist == other.alist and self.adict == other.adict

    def __hash__(self):
        return (self.fnc, self.alist, self.adict).__hash__()

    @staticmethod
    def sort_key(f_f):
        return (f_f.fnc, f_f.alist, f_f.adict)

def freezed(fnc):
    def _f(*l, **d):
        return Freezed_fnc(fnc, l, d)
    return _f

def debug(a, b):
    print(a, '->', b)

class _Set_operations:

    @staticmethod
    def smaller_and_bigger(a, b):
        if len(a) <= len(b):
            return a, b
        return b, a

    @staticmethod
    def discard_b_from_a(a, b):
        c = copy.copy(a)
        for key in b:
            c.discard(key)
        return c


class Identity:
    def __init__(self, operator=None):
        self.sources = set([self])
        self.sinks = set([self])
        self.operations = set([])
        self.operator = operator

    def __hash__(self):
        return str(self).__hash__()

    def __lt__(self, other):
        return str(self).__lt__(str(other))

    def __eq__(self, other):
        return str(self).__eq__(str(other))

    def is_identity(self):
        return True
    def is_zero(self):
        return False

    def __add__(self, anext):
        result = Container(
            operator=self.operator,
            items=[],
            sinks=self.sinks.union(anext.sinks),
            sources=self.sources.union(anext.sources),
            operations=self.operations.union(anext.operations),
            processeditems=[self, "'+'", anext])
        return result

    def __sub__(self, anext):
        result = Container(
            operator=self.operator,
            items=[],
            sinks=_Set_operations.discard_b_from_a(self.sinks, anext.sinks),
            sources=_Set_operations.discard_b_from_a(self.sources, anext.sources),
            operations=_Set_operations.discard_b_from_a(self.operations, anext.operations),
            processeditems=[self, "'-'", anext])
        return result

    def __mul__(self, anext):
        result = copy.copy(anext)
        result.processeditems = [self, "'*'", anext]
        return anext

    def evaluate(self):
        operations = sorted(self.operations, key = Freezed_fnc.sort_key)
        
        for frozen in operations:
            frozen.evaluate()

    def __str__(self):
        return 'I'

    def __repr__(self):
        return str(self)


class Zero(Identity):
    def __init__(self, operator=None):
        self.sources = set([])
        self.sinks = set([])
        self.operations = set([])
        self.operator = operator

    def is_identity(self):
        return False
    def is_zero(self):
        return True
    def __mul__(self, anext):
        if anext.is_identity():
            return self
        result = copy.copy(anext)
        result.sinks = set([])
        result.processeditems = [self, "'*'", anext]
        return result

    def __str__(self):
        return 'O'
    def __repr__(self):
        return str(self)

def get_I_and_O(operator): return Identity(operator), Zero(operator)


class Container(Identity):
    def __init__(
            self,
            operator=None,
            items=[],
            sources=[],
            sinks=[],
            operations=[],
            processeditems=[]):


        self.sources = set(sources)
        self.sinks = set(sinks)
        self.operations = set(operations)

        self.operator = operator

        for item in items:
            if isinstance(item, Identity):
                self.sources.update(item.sources)
                self.sinks.update(item.sinks)
                self.operations.update(item.operations)
            else:
                self.sources.add(item)
                self.sinks.add(item)
        self.processeditems = list(items) + processeditems

    def __str__(self):
        return "C(%s)" % ",".join(map(str, self.processeditems))

    def is_identity(self):
        return False
    def is_zero(self):
        return len(self.sinks) == 0 and len(self.sources) == 0 and len(self.operations) == 0

    def __mul__(self, anext):
        if anext.is_identity():
            return self
        if anext.is_zero():
            new = copy.copy(self)
            new.sources = set([])
            return new

        new_operations = set([])
        for source in self.sources:
            if isinstance(source, Identity):
                if source.is_identity() or source.is_zero():
                    continue
            for sink in anext.sinks:
                if isinstance(sink, Identity):
                    if sink.is_identity() or sink.is_zero():
                        continue
                #print source,'---', sink
                new_operations.add(self.operator(source, sink))

        new_sources = set([])
        for v in anext.sources:
            if isinstance(v, Identity) and v.is_identity():
                new_sources.update(self.sources)
            elif isinstance(v, Identity) and v.is_zero():
                continue
            else:
                new_sources.add(v)

        new_sinks = set([])
        for v in self.sinks:
            if isinstance(v, Identity) and v.is_identity():
                new_sinks.update(anext.sinks)
            elif isinstance(v, Identity) and v.is_zero():
                continue
            else:
                new_sinks.add(v)

        operations = self.operations.union(anext.operations).union(new_operations)
        #print operations
        #print len(operations)
        result = Container(
            operator=anext.operator,
            items=set([]),
            sinks=new_sinks,
            sources=new_sources,
            operations=operations,
            processeditems=[self, "'*'", anext])
        return result



def from_operator(operation=debug):
    """Category like equations in which
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

    """

    operator = freezed(operation)

    _I, _O = get_I_and_O(operator)


    def _C(*things):
        return Container(operator, list(things), [], [], [], [])

    return _I, _O, _C

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    I, O, C = from_operator()

