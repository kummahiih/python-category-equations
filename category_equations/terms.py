"""
   @copyright: 2010 - 2018 by Pauli Rikula <pauli.rikula@gmail.com>
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

import copy
import enum
import abc
from typing import Set, List, Callable


class FreezedOperation:
    def __init__(self, operator, source, sink):
        self._operator = operator
        self._source = source
        self._sink = sink

    @property
    def operator(self) -> Callable:
        """
        The connecting operator, which is about to connect the source to the sink
        """
        return self._operator

    @property
    def source(self):
        """
        The source, which is waiting for the connection with the sink
        """
        return self._source

    @property
    def sink(self):
        """
        The sink, which is waiting for the connection with the source
        """

        return self._sink


    def __repr__(self):
        return 'F(%s,%s)'% (self.source, self.sink)

    def evaluate(self):
        """
        Connect source to sink via operator
        """
        return self.operator(self.source, self.sink)

    def __eq__(self, other):
        return isinstance(other, FreezedOperation) and \
            (self.operator, self.source, self.sink) == (other.operator, other.source, other.sink)

    def __hash__(self):
        return (self.operator, self.source, self.sink).__hash__()

    @staticmethod
    def sort_key(f_f):
        return (f_f.operator, f_f.source, f_f.sink)


def debug(source, sink):
    print(source, '->', sink)

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


class CategoryOperations(enum.Enum):
    """

    >>> for operation in CategoryOperations:
    ...  print(operation.name, operation.value)
    ADD +
    DISCARD -
    ARROW *

    """
    ADD = '+'
    DISCARD = '-'
    ARROW = '*'


class OperationsSet(set):
    def __init__(self, operations, operator=None):
        if not isinstance(operator, Callable):
            raise ValueError("given operator {} is not Callable".format(operator))
        self.operator = operator
        self.check_operations(operations)
        super().__init__(operations)

    def check_operations(self, operations):
        for operation in operations:
            if not isinstance(operation, FreezedOperation):
                raise ValueError("expected FreezedOperation, got {}".format(type(operation)))
            if operation.operator != self.operator:
                raise ValueError("incompatible operator in given operation")

    def union(self, another):
        self.check_operations(another)
        return OperationsSet(super().union(another), operator=self.operator)

    def discard_all(self, another):
        self.check_operations(another)
        c = OperationsSet(self, operator=self.operator)
        for operation in another:
            c.discard(operation)
        return c

    def add_freezed_operation(self, a, b):
        self.add(FreezedOperation(self.operator, a, b))

    @property
    def as_sorted_list(self):
        """
        Converts the set to a sorted list
        """
        return sorted(self, key=FreezedOperation.sort_key)


class Category(metaclass=abc.ABCMeta):
    def __init__(
            self,
            operator: Callable = None,
            sources: Set = None,
            sinks: Set = None,
            operations: OperationsSet = None):

        if None in [operator, sources, sinks, operations]:
            raise ValueError("These should not be none: {}".format(
                [operator, sources, sinks, operations]))
        if not isinstance(operations, OperationsSet):
            raise ValueError("expected OperationsSet, got {}".format(type(operations)))
        self._operator = operator
        self._sources = sources
        self._sinks = sinks
        self._operations = operations

    @property
    def operator(self) -> Callable:
        return self._operator

    @property
    def sources(self) -> Set:
        return self._sources

    @property
    def sinks(self) -> Set:
        return self._sinks

    @property
    def operations(self) -> OperationsSet:
        return self._operations

    def __hash__(self):
        return str(self).__hash__()

    def __lt__(self, other):
        return str(self).__lt__(str(other))

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Category):
            return False
        if self.operator != other.operator:
            return False
        return self.sinks == other.sinks and \
            self.sources == other.sources and \
            self.operations == other.operations

    @abc.abstractclassmethod
    def is_identity(self) -> bool:
        raise NotImplementedError

    @abc.abstractclassmethod
    def is_zero(self)  -> bool:
        raise NotImplementedError

    def evaluate(self):
        for frozen in self.operations.as_sorted_list:
            frozen.evaluate()

    @abc.abstractclassmethod
    def __str__(self) -> str:
        raise NotImplementedError

    def __repr__(self):
        return str(self)


class ProcessedTerm:
    """
    >>> I, O, C = from_operator(debug)
    >>> a = ProcessedTerm(C('source'), CategoryOperations.ARROW, C('sink') )
    >>> b = ProcessedTerm(C('source'), CategoryOperations.ARROW, C('sink') )
    >>> c = ProcessedTerm(C('source'), CategoryOperations.ARROW, C('source') )
    >>> d = ProcessedTerm(C('source'), CategoryOperations.ADD, C('sink') )
    >>> e = ProcessedTerm(C('sink'), CategoryOperations.ARROW, C('sink') )
    
    >>> a == b == a == a
    True
    >>> a == c
    False
    >>> a == d
    False
    >>> a == e
    False

    """
    def __init__(
            self,
            source: Category = None,
            operation: CategoryOperations = None,
            sink: Category = None):
        if None in [source, operation, sink]:
            raise ValueError("these should not be none {}".format([source, operation, sink]))
        self._source = source
        self._operation = operation
        self._sink = sink

    def __str__(self):
        return "({}) {} ({})".format(self.source, self.operation.value, self.sink)

    def __repr__(self):
        return str(self)

    @property
    def source(self):
        return self._source

    @property
    def operation(self) -> CategoryOperations:
        return self._operation

    @property
    def sink(self):
        return self._sink

    def __eq__(self, other):
        return isinstance(other, ProcessedTerm) and \
            (self.source, self.operation.value, self.sink) == (other.source, other.operation.value, other.sink)

    def __hash__(self):
        return (self.source, self.operation, self.sink).__hash__()


class IEquationTerm(Category, metaclass=abc.ABCMeta):

    @abc.abstractproperty
    def processed_term(self) -> ProcessedTerm:
        raise NotImplementedError


class EquationTerm(IEquationTerm):

    def __init__(self, processed_term: ProcessedTerm = None, **rest):
        self._processed_term = processed_term
        super().__init__(**rest)

    @property
    def processed_term(self) -> ProcessedTerm:
        return self._processed_term

    def __add__(self, anext: Category) -> IEquationTerm:
        result = MediateTerm(
            operator=self.operator,
            sinks=self.sinks.union(anext.sinks),
            sources=self.sources.union(anext.sources),
            operations=self.operations.union(anext.operations),
            processed_term=ProcessedTerm(self, CategoryOperations.ADD, anext))
        return result

    def __sub__(self, anext: Category) -> IEquationTerm:
        result = MediateTerm(
            operator=self.operator,
            sinks=_Set_operations.discard_b_from_a(self.sinks, anext.sinks),
            sources=_Set_operations.discard_b_from_a(self.sources, anext.sources),
            operations=self.operations.discard_all(anext.operations),
            processed_term=ProcessedTerm(self, CategoryOperations.DISCARD, anext))
        return result

    def __mul__(self, anext: Category) -> IEquationTerm:
        if anext.is_identity():
            return MediateTerm(
                sinks=self.sinks,
                sources=self.sources,
                operations=self.operations,
                operator=anext.operator,
                processed_term=ProcessedTerm(self, CategoryOperations.ARROW, anext))

        if anext.is_zero():
            return MediateTerm(
                sinks=self.sinks,
                sources=set(),
                operations=self.operations,
                operator=anext.operator,
                processed_term=ProcessedTerm(self, CategoryOperations.ARROW, anext))

        new_operations = OperationsSet([], operator=self.operator)
        for source in self.sources:
            if isinstance(source, Identity):
                if source.is_identity() or source.is_zero():
                    continue
            for sink in anext.sinks:
                if isinstance(sink, Identity):
                    if sink.is_identity() or sink.is_zero():
                        continue
                #print source,'---', sink
                new_operations.add_freezed_operation(source, sink)

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
        result = MediateTerm(
            operator=anext.operator,
            sinks=new_sinks,
            sources=new_sources,
            operations=operations,
            processed_term=ProcessedTerm(self, CategoryOperations.ARROW, anext))
        return result


class Identity(EquationTerm):

    def __init__(self, operator: Callable = None):
        super().__init__(
            sources=set([self]),
            sinks=set([self]),
            operations=OperationsSet([], operator=operator),
            operator=operator)

    def __mul__(self, anext: Category) -> Category:
        return MediateTerm(
            sinks=anext.sinks,
            sources=anext.sources,
            operations=anext.operations,
            operator=anext.operator,
            processed_term=ProcessedTerm(self, CategoryOperations.ARROW, anext))

    def __str__(self):
        return 'I'

    def is_identity(self) -> bool:
        return True

    def is_zero(self) -> bool:
        return False


class Zero(EquationTerm):

    def __init__(self, operator: Callable = None):
        super().__init__(
            sources=set([]),
            sinks=set([]),
            operations=OperationsSet([], operator=operator),
            operator=operator)

    def is_identity(self) -> bool:
        return False

    def is_zero(self) -> bool:
        return True

    def __mul__(self, anext: Category) -> Category:
        return MediateTerm(
            sinks=set([]),
            sources=anext.sources,
            operations=anext.operations,
            operator=anext.operator,
            processed_term=ProcessedTerm(self, CategoryOperations.ARROW, anext))

    def __str__(self) -> str:
        return 'O'


class Adder(EquationTerm):

    def __init__(self, items: Set[object], operator = None):
        sources = set([])
        sinks = set([])
        operations = OperationsSet([], operator=operator)
        self._items = items

        for item in items:
            if isinstance(item, Identity):
                sources.update(item.sources)
                sinks.update(item.sinks)
                operations.update(item.operations)
            else:
                sources.add(item)
                sinks.add(item)

        super().__init__(
            sources=sources,
            sinks=sinks,
            operations=operations,
            operator=operator)

    def is_identity(self) -> bool:
        return False

    def is_zero(self) -> bool:
        return False

    def __str__(self):
        return "C({})".format(", ".join(map(str, self._items)))


class MediateTerm(EquationTerm):

    def __init__(
            self,
            operator: Callable = None,
            sources: Set = None,
            sinks: Set = None,
            operations: OperationsSet = None,
            processed_term: ProcessedTerm = None):
        if processed_term is None:
            raise ValueError('processed_term should not be None')
        super().__init__(
            sources=sources,
            sinks=sinks,
            operations=operations,
            operator=operator,
            processed_term=processed_term)



    def __str__(self) -> str:
        return str(self.processed_term)

    def is_identity(self) -> bool:
        return False

    def is_zero(self) -> bool:
        return False


def get_I_and_O(operator): return Identity(operator), Zero(operator)

def from_operator(operation=debug):
    """# python-category-equations

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


By combining the two previous examples:

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


    """

    _I, _O = get_I_and_O(operation)


    def _C(*things):
        return Adder(operator=operation, items=set(things))

    return _I, _O, _C

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    I, O, C = from_operator()

