if __name__ == '__main__':
    import doctest
    import category_equations

    # by importing these here, there might be some import errors left..
    globs = {
        'debug': category_equations.debug,
        'from_operator': category_equations.from_operator,
        'OperationsSet': category_equations.OperationsSet,
        'Category': category_equations.Category,
        'CategoryOperations': category_equations.CategoryOperations,
        'ProcessedTerm': category_equations.ProcessedTerm,
        'IEquationTerm': category_equations.IEquationTerm,
        'EquationTerm': category_equations.EquationTerm,
        'Get': category_equations.Get,
        'Equal': category_equations.Equal,
        'TermIs': category_equations.TermIs}
    
    #doctest.testfile(filename="operation.py", module_relative=True, package=category_equations, globs=globs)
    #doctest.testfile(filename="category.py", module_relative=True, package=category_equations, globs=globs)
    #doctest.testfile(filename="terms.py", module_relative=True, package=category_equations, globs=globs)
    doctest.testfile(filename="__init__.py", module_relative=True, package=category_equations, globs=globs)
    doctest.testfile(filename="term.py", module_relative=True, package=category_equations, globs=globs)
    doctest.testfile(filename="analysis.py", module_relative=True, package=category_equations, globs=globs)

    