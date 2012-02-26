#!/usr/bin/env python

class BeastCommentParser:
    """Class to parse BEAST-style comments in Nexus trees.
    """
    def __init__(self, string):
        """
        Returns a `BeastCommentParser` object when passed a comment string as an argument.

        """
        self.comment = string
        self._stream = self.tokenize(string)

    class BeastCommentParserError(Exception):
        pass

    def parse(self):
        """Parses the comment string associated with the current object. Returns a python
        dictionary if successful, or raises a `BeastCommentParserException` otherwise.

        >>> parser = BeastCommentParser('&height_95%_HPD={40.05717565800388,70.61032474932166},height_median=47.571176094511124')
        >>> print parser.parse()
        {'height_95%_HPD': ['40.05717565800388', '70.61032474932166'], 'height_median': '47.571176094511124'}

        >>> badparser = BeastCommentParser('height=5555')
        >>> badparser.parse()
        Traceback (most recent call last):
            ...
        BeastCommentParserError: Expected '&' but got 'height'
        """
        try:
            self._parse(self._stream)
        except StopIteration:
            return self.parsed

    def _parse(self, stream):
        """Internal parse function. A simple recursive-descent parser."""
        self.parsed = {}
        self._expect('&')
        while self.token is not None:
            identifier = self._expect('IDENTIFIER', self._not_special).strip('"')
            self._expect('=')
            if (self._not_special(self._advance())):
                self.parsed[identifier] = self._check('VALUE', self._not_special).strip('"')
                self._expect(',')
            else:
                array = []
                self._check('{')
                while self.token is not '}':
                    array.append(self._expect('VALUE', self._not_special).strip('"'))
                    self._expect(',}')
                self.parsed[identifier] = array
                self._expect(',')

    def _expect(self, wanted, test=None):
        """Advances the current token and checks it against "wanted"."""
        self._advance()
        return self._check(wanted, test)

    def _check(self, wanted, test=None):
        """Checks that the current token is what we want, otherwise throw BeastCommentParserError."""
        if test is None:
            test = self.token in wanted
        elif callable(test):
            test = test(self.token)
        if not test:
            raise self.BeastCommentParserError("Expected '%s' but got '%s'" % (wanted, self.token))
        return self.token

    def _not_special(self, char=None):
        """Returns True if the token is a literal or identifier.

        >>> parser = BeastCommentParser('')
        >>> parser._not_special('&')
        False
        >>> parser._not_special('abc123')
        True
        """
        return not char in '&={},'

    def _advance(self):
        """Advances the current token and returns it."""
        self.token = self._stream.next()
        return self.token

    def tokenize(self, string):
        """Simple generator that generates tokens for the parser."""
        accumulator = ''
        for char in string:
            if self._not_special(char):
                accumulator += char
            else:
                if len(accumulator):
                    yield accumulator
                    accumulator = ''
                yield char
        yield accumulator # eof, so clear the buffer and exit

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.IGNORE_EXCEPTION_DETAIL)
