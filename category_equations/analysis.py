"""
@copyright: 2018 by Pauli Rikula <pauli.rikula@gmail.com>

@license: MIT <http://www.opensource.org/licenses/mit-license.php>

"""


from .term import (
    CategoryOperations,
    ProcessedTerm,
    IEquationTerm,
    CategoryOperations,
    Identity)

class TermIs:

    @staticmethod
    def terminal(term: IEquationTerm) -> bool: 
        return term.processed_term is None
    
    @staticmethod
    def not_terminal(term: IEquationTerm) -> bool: 
        return term.processed_term is not None
    
    @staticmethod
    def arrow(term: IEquationTerm) -> bool: 
        return TermIs.not_terminal(term) and term.processed_term.operation == CategoryOperations.ARROW

    @staticmethod
    def add(term: IEquationTerm) -> bool: 
        return TermIs.not_terminal(term) and term.processed_term.operation == CategoryOperations.ADD
    
    @staticmethod
    def discard(term: IEquationTerm) -> bool: 
        return TermIs.not_terminal(term) and term.processed_term.operation == CategoryOperations.DISCARD

class Get:
    @staticmethod
    def all_terms(term: IEquationTerm):
        """
        >>> I, O, C = from_operator(debug)
        >>> a = C(1) * C(2) * C(3) * O
        >>> for i in Get.all_terms(a):
        ...   print(i)
        C(1)
        C(1) * C(2)
        C(1) * C(2) * C(3)
        C(1) * C(2) * C(3) * O
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
            collect_terms(term.processed_term.sink)
            collect_terms(term.processed_term.source)

        collect_terms(term)
        all_terms_l = list(all_terms)
        all_terms_l.sort()
        return all_terms_l

    @staticmethod
    def tail_products(term: IEquationTerm):
        """
        >>> I, O, C = from_operator(debug)
        >>> for i in Get.tail_products(C(1) * C(2) * C(3) * (O + C(4))):
        ...   print(i)
        C(1) * C(2) * C(3) * (O + C(4))
        C(2) * C(3) * (O + C(4))
        C(3) * (O + C(4))
        O + C(4)
        
        >>> for i in Get.tail_products(C(1) * (C(2) + C(3)) * (O + C(4))):
        ...   print(i)
        C(1) * (C(2) + C(3)) * (O + C(4))
        (C(2) + C(3)) * (O + C(4))
        O + C(4)

        """
        if TermIs.terminal(term):
            yield term
        if TermIs.add(term):
            yield term

        if TermIs.arrow(term):
            right_tail_terms = list(Get.tail_products(term.processed_term.source))
            left_tail_terms = list(Get.tail_products(term.processed_term.sink))
            if len(right_tail_terms) > 0:
                for tail in left_tail_terms:
                    yield tail * term.processed_term.source
                yield from right_tail_terms

    @staticmethod
    def topmost_sums(term: IEquationTerm):
        """
        >>> I, O, C = from_operator(debug)
        >>> for i in Get.topmost_sums(C(1) + (C(2) * C(3)) + C(1)* C(3) * C(4)):
        ...   print(i)
        C(1)
        C(2) * C(3)
        C(1) * C(3) * C(4)


        """
        if TermIs.terminal(term):
            yield term
        if TermIs.arrow(term):
            yield term
        if TermIs.add(term):
            yield from Get.topmost_sums(term.processed_term.sink)
            yield from Get.topmost_sums(term.processed_term.source)

    @staticmethod
    def topmost_tail_products(term: IEquationTerm):
        """
        >>> I, O, C = from_operator(debug)
        >>> for i in Get.topmost_tail_products(C(1) * C(2) + C(1) * C(3) * (O + C(4)) + C(5)):
        ...   print(i)
        C(1) * C(2)
        C(2)
        C(1) * C(3) * (O + C(4))
        C(3) * (O + C(4))
        O + C(4)
        C(5)

        """
        for sub_term in Get.topmost_sums(term):
            yield from Get.tail_products(sub_term)

    @staticmethod
    def head(term: IEquationTerm) -> IEquationTerm:
        """
        >>> I, O, C = from_operator(debug)
        >>> Get.head(C(1) * C(2))
        C(1)
        >>> Get.head(C(1) + C(2))
        >>> Get.head(C(1))
        C(1)

        """
        if TermIs.terminal(term):
            return term
        if TermIs.arrow(term):
            return term.processed_term.sink
        return None

    @staticmethod
    def tail(term: IEquationTerm) -> IEquationTerm:
        """
        >>> I, O, C = from_operator(debug)
        >>> Get.tail(C(1) * C(2))
        C(2)
        >>> Get.tail(C(1) + C(2))
        >>> Get.tail(C(1))
        C(1)

        """
        if TermIs.terminal(term):
            return term
        if TermIs.arrow(term):
            return term.processed_term.source
        return None

class Equal:
    @staticmethod
    def head_out(term: IEquationTerm, I: Identity) -> IEquationTerm:
        """
        >>> I, O, C = from_operator(debug)

        >>> Equal.head_out(C(1), I)
        C(1) * I

        >>> Equal.head_out(C(1)*C(2), I)
        C(1) * I * C(2)
        
        >>> Equal.head_out((C(1) * C(2)) + (C(1) * C(3)), I)
        C(1) * (I * C(2) + I * C(3))
        
        >>> Equal.head_out((C(1) * C(2)) + (C(2) * C(3)), I)
        (C(1) * C(2) + C(2) * C(3)) * I

        >>> Equal.head_out(C(1)-C(2), I)
        (C(1) - C(2)) * I

        """

        if TermIs.terminal(term) or TermIs.discard(term):
            return term*I
        
        if TermIs.arrow(term):
            return term.processed_term.sink * (I * term.processed_term.source)
        
        if TermIs.add(term):
            head_sink = Get.head(term.processed_term.sink)
            head_source = Get.head(term.processed_term.source)
            if head_sink != head_source:
                return term * I
        return head_sink * (
            Equal.head_out(term.processed_term.sink, I).processed_term.source + \
                Equal.head_out(term.processed_term.source, I).processed_term.source)

    @staticmethod
    def identity_off(term: IEquationTerm, I) -> IEquationTerm:
        """
        >>> I, O, C = from_operator(debug)
        >>> Equal.identity_off(C(1), I)
        C(1)
        >>> Equal.identity_off(C(1) * I, I)
        C(1)
        
        >>> Equal.identity_off(I * C(1), I)
        C(1)

        >>> Equal.identity_off(C(2)* C(1), I)
        C(2) * C(1)

        >>> Equal.identity_off(C(2)* I * C(1), I)
        C(2) * C(1)
        
        """
        if TermIs.arrow(term):
            if term.processed_term.sink == I:
                return Equal.identity_off(term.processed_term.source, I)
            if term.processed_term.source == I:
                return Equal.identity_off(term.processed_term.sink, I)
            return Equal.identity_off(term.processed_term.sink, I) * Equal.identity_off(term.processed_term.source, I)
        return term

    @staticmethod
    def tail_out(term: IEquationTerm, I: Identity) -> IEquationTerm:
        """
        >>> I, O, C = from_operator(debug)

        >>> Equal.tail_out(C(1), I)
        I * C(1)

        >>> Equal.tail_out(C(1)*C(2), I)
        C(1) * I * C(2)
        
        >>> Equal.tail_out((C(1) * C(3)) + (C(2) * C(3)), I)
        (C(1) * I + C(2) * I) * C(3)
        
        >>> Equal.tail_out((C(1) * C(2)) + (C(2) * C(3)), I)
        I * (C(1) * C(2) + C(2) * C(3))

        >>> Equal.tail_out(C(1)-C(2), I)
        I * (C(1) - C(2))

        """

        if TermIs.terminal(term) or TermIs.discard(term):
            return I * term
        
        if TermIs.arrow(term):
            return (term.processed_term.sink * I) * term.processed_term.source
        
        if TermIs.add(term):
            tail_sink = Get.tail(term.processed_term.sink)
            tail_source = Get.tail(term.processed_term.source)
            if tail_sink != tail_source:
                return I * term
        return (Equal.tail_out(term.processed_term.sink, I).processed_term.sink + \
                Equal.tail_out(term.processed_term.source, I).processed_term.sink) * tail_sink
    
    @staticmethod
    def swap_tail(term: IEquationTerm) -> IEquationTerm:
        """
        >>> I, O, C = from_operator(debug)

        >>> a = C(1) + (C(2) + C(3))
        >>> a.processed_term.source
        C(2) + C(3)
        >>> b = Equal.swap_tail(a)
        >>> b
        (C(1) + C(2)) + C(3)
        >>> Equal.swap_tail(C(1) * (C(2) * C(3))).processed_term.sink
        C(1) * C(2)

        """
        if TermIs.add(term):
            if TermIs.add(term.processed_term.source):
                return (term.processed_term.sink + term.processed_term.source.processed_term.sink) + term.processed_term.source.processed_term.source
        if TermIs.arrow(term):
            if TermIs.arrow(term.processed_term.source):
                return (term.processed_term.sink * term.processed_term.source.processed_term.sink) * term.processed_term.source.processed_term.source
    
    @staticmethod
    def swap_head(term: IEquationTerm) -> IEquationTerm:
        """
        >>> I, O, C = from_operator(debug)

        >>> a = (C(1) + C(2)) + C(3)
        >>> a.processed_term.source
        C(3)
        >>> b = Equal.swap_head(a)
        >>> b
        C(1) + (C(2) + C(3))
        >>> Equal.swap_head((C(1) * C(2)) * C(3)).processed_term.source
        C(2) * C(3)

        """
        if TermIs.add(term):
            if TermIs.add(term.processed_term.sink):
                return term.processed_term.sink.processed_term.sink + (term.processed_term.sink.processed_term.source + term.processed_term.source)
        if TermIs.arrow(term):
            if TermIs.arrow(term.processed_term.sink):
                return term.processed_term.sink.processed_term.sink * (term.processed_term.sink.processed_term.source * term.processed_term.source)
            



