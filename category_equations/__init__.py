"""
@copyright: 2010 - 2018 by Pauli Rikula <pauli.rikula@gmail.com>

@license: MIT <http://www.opensource.org/licenses/mit-license.php>


"""

from .terms import (
    debug,
    from_operator,
    OperationsSet,
    Category,
    CategoryOperations,
    ProcessedTerm,
    IEquationTerm,
    EquationTerm)

from .analysis import get_o_tail_products

__all__ = [
    'debug',
    'from_operator',
    'OperationsSet',
    'Category',
    'CategoryOperations',
    'ProcessedTerm',
    'IEquationTerm',
    'EquationTerm',
    'get_o_tail_products']
