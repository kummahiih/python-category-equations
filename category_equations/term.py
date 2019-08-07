"""
   @copyright: 2010 - 2019 by Pauli Rikula <pauli.rikula@gmail.com>
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

import copy
import enum
import abc
from typing import Set, List, Callable

from .operation import FreezedOperation, OperationsSet
from .category import Category
from .processed_term import CategoryOperations, ProcessedTerm, IPrintableTerm



class IEquationTerm(IPrintableTerm, metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def processed_term(self) -> ProcessedTerm:
        raise NotImplementedError

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
    """
    >>> I, O, C = from_operator(debug)

    >>> I == I
    True
    
    >>> I == O
    False
    
    >>> I == (I*I)
    True
    
    >>> I == (I+I)
    True
    
    >>> I ==(I-I)
    False

    >>> I == (I-O)
    True
    
    >>> I ==(O*I)
    False
    
    >>> I ==(O+I)
    True
    
    >>> I ==(O-I)
    False
    
    >>> I ==(O+O)
    False
    
    """

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

    def needs_parenthesis_on_print(self) -> bool:
        return False


class Zero(EquationTerm):
    """
    >>> I, O, C = from_operator(debug)

    >>> (C(1) - C(1)) == O
    True

    >>> O ==(I)
    False
    
    >>> O ==(O)
    True
    
    >>> O ==(I*I)
    False
    
    >>> O ==(I+I)
    False
    
    >>> O ==(I-I)
    True

    >>> O ==(I-O)
    False
    
    >>> O ==(O*I)
    False
    
    >>> O ==(O+I)
    False
    
    >>> O ==(O-I)
    True
    
    >>> O ==(O+O)
    True

    """

    def __init__(self, operator: Callable = None):
        super().__init__(
            sources=set([]),
            sinks=set([]),
            operations=OperationsSet([], operator=operator),
            operator=operator)

    def __mul__(self, anext: Category) -> Category:
        return MediateTerm(
            sinks=set([]),
            sources=anext.sources,
            operations=anext.operations,
            operator=anext.operator,
            processed_term=ProcessedTerm(self, CategoryOperations.ARROW, anext))

    def __str__(self) -> str:
        return 'O'

    def is_identity(self) -> bool:
        return False

    def is_zero(self) -> bool:
        return True

    def needs_parenthesis_on_print(self) -> bool:
        return False



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

    def combine(self, adder):
        if not isinstance(adder, Adder) or self.operator != adder.operator:
            raise ValueError
        items = set()
        items.update(self._items)
        items.update(adder._items)
        return Adder(items = items, operator=self.operator)

    def reduce_to_additions(self):
        if len(self._items) == 0:
            return Adder(items=set(), operator=self.operator)
        items = list(self._items)
        items.sort()
        retuned = Adder(items=set([items[0]]), operator=self.operator)
        for item in items[1:]:
            retuned += Adder(items=set([item]), operator=self.operator)
        return retuned

    def needs_parenthesis_on_print(self) -> bool:
        return False



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

    def needs_parenthesis_on_print(self) -> bool:
        return self.processed_term.operation in [CategoryOperations.ADD, CategoryOperations.DISCARD]

