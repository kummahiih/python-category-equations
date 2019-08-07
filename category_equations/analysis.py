"""
@copyright: 2018 by Pauli Rikula <pauli.rikula@gmail.com>

@license: MIT <http://www.opensource.org/licenses/mit-license.php>

"""

from heapq import heappop, heappush

from .term import (
    CategoryOperations,
    ProcessedTerm,
    IEquationTerm,
    CategoryOperations,
    Identity,
    Adder,
    MediateTerm)

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
    def replacers(term: IEquationTerm):
        """
        >>> I, O, C = from_operator(debug)
        >>> len( [r for r in Get.replacers( (C(1) + C(2)) * C(3) )])
        5
        
        """
        
        def replace_terminal(manipulator):
            return manipulator(term)
        yield replace_terminal
        

        if TermIs.terminal(term):
            return
        
        def replace_sink(manipulator):
            new_sink = manipulator(term.processed_term.sink)
            if new_sink is None:
                return None
            processed_term = ProcessedTerm(
                sink = new_sink,
                operation=term.processed_term.operation,
                source = term.processed_term.source)

            return MediateTerm(
                operator=term.operator,
                sources=term.sources,
                sinks=term.sinks,
                operations=term.operations,
                processed_term=processed_term)

        def replace_source(manipulator):
            new_source = manipulator(term.processed_term.source)
            if new_source is None:
                return None
            processed_term = ProcessedTerm(
                sink = term.processed_term.sink,
                operation=term.processed_term.operation,
                source = new_source)

            return MediateTerm(
                operator=term.operator,
                sources=term.sources,
                sinks=term.sinks,
                operations=term.operations,
                processed_term=processed_term)

        for child_operation in Get.replacers(term.processed_term.sink):
            def replace_in_sink(manipulator):
                def replace_term(term):
                    return child_operation(manipulator)
                return replace_sink(replace_term)
            yield replace_in_sink
        
        for child_operation in Get.replacers(term.processed_term.source):
            def replace_in_source(manipulator):
                def replace_term(term):
                    return child_operation(manipulator)
                return replace_source(replace_term)
            yield replace_in_source


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
                for source in left_tail_terms:
                    yield source * term.processed_term.source
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
        C(1)

        >>> Get.head(C(1))
        C(1)

        """
        if TermIs.terminal(term):
            return term
        if TermIs.arrow(term) or TermIs.add(term):
            return term.processed_term.sink
        return None

    @staticmethod
    def tail(term: IEquationTerm) -> IEquationTerm:
        """
        >>> I, O, C = from_operator(debug)
        >>> Get.tail(C(1) * C(2))
        C(2)
        >>> Get.tail(C(1) + C(2))
        C(2)
        >>> Get.tail(C(1))
        C(1)

        """
        if TermIs.terminal(term):
            return term
        if TermIs.arrow(term) or TermIs.add(term):
            return term.processed_term.source
        return None

class Equal:
    @staticmethod
    def sink_out(term: IEquationTerm, I: Identity) -> IEquationTerm:
        """
        >>> I, O, C = from_operator(debug)

        >>> Equal.sink_out(C(1), I)
        C(1) * I

        >>> Equal.sink_out(C(1)*C(2), I)
        C(1) * I * C(2)
        
        >>> Equal.sink_out((C(1) * C(2)) + (C(1) * C(3)), I)
        C(1) * (I * C(2) + I * C(3))
        
        >>> Equal.sink_out((C(1) * C(2)) + (C(2) * C(3)), I)
        (C(1) * C(2) + C(2) * C(3)) * I

        >>> Equal.sink_out(C(1)-C(2), I)
        (C(1) - C(2)) * I

        """

        if TermIs.terminal(term) or TermIs.discard(term):
            return term*I
        
        if TermIs.arrow(term):
            if I in [term.processed_term.sink, term.processed_term.source]:
                return None
            return term.processed_term.sink * (I * term.processed_term.source)
        
        if TermIs.add(term):
            head_sink = Get.head(term.processed_term.sink)
            head_source = Get.head(term.processed_term.source)
            if head_sink != head_source:
                return term * I
            sink_sink = Equal.sink_out(term.processed_term.sink, I)
            source_sink = Equal.sink_out(term.processed_term.source, I)
            if None in [sink_sink, source_sink]:
                return None
            return head_sink * (
                sink_sink.processed_term.source + \
                    source_sink.processed_term.source)
        return None

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
    def source_out(term: IEquationTerm, I: Identity) -> IEquationTerm:
        """
        >>> I, O, C = from_operator(debug)

        >>> Equal.source_out(C(1), I)
        I * C(1)

        >>> Equal.source_out(C(1)*C(2), I)
        C(1) * I * C(2)
        
        >>> Equal.source_out((C(1) * C(3)) + (C(2) * C(3)), I)
        (C(1) * I + C(2) * I) * C(3)
        
        >>> Equal.source_out((C(1) * C(2)) + (C(2) * C(3)), I)
        I * (C(1) * C(2) + C(2) * C(3))

        >>> Equal.source_out(C(1)-C(2), I)
        I * (C(1) - C(2))

        """

        if TermIs.terminal(term) or TermIs.discard(term):
            return I * term
        
        if TermIs.arrow(term):
            if I in [term.processed_term.sink, term.processed_term.source]:
                return None
            return (term.processed_term.sink * I) * term.processed_term.source
        
        if TermIs.add(term):
            tail_sink = Get.tail(term.processed_term.sink)
            tail_source = Get.tail(term.processed_term.source)
            if tail_sink != tail_source:
                return I * term
            sink_source = Equal.source_out(term.processed_term.sink, I)
            source_source = Equal.source_out(term.processed_term.source, I)
            if None in [sink_source, source_source]:
                return None
            return (sink_source.processed_term.sink + \
                    source_source.processed_term.sink) * tail_sink
        return None
    
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
        >>> Equal.swap_tail(C(1))

        """
        if TermIs.add(term):
            if TermIs.add(term.processed_term.source):
                return (term.processed_term.sink + term.processed_term.source.processed_term.sink) + term.processed_term.source.processed_term.source
        if TermIs.arrow(term):
            if TermIs.arrow(term.processed_term.source):
                return (term.processed_term.sink * term.processed_term.source.processed_term.sink) * term.processed_term.source.processed_term.source
        return None
    
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
        return None
    
    @staticmethod
    def swap(term: IEquationTerm) -> IEquationTerm:
        """
        >>> I, O, C = from_operator(debug)

        >>> Equal.swap( C(1) + C(2) )
        C(2) + C(1)

        >>> Equal.swap( C(1) * C(2) )

        """
        if TermIs.add(term):
            return  term.processed_term.source + term.processed_term.sink
        return None

    @staticmethod
    def remove_adder(term: IEquationTerm) -> IEquationTerm:
        """
        >>> I, O, C = from_operator(debug)

        >>> Equal.remove_adder( C(1,2,3) )
        (C(1) + C(2)) + C(3)

        >>> Equal.remove_adder( C(1) )
        C(1)

        >>> Equal.remove_adder( I )


        """
        if isinstance(term, Adder):
            return term.reduce_to_additions()
        return None
    
    @staticmethod
    def add_adder(term: IEquationTerm) -> IEquationTerm:
        """
        >>> I, O, C = from_operator(debug)
        >>> a = C(1) + C(2)
        >>> TermIs.add(a)
        True
        >>> Equal.add_adder(a)
        C(1, 2)
        >>> Equal.add_adder(C(1,2) + C(3))
        C(1, 2, 3)

        >>> Equal.add_adder( C(1) )
        >>> Equal.add_adder( C(1) * C(2) )

        """
        if TermIs.add(term):
            head = Get.head(term)
            tail = Get.tail(term)
            if isinstance(head, Adder) and isinstance(tail, Adder):
                return head.combine(tail)
        return None

class EquationMapItem:
    def __init__(self,term):
        self.term = term
    def as_tuple(self):
        return (self.term, self.term.processed_term)

    def __hash__(self):
        return self.as_tuple().__hash__()
    def __str__(self):
        return str(self.term)
    def __repr__(self):
        return str(self)
    def __lt__(self, another):
        return str(self) < str(another)

    def __le__(self, another):
        return str(self) <= str(another)

    def __eq__(self, other):
        if other is None:
            return False
        return self.as_tuple() ==  other.as_tuple()


class EquationMap:
    def __init__(self, I, O, C, manipulations: list = None):
        """
        >>> I, O, C = from_operator(debug)
        >>> a = C(1) + C(2)
        >>> m = EquationMap(I, O, C)
        >>> len(m.manipulations)
        8

        """
        self.I, self.O, self.C = I, O, C

        if manipulations is None:
            self.manipulations = [
                lambda term: Equal.identity_off(term, I),
                Equal.remove_adder,
                Equal.add_adder,
                Equal.swap,
                Equal.swap_head,
                Equal.swap_tail,
                lambda term: Equal.sink_out(term, I),
                lambda term: Equal.source_out(term, I)]
        else:
            self.manipulations = manipulations
        self._node_cache = {}
    
    def get_cached(self, x):
        if x is None:
            return None
        if isinstance(x, EquationMapItem):
            new_cached = x
        else:
            new_cached = EquationMapItem(x)
        cached = self._node_cache.get(new_cached, None)
        if cached is not None:
            return cached
        else:
            self._node_cache[new_cached] = new_cached
            return new_cached
        
    def clear_cache(self):
        self._node_cache = {}

    def dist_between(self, x, y):
        """
        >>> I, O, C = from_operator(debug)
        >>> a = C(1) + C(2)
        >>> b = C(1) + C(3)
        >>> m = EquationMap(I, O, C)
        >>> m.dist_between(a, a)
        0
        >>> m.dist_between(a, b)
        2
        >>> m.dist_between((C(2) + C(1)) * I, None)
        17

        """


        str_x = str(x if x is not None else "")
        len_str_x = len(str_x)

        str_y = str(y if y is not None else "")
        len_str_y = len(str_y)
        diff_point = min(len_str_x, len_str_y)

        for i in range(min(len_str_x, len_str_y)):
            if str_x[i] != str_y[i]:
                diff_point = i
                break

        return max(len_str_x, len_str_y) - diff_point

    
    def neighbor_nodes(self, x):
        """
        >>> I, O, C = from_operator(debug)
        >>> a = C(1) + C(2)
        >>> m = EquationMap(I, O, C)
        >>> for node in m.neighbor_nodes(a):
        ...    print(node)
        C(1) + C(2)
        C(1) + C(2)
        C(1) + C(2)
        C(1) + C(2)
        C(1) + C(2)
        C(1, 2)
        C(2) + C(1)
        (C(1) + C(2)) * I
        C(1) * I + C(2)
        C(1) + C(2) * I
        I * (C(1) + C(2))
        I * C(1) + C(2)
        C(1) + I * C(2)
        
        >>> for node in m.neighbor_nodes(C(1) * C(2)):
        ...    print(node)
        C(1) * C(2)
        C(1) * C(2)
        C(1) * C(2)
        C(1) * C(2)
        C(1) * C(2)
        C(1) * I * C(2)
        C(1) * I * C(2)
        C(1) * C(2) * I
        C(1) * I * C(2)
        I * C(1) * C(2)
        C(1) * I * C(2)

        """
        x = self.get_cached(x)
        
        for manipulation in self.manipulations:
            def cached_manipulation(term):
                returned = manipulation(term)
                if returned is None:
                    return None
                return self.get_cached(returned).term

            for replacer in Get.replacers(x.term):
                returned = replacer(cached_manipulation)

                if returned is not None:
                    yield self.get_cached(returned)


def simplify(term: IEquationTerm, max_iterations = 1024, equation_map=None):
    """
    >>> I, O, C = from_operator(debug)
    >>> a = C(1) + C(2)
    >>> m = EquationMap(I, O, C)
    >>> simplify(a, 300, m)
    (C(1, 2), [C(1) + C(2), C(1, 2)])

    >>> b = C(1) * C(3) + C(2) * C(3)
    >>> simplified, path = simplify(b, 100, m)
    >>> simplified
    C(1, 2) * C(3)
    >>> for p in path:
    ...    print(p)
    C(1) * C(3) + C(2) * C(3)
    (C(1) * I + C(2) * I) * C(3)
    (C(1) + C(2) * I) * C(3)
    (C(1) + C(2)) * C(3)
    C(1, 2) * C(3)

    """
    cached_term = equation_map.get_cached(term)

    closedset = set([])
    firstItem = (equation_map.dist_between(cached_term, None), cached_term)
    scoreHeap = [firstItem]
    visitedheap = [firstItem]
    
    came_from = {}

    iteration_count = 0
    while any(scoreHeap) and iteration_count < max_iterations: # is not empty
        iteration_count += 1
        x = heappop(scoreHeap)
        closedset.add(x[1])

        neighbornodes =  [ 
            (equation_map.dist_between(node_y, None), node_y )
            for node_y in equation_map.neighbor_nodes(x[1]) if node_y is not None
            ]
        #better sort here than update the heap
        neighbornodes.sort()

        for score, y in neighbornodes:
            
            if y in closedset:
                continue
            
            came_from[y] = x[1]
            
            heappush(scoreHeap, (score, y))
            heappush(visitedheap, (score, y))
    
    shortest = heappop(visitedheap)[1]
    path = [shortest.term]
    prev = shortest
    while str(prev) != str(term):
        prev = came_from[prev]
        path.insert(0, prev.term)

    return shortest.term, path

def get_route(a,b, max_iterations=1024, equation_map=None):
    """
    >>> I, O, C = from_operator(debug)
    >>> m = EquationMap(I, O, C)
    >>> a = C(1) * C(3) + C(2) * C(3)
    >>> b = C(1, 2) * C(3)
    >>> shortest, path = get_route(a,b, 100, m)
    >>> for p in path:
    ...    print(p)
    C(1) * C(3) + C(2) * C(3)
    C(1) * C(3) + C(2) * I * C(3)
    (C(1) * I + C(2) * I) * C(3)
    (C(1) + C(2) * I) * C(3)
    (C(1) + C(2)) * C(3)
    C(1, 2) * C(3)


    """
    a = equation_map.get_cached(a)
    b = equation_map.get_cached(b)

    closedset = set([])
    firstItem = (equation_map.dist_between(a, b), a)
    scoreHeap = [firstItem]
    visitedheap = [firstItem]
    came_from = {}

    iteration_count = 0
    while any(scoreHeap) and iteration_count < max_iterations: # is not empty
        iteration_count += 1
        x = heappop(scoreHeap)
        closedset.add(x[1])

        neighbornodes =  [ 
            (equation_map.dist_between(node_y, b), node_y )
            for node_y in equation_map.neighbor_nodes(x[1]) if node_y is not None
            ]
        #better sort here than update the heap
        neighbornodes.sort()

        for score, y in neighbornodes:
            
            if y in closedset:
                continue
            
            came_from[y] = x[1]
            
            heappush(scoreHeap, (score, y))
            heappush(visitedheap, (score, y))
    
    
    shortest = heappop(visitedheap)[1]
    path = [shortest.term]
    prev = shortest
    while str(prev) != str(a):
        prev = came_from[prev]
        path.insert(0, prev.term)

    return shortest.term, path



