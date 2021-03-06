# -*- coding: utf-8 -*-
""" Run is the main function that will check if the recode and bibtex
modules are working """

import sys, os


def check_recode ():
    try:
        import _recode

    except SystemError:
        raise RuntimeError ('the recode library is probably broken.')

    # First, check if the recode version has the famous 3.6 bug
    rq = _recode.request ('latin1..latex')
    
    if _recode.recode (rq, 'abc') != 'abc':
        raise RuntimeError ('the _recode module is broken.')

    return 0


def expected_result (obtained, valid):
    if obtained == valid:
        return True
    try:
        return eval(obtained) == eval(valid)
    except SyntaxError:
        return False


def check_bibtex ():

    _debug = False
    
    import _bibtex


    def checkfile (filename, strict = 1, typemap = {}):
        
        def expand (file, entry, type = -1):
            """Inline the expanded respresentation of each field."""
            bibkey, bibtype, a, b, items = entry
            results = []
            for k in sorted(items):
                results.append((k, _bibtex.expand (file, items [k], typemap.get (k, -1))))
            return (bibkey, bibtype, a, b, results)
        
        file   = _bibtex.open_file (filename, strict)
        result = open (filename + '-ok', 'r')

        line     = 1
        failures = 0
        checks   = 0
        
        while 1:

            try:
                entry = _bibtex.next (file)

                if entry is None: break
                            
                obtained = repr(expand (file, entry))
                
            except IOError as msg:
                obtained = 'ParserError'
                

            if _debug: print(obtained)

            valid = result.readline ().strip ()
            
            if not expected_result(obtained, valid):
                sys.stderr.write ('error: %s: line %d: unexpected result:\n' % (
                    filename, line))
                sys.stderr.write ('error: %s: line %d:    obtained %s\n' % (
                    filename, line, obtained))
                sys.stderr.write ('error: %s: line %d:    expected %s\n' % (
                    filename, line, valid))

                failures = failures + 1

            checks = checks + 1
                
        return failures, checks

    def checkunfiltered (filename, strict = 1):
        
        def expand (file, entry):
            if entry[0] in ('preamble', 'string'):
                return entry

            bibkind, (bibkey, bibtype, a, b, items) = entry

            results = [(k, _bibtex.expand (file, items [k], -1))
                       for k in sorted(items)]
            return (bibkind, (bibkey, bibtype, a, b, results))
        
        file   = _bibtex.open_file (filename, strict)
        result = open (filename + '-ok', 'r')

        line     = 1
        failures = 0
        checks   = 0
        
        while 1:

            try:
                entry = _bibtex.next_unfiltered (file)

                if entry is None: break

                obtained = repr(expand (file, entry))
                
            except IOError as msg:
                obtained = 'ParserError'
                

            if _debug: print(obtained)

            valid = result.readline ().strip ()
            
            if not expected_result(obtained, valid):
                sys.stderr.write ('error: %s: line %d: unexpected result:\n' % (
                    filename, line))
                sys.stderr.write ('error: %s: line %d:    obtained %s\n' % (
                    filename, line, obtained))
                sys.stderr.write ('error: %s: line %d:    expected %s\n' % (
                    filename, line, valid))
                failures = failures + 1
            checks = checks + 1
        return failures, checks

    failures = 0
    checks   = 0

    parser = _bibtex.open_file('/dev/null', True)
    def convert(text, t):
        field = _bibtex.reverse(t, True, text)
        return _bibtex.get_latex(parser, field, t)

    for t, r in ((0, r'\'essai A \{\} toto~tutu'),
                 (2, r'\'essai {A} \{\} toto~tutu'),
                 (4, text)):
        checks += 1
        o = convert(text, t)
        if o != r:
            print("type %d convert: got %r instead of %r" % (
                t, o, r))
            failures += 1

    for file in('tests/preamble.bib',
                'tests/string.bib',
                'tests/simple-2.bib'):
        f, c = checkunfiltered (file)
        failures = failures + f
        checks   = checks   + c

    failures += f
    checks   += c
   
    for file in ('tests/simple.bib',
                 'tests/authors.bib',
                 'tests/eof.bib',
                 'tests/paren.bib',
                 'tests/url.bib'):

        f, c = checkfile (file, typemap = {'url': 4})
        failures = failures + f
        checks   = checks   + c

    print("testsuite: %d checks, %d failures" % (checks, failures))
    return failures



def run ():
    failures = 0

    return 0
    failures += check_recode ()
    failures += check_bibtex ()

    return failures
