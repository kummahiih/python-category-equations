"""
   @copyright: 2010 - 2018 by Pauli Rikula <pauli.rikula@gmail.com>
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

import copy
import enum
import abc
from typing import Set, List, Callable


class FreezedFunction:
    def __init__(self, fnc, alist=[], adict={}):
        self.fnc = fnc
        self.alist = tuple(alist)
        self.adict = tuple(adict.items())

    def __repr__(self):
        return 'F(%s,%s)'% (self.alist, self.adict)

    def evaluate(self):
        return self.fnc(*self.alist, **dict(self.adict))

    def __eq__(self, other):
        return isinstance(other, FreezedFunction) and \
            self.alist == other.alist and self.adict == other.adict

    def __hash__(self):
        return (self.fnc, self.alist, self.adict).__hash__()

    @staticmethod
    def sort_key(f_f):
        return (f_f.fnc, f_f.alist, f_f.adict)

def freezed(fnc):
    def _f(*l, **d):
        return FreezedFunction(fnc, l, d)
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

FreezablesSet = Set[FreezedFunction]


class Category(metaclass=abc.ABCMeta):
    
    def __init__(
            self,
            operator: Callable=None,
            sources: Set=None,
            sinks: Set=None,
            operations: FreezablesSet=None):
            
        if None in [operator, sources, sinks, operations]:
            raise ValueError("These should not be none: {}".format([operator, sources, sinks, operations]))
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
    def operations(self) -> Set[FreezedFunction]:
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
        return self.sinks == other.sinks and self.sources == other.sources and self.operations == other.operations

    @abc.abstractclassmethod
    def is_identity(self) -> bool:
        raise NotImplemented()

    @abc.abstractclassmethod
    def is_zero(self)  -> bool:
        raise NotImplemented()
    
    def evaluate(self):
        operations = sorted(self.operations, key = FreezedFunction.sort_key)
        
        for frozen in operations:
            frozen.evaluate()

    @abc.abstractclassmethod
    def __str__(self) -> str:
        raise NotImplemented()

    def __repr__(self):
        return str(self)


class EquationTerm(Category):
    def __add__(self, anext: Category) -> Category:
        result = MediateTerm(
            operator=self.operator,
            sinks=self.sinks.union(anext.sinks),
            sources=self.sources.union(anext.sources),
            operations=self.operations.union(anext.operations),
            processed_term=ProcessedTerm(self, CategoryOperations.ADD, anext))
        return result

    def __sub__(self, anext: Category) -> Category:
        result = MediateTerm(
            operator=self.operator,
            sinks=_Set_operations.discard_b_from_a(self.sinks, anext.sinks),
            sources=_Set_operations.discard_b_from_a(self.sources, anext.sources),
            operations=_Set_operations.discard_b_from_a(self.operations, anext.operations),
            processed_term=ProcessedTerm(self, CategoryOperations.DISCARD, anext))
        return result

    def __mul__(self, anext: Category) -> Category:
        if anext.is_identity():
            return MediateTerm(
                sinks=self.sinks,
                sources=self.sources,
                operations=self.operations,
                operator=anext.operator,
                processed_term = ProcessedTerm(self, CategoryOperations.ARROW, anext))
                
        if anext.is_zero():
            return MediateTerm(
                sinks=self.sinks,
                sources=set(),
                operations=self.operations,
                operator=anext.operator,
                processed_term = ProcessedTerm(self, CategoryOperations.ARROW, anext))
                
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
        result = MediateTerm(
            operator=anext.operator,
            sinks=new_sinks,
            sources=new_sources,
            operations=operations,
            processed_term = ProcessedTerm(self, CategoryOperations.ARROW, anext))
        return result
    

class ProcessedTerm:
    def __init__(self, source: Category=None, operation: CategoryOperations=None, sink: Category=None):
        if None in [source, operation, sink]:
            raise ValueError("these should not be none {}".format([source, operation, sink]))
        self._source = source
        self._operation = operation
        self._sink = sink
    
    def __str__(self):
        return "({}) {} ({})".format(self.source, self.operation.value, self.sink)
    
    @property
    def source(self):
        return self._source
   
    @property
    def operation(self):
        return self._operation
       
    @property
    def sink(self):
        return self._sink


class Identity(EquationTerm):
    def __init__(self, operator:Callable=None):
        super().__init__(
            sources=set([self]),
            sinks=set([self]),
            operations=set([]),
            operator=operator)

    def __mul__(self, anext: Category) -> Category:
        return MediateTerm(
            sinks=anext.sinks,
            sources=anext.sources,
            operations=anext.operations,
            operator=anext.operator,
            processed_term = ProcessedTerm(self, CategoryOperations.ARROW, anext))

    def __str__(self):
        return 'I'
        
    def is_identity(self) -> bool:
        return True

    def is_zero(self) -> bool:
        return False



class Zero(EquationTerm):
    def __init__(self, operator: Callable=None):
        super().__init__(
            sources=set([]),
            sinks=set([]),
            operations=set([]),
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
            processed_term = ProcessedTerm(self, CategoryOperations.ARROW, anext))

    def __str__(self) -> str:
        return 'O'



def get_I_and_O(operator): return Identity(operator), Zero(operator)

class Adder(EquationTerm):
    def __init__(self, items: Set[object], operator=None):
        sources=set([])
        sinks=set([])
        operations=set([])
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
            operator: Callable=None,
            sources: Set=None,
            sinks: Set=None,
            operations: FreezablesSet=None,
            processed_term: ProcessedTerm=None):        

        super().__init__(
            sources=sources,
            sinks=sinks,
            operations=operations,
            operator=operator)
        if processed_term is None:
            raise ValueError('processed_term should not be None')
        self._processed_term = processed_term

    @property
    def processed_term(self) -> ProcessedTerm:
        return self._processed_term

    def __str__(self) -> str:
        return str(self.processed_term)

    def is_identity(self) -> bool:
        return False
        
    def is_zero(self) -> bool:
        return False







def from_operator(operation=debug):
    """

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

If two terms have the same middle part you can simplify equations via terminating loose sinks or sources with O:
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

    operator = freezed(operation)

    _I, _O = get_I_and_O(operator)


    def _C(*things):
        return Adder(operator=operator, items=set(things))

    return _I, _O, _C

if __name__ == '__main__':
    import doctest
    doctest.testmod()

    I, O, C = from_operator()

