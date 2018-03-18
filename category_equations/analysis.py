"""
@copyright: 2018 by Pauli Rikula <pauli.rikula@gmail.com>

@license: MIT <http://www.opensource.org/licenses/mit-license.php>

"""

from copy import copy

from category_equations.terms import (
    debug,
    from_operator,
    OperationsSet,
    Category,
    CategoryOperations,
    ProcessedTerm,
    IEquationTerm)


def get_o_tail_products(term: IEquationTerm):
    """
    >>> I, O, C = from_operator(debug)
    >>> a = C(1) * C(2) * C(3) * O
    >>> get_o_tail_products(a)
    [(((C(1)) * (C(2))) * (C(3))) * (O)]
    >>> a = C(1) * (C(2) + C(3)*O) *C(4) * O
    >>> get_o_tail_products(a)
    [(((C(1)) * ((C(2)) + ((C(3)) * (O)))) * (C(4))) * (O), (C(3)) * (O)]

    >>> a = C(1) * (C(2) + C(3)*O) + C(1) * O
    >>> get_o_tail_products(a)
    [(C(1)) * (O), (C(3)) * (O)]
    >>> get_o_tail_products(O*O)
    []
    >>> get_o_tail_products(I*O)
    []
    >>> get_o_tail_products(I)
    []
    >>> get_o_tail_products(O)
    []
    >>> get_o_tail_products(C(4))
    []
    """

    if not isinstance(term, IEquationTerm):
        raise ValueError("expected IEquationTerm, got '{}'".format(type(term)))

    currently_analyzed = set()
    already_analyzed = dict()

    def analyze_and_remember(term: IEquationTerm):
        if term in currently_analyzed:
            raise ValueError("found a loop leading to '{}'".format(term))
        if term in already_analyzed:
            return already_analyzed[term]
        currently_analyzed.add(term)
        result = get_o_product(term)
        already_analyzed[term] = result
        currently_analyzed.remove(term)
        return result

    def get_o_product(term: IEquationTerm):
        if term.processed_term is None:
            return None
        if term.processed_term.operation != CategoryOperations.ARROW:
            return None
        if term.processed_term.source.is_zero():
            return None
        if term.processed_term.source.is_identity():
            return None
        if term.processed_term.sink.is_zero():
            return term
        return analyze_and_remember(term.processed_term.sink)


    all_terms = set()

    def collect_terms(term: IEquationTerm):
        if term in all_terms:
            return
        all_terms.add(term)
        if term.processed_term is None:
            return
        collect_terms(term.processed_term.source)
        collect_terms(term.processed_term.sink)

    collect_terms(term)

    for processed_term in all_terms:
        analyze_and_remember(processed_term)

    o_products = [i for i in already_analyzed.values() if i is not None]
    o_products.sort()
    return o_products



if __name__ == '__main__':
    import doctest
    doctest.testmod()