"""
@copyright: 2018 by Pauli Rikula <pauli.rikula@gmail.com>

@license: MIT <http://www.opensource.org/licenses/mit-license.php>

"""

from category_equations.terms import (
    debug,
    from_operator,
    OperationsSet,
    Category,
    CategoryOperations,
    ProcessedTerm,
    IEquationTerm)

def term_is_terminal(term): return term.processed_term is None

def term_is_o(term): return term.is_zero()

def term_is_almost_o(term):
    return term_is_o(term) or not term_is_terminal(term) and (
        term_is_o(term.processed_term.source) or term_is_o(term.processed_term.sink))

def term_sink_is_o(term): 
    if term.processed_term is None:
        return False
    return term.processed_term.is_zero()

def term_is_arrow(term): 
    if term.processed_term is None:
        return False
    return term.processed_term.operation == CategoryOperations.ARROW

def term_is_add(term): 
    if term.processed_term is None:
        return False
    return term.processed_term.operation == CategoryOperations.ADD


def get_all_terms(term: IEquationTerm):
    """
    >>> I, O, C = from_operator(debug)
    >>> a = C(1) * C(2) * C(3) * O
    >>> for i in get_all_terms(a):
    ...   print(i)
    (((C(1)) * (C(2))) * (C(3))) * (O)
    ((C(1)) * (C(2))) * (C(3))
    (C(1)) * (C(2))
    C(1)
    C(2)
    C(3)
    O
    """
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
    all_terms_l = list(all_terms)
    all_terms_l.sort()
    return all_terms_l

def get_tail_products(term: IEquationTerm):
    """
    >>> I, O, C = from_operator(debug)
    >>> for i in get_tail_products(C(1) * C(2) * C(3) * (O + C(4))):
    ...   print(i)
    (((C(1)) * (C(2))) * (C(3))) * ((O) + (C(4)))
    ((C(2)) * (C(3))) * ((O) + (C(4)))
    (C(3)) * ((O) + (C(4)))
    (O) + (C(4))
    
    >>> for i in get_tail_products(C(1) * (C(2) + C(3)) * (O + C(4))):
    ...   print(i)
    ((C(1)) * ((C(2)) + (C(3)))) * ((O) + (C(4)))
    ((C(2)) + (C(3))) * ((O) + (C(4)))
    (O) + (C(4))
    """
    if term_is_terminal(term):
        yield term
    if term_is_add(term):
        yield term

    if term_is_arrow(term):
        right_tail_terms = list(get_tail_products(term.processed_term.sink))
        left_tail_terms = list(get_tail_products(term.processed_term.source))
        if len(right_tail_terms) > 0:
            for tail in left_tail_terms:
                yield tail * term.processed_term.sink
            yield from right_tail_terms

def get_topmost_sums(term: IEquationTerm):
    """
    >>> I, O, C = from_operator(debug)
    >>> for i in get_topmost_sums(C(1) + (C(2) * C(3)) + C(1)* C(3) * C(4)):
    ...   print(i)
    C(1)
    (C(2)) * (C(3))
    ((C(1)) * (C(3))) * (C(4))

    """
    if term_is_terminal(term):
        yield term
    if term_is_arrow(term):
        yield term
    if term_is_add(term):
        yield from get_topmost_sums(term.processed_term.source)
        yield from get_topmost_sums(term.processed_term.sink)

def get_topmost_tail_products(term: IEquationTerm):
    """
    >>> I, O, C = from_operator(debug)
    >>> for i in get_topmost_tail_products(C(1) * C(2) + C(1) * C(3) * (O + C(4)) + C(5)):
    ...   print(i)
    (C(1)) * (C(2))
    C(2)
    ((C(1)) * (C(3))) * ((O) + (C(4)))
    (C(3)) * ((O) + (C(4)))
    (O) + (C(4))
    C(5)

    """
    for sub_term in get_topmost_sums(term):
        yield from get_tail_products(sub_term)


if __name__ == '__main__':
    import doctest
    doctest.testmod()