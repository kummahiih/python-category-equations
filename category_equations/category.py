"""
   @copyright: 2010 - 2019 by Pauli Rikula <pauli.rikula@gmail.com>
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

import enum
import abc
from typing import Set, List, Callable

from .operation import FreezedOperation, OperationsSet

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