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
            source: IPrintableTerm = None,
            operation: CategoryOperations = None,
            sink: IPrintableTerm = None):
        if None in [source, operation, sink]:
            raise ValueError("these should not be none {}".format([source, operation, sink]))
        self._source = source
        self._operation = operation
        self._sink = sink

    def __str__(self):
        if not self.source.needs_parenthesis_on_print():
            if not self.sink.needs_parenthesis_on_print():
                return "{} {} {}".format(self.source, self.operation.value, self.sink)
            return "{} {} ({})".format(self.source, self.operation.value, self.sink)
        if not self.sink.needs_parenthesis_on_print():
            return "({}) {} {}".format(self.source, self.operation.value, self.sink)
        return "({}) {} ({})".format(self.source, self.operation.value, self.sink)

    def __repr__(self):
        return str(self)

    @property
    def source(self) -> IPrintableTerm:
        return self._source

    @property
    def operation(self) -> CategoryOperations:
        return self._operation

    @property
    def sink(self) -> IPrintableTerm:
        return self._sink

    def __eq__(self, other):
        return isinstance(other, ProcessedTerm) and \
            (self.source, self.operation.value, self.sink) == (other.source, other.operation.value, other.sink)

    def __hash__(self):
        return (self.source, self.operation, self.sink).__hash__()

