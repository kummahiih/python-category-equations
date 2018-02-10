"""
@copyright: 2010 - 2018 by Pauli Rikula <pauli.rikula@gmail.com>

@license: MIT <http://www.opensource.org/licenses/mit-license.php>


Create category like equations for the given operator in which
the underlaying '+' and '-' operations are basic set operations called union and discard.
The multiplication operator '*' connects sources to sinks. The equation system also has
a Identity 'I' and zerO 'O' terms. For futher details search 'category theory'
from the Wikipedia and do your own maths.
"""

from .terms import from_operator


__all__ = ['from_operator']
