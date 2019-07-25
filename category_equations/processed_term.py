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


class CategoryOperations(enum.Enum):
    """
    >>> for operation in CategoryOperations:
    ...    print(operation.name, operation.value)
    ADD +
    DISCARD -
    ARROW *

    """

    ADD = '+'
    DISCARD = '-'
    ARROW = '*'


class IPrintableTerm(Category, metaclass=abc.ABCMeta):
    @abc.abstractproperty
    def needs_parenthesis_on_print(self) -> bool:
        raise NotImplementedError

class ProcessedTerm:
    """
    ProcessedTerm class is for the book keeping of the term manipulations and not the underlaying category itself

    >>> I, O, C = from_operator(debug)
    >>> a = ProcessedTerm(C('sink'), CategoryOperations.ARROW, C('source') )
    >>> b = ProcessedTerm(C('sink'), CategoryOperations.ARROW, C('source') )
    >>> c = ProcessedTerm(C('sink'), CategoryOperations.ARROW, C('sink') )
    >>> d = ProcessedTerm(C('sink'), CategoryOperations.ADD, C('source') )
    >>> e = ProcessedTerm(C('source'), CategoryOperations.ARROW, C('source') )

    >>> a == b == a == a
    True
    >>> a == c
    False
    >>> a == d
    False
    >>> a == e
    False

    Printouts are simplified like this:

    >>> C(1, 2) * C(1, 2)
    C(1, 2) * C(1, 2)

    >>> C(1, 2) * (C(1) + C(2))
    C(1, 2) * (C(1) + C(2))

    >>> C(1, 2) * (C(1) * C(2))
    C(1, 2) * C(1) * C(2)

    >>> (C(1) + C(2)) * (C(1) * C(2))
    (C(1) + C(2)) * C(1) * C(2)

    >>> (C(1) * C(2)) * (C(1) * C(2))
    C(1) * C(2) * C(1) * C(2)

    >>> (C(1) * C(2)) * (C(1) * C(2))
    C(1) * C(2) * C(1) * C(2)


    """

    def __init__(
            self,
            sink: IPrintableTerm = None,
            operation: CategoryOperations = None,
            source: IPrintableTerm = None):
        if None in [sink, operation, source]:
            raise ValueError("these should not be none {}".format([sink, operation, source]))
        self._source = sink
        self._operation = operation
        self._sink = source

    def __str__(self):
        if not self.sink.needs_parenthesis_on_print():
            if not self.source.needs_parenthesis_on_print():
                return "{} {} {}".format(self.sink, self.operation.value, self.source)
            return "{} {} ({})".format(self.sink, self.operation.value, self.source)
        if not self.source.needs_parenthesis_on_print():
            return "({}) {} {}".format(self.sink, self.operation.value, self.source)
        return "({}) {} ({})".format(self.sink, self.operation.value, self.source)

    def __repr__(self):
        return str(self)

    @property
    def sink(self) -> IPrintableTerm:
        return self._source

    @property
    def operation(self) -> CategoryOperations:
        return self._operation

    @property
    def source(self) -> IPrintableTerm:
        return self._sink

    def __eq__(self, other):
        return isinstance(other, ProcessedTerm) and \
            (self.sink, self.operation.value, self.source) == (other.sink, other.operation.value, other.source)

    def __hash__(self):
        return (self.sink, self.operation, self.source).__hash__()

