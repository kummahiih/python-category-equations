"""
   @copyright: 2010 - 2019 by Pauli Rikula <pauli.rikula@gmail.com>
   @license: MIT <http://www.opensource.org/licenses/mit-license.php>
"""

from typing import Set, List, Callable


"""
These classes are used for connection operation serialization so that the connections can be 
manipulated before applying em.
"""


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