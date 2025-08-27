#!/usr/bin/env python3

from collections.abc import Generator
from enum import Enum, auto
from typing import Tuple
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

WS = [' ', '\u0020', '\u000A', '\u000D', '\u0009']

class Term(Enum):
    pass

class Rule(Enum):
    pass

class Terminal(Term):
    ZERO = auto()
    ONE_NINE = auto()
    CHAR = auto()
    INVALID = auto()
    END = auto()
    VALUE_NUMBER = auto()
    VALUE_BOOLEAN = auto()
    VALUE_NULL = auto()
    EMPTY = auto()
    ESCAPE_SPECIAL = auto()
    ESCAPE_HEX = auto()
    HEX = auto()

    def __str__(self):
        return f"T_{self.name}"


class NonTerminal(Rule):
    """Non Terminals used during syntatical analysis."""
    ELEMENTS = auto()
    ELEMENTS_TAIL = auto()
    VALUE = auto()
    VALUE_OBJECT = auto()
    VALUE_ARRAY = auto()
    VALUE_NUMBER = auto()
    VALUE_STRING = auto()
    MEMBER = auto()
    MEMBERS = auto()
    MEMBERS_TAIL = auto()
    FRACTION = auto()
    FRACTION_TAIL = auto()
    EXPONENT = auto()
    EXPONENT_E = auto()
    EXPONENT_e = auto()
    SIGN = auto()
    SIGN_PLUS = auto()
    SIGN_MINUS = auto()
    INTEGER = auto()
    INTEGER_DIGIT = auto()
    INTEGER_ONE_NINE = auto()
    INTEGER_MINUS = auto()
    INTEGER_MINUS_TAIL = auto()
    INTEGER_MINUS_DIGIT = auto()
    INTEGER_MINUS_ONE_NINE = auto()
    DIGIT = auto()
    DIGITS = auto()
    CHARS = auto()
    CHARS_TAIL = auto()
    ESCAPE = auto()
    ESCAPE_TAIL = auto()
    ESCAPE_HEX_TAIL = auto()
    NULL = auto()
    FALSE = auto()
    TRUE = auto()

    def __str__(self):
        return f"T_{self.name}"

class Lexer():

    def __init__(self, input_string):
        self.idx = 0
        self.input_string = input_string

    def parse_string(self):
        curr_str = ""

        self.idx += 1
        while self.input_string[self.idx] != '"':
            curr_str += self.input_string[self.idx]
            self.idx += 1
        self.idx += 1

        return curr_str

    def lexical_analysis(self) -> Generator[Tuple[Terminal,object]]:

        logger.debug("Lexical Analysis (LEXXER)")

        while self.idx < len(self.input_string):
            c = self.input_string[self.idx]

            if c in WS + ['\n']:
                self.idx += 1  # ignore
            elif c.isnumeric():
                self.idx += 1
                if c == '0':
                    yield (Terminal.ZERO, c)
                else:
                    yield (Terminal.ONE_NINE, c)
            elif c >= '\u0020' and c <= '\U0010FFFF':
                self.idx += 1
                yield (Terminal.CHAR, c)
            else:
                print("got invalid input ", c)
                exit(1)
                yield (Terminal.INVALID, None)
        yield (Terminal.END, None)


class SyntaticalAnalysis():
    """
    json -> element
    element -> value
    value -> object
    value -> array
    value -> string
    value -> number
    value -> boolean
    value -> null

    object -> '{' '}'
    object -> '{' members '}'
    members -> member
    members -> member ',' members
    member -> string ':' element

    array -> '[' ']'
    array -> '[' elements ']'
    elements -> element
    elements -> element ',' elements

             {  }  [  ]
    json     -  -
    element  -  -
    value    -  -
    object
    """

    def __init__(self):
        self.table = {
            NonTerminal.ELEMENTS: {
                (Terminal.CHAR, '"'): NonTerminal.ELEMENTS,
                Terminal.ZERO: NonTerminal.ELEMENTS,
                Terminal.ONE_NINE: NonTerminal.ELEMENTS,
                (Terminal.CHAR, '{'): NonTerminal.ELEMENTS,
                (Terminal.CHAR, '-'): NonTerminal.ELEMENTS,
                (Terminal.CHAR, ','): NonTerminal.ELEMENTS_TAIL,
                (Terminal.CHAR, ']'): Terminal.EMPTY
            },
            NonTerminal.ELEMENTS_TAIL: {
                (Terminal.CHAR, ','): NonTerminal.ELEMENTS_TAIL,
                (Terminal.CHAR, ']'): Terminal.EMPTY
            },
            NonTerminal.VALUE: {
                (Terminal.CHAR, '{'): NonTerminal.VALUE_OBJECT,
                (Terminal.CHAR, '['): NonTerminal.VALUE_ARRAY,
                (Terminal.CHAR, '"'): NonTerminal.VALUE_STRING,
                (Terminal.CHAR, '-'): NonTerminal.VALUE_NUMBER,
                Terminal.ZERO: NonTerminal.VALUE_NUMBER,
                Terminal.ONE_NINE: NonTerminal.VALUE_NUMBER,
                (Terminal.CHAR, 'n'): NonTerminal.NULL,
                (Terminal.CHAR, 't'): NonTerminal.TRUE,
                (Terminal.CHAR, 'f'): NonTerminal.FALSE,
            },
            NonTerminal.VALUE_STRING: {
                (Terminal.CHAR, '"'): NonTerminal.VALUE_STRING
            },
            NonTerminal.VALUE_ARRAY: {
                (Terminal.CHAR, ']'): (Terminal.CHAR, ']')
            },
            NonTerminal.MEMBERS: {
                (Terminal.CHAR, '"'): NonTerminal.MEMBERS,
                (Terminal.CHAR, ','): NonTerminal.MEMBERS,
                (Terminal.CHAR, '}'): Terminal.EMPTY
            },
            NonTerminal.MEMBERS_TAIL: {
                (Terminal.CHAR, ','): NonTerminal.MEMBERS_TAIL,
                (Terminal.CHAR, '}'): Terminal.EMPTY,
            },
            NonTerminal.MEMBER: {(Terminal.CHAR, '"'): NonTerminal.MEMBER},
            NonTerminal.INTEGER: {
                NonTerminal.DIGIT: NonTerminal.INTEGER_DIGIT,
                Terminal.ONE_NINE: NonTerminal.INTEGER_ONE_NINE,
                (Terminal.CHAR, '-'): NonTerminal.INTEGER_MINUS,
            },
            NonTerminal.INTEGER_MINUS_TAIL: {
                Terminal.ONE_NINE: NonTerminal.INTEGER_MINUS_ONE_NINE,
            },
            NonTerminal.DIGITS: {
                Terminal.ZERO: NonTerminal.INTEGER_DIGIT,
                Terminal.ONE_NINE: NonTerminal.INTEGER_DIGIT,
                (Terminal.CHAR, '.'): Terminal.EMPTY,
                (Terminal.CHAR, ','): Terminal.EMPTY,
                (Terminal.CHAR, '}'): Terminal.EMPTY,
                (Terminal.CHAR, ']'): Terminal.EMPTY,
                (Terminal.CHAR, 'E'): Terminal.EMPTY,
                (Terminal.CHAR, 'e'): Terminal.EMPTY,
                Terminal.END: Terminal.EMPTY,
            },
            NonTerminal.DIGIT: {
                Terminal.ZERO: Terminal.ZERO,
                Terminal.ONE_NINE: Terminal.ONE_NINE,
            },
            NonTerminal.FRACTION: {
                (Terminal.CHAR, '.'): NonTerminal.FRACTION_TAIL,
                (Terminal.CHAR, ','): Terminal.EMPTY,
                (Terminal.CHAR, '}'): Terminal.EMPTY,
                (Terminal.CHAR, ']'): Terminal.EMPTY,
                (Terminal.CHAR, 'E'): Terminal.EMPTY,
                (Terminal.CHAR, 'e'): Terminal.EMPTY,
                Terminal.END: Terminal.EMPTY,
            },
            NonTerminal.EXPONENT: {
                (Terminal.CHAR, 'E'): NonTerminal.EXPONENT_E,
                (Terminal.CHAR, 'e'): NonTerminal.EXPONENT_e,
                (Terminal.CHAR, ','): Terminal.EMPTY,
                (Terminal.CHAR, '}'): Terminal.EMPTY,
                (Terminal.CHAR, ']'): Terminal.EMPTY,
                Terminal.END: Terminal.EMPTY,
            },
            NonTerminal.SIGN: {
                Terminal.ZERO: Terminal.EMPTY,
                Terminal.ONE_NINE: Terminal.EMPTY,
                (Terminal.CHAR, '-'): NonTerminal.SIGN_MINUS,
                (Terminal.CHAR, '+'): NonTerminal.SIGN_PLUS,
            },
            NonTerminal.CHARS: {
                (Terminal.CHAR, '"'): Terminal.EMPTY,
                Terminal.CHAR: NonTerminal.CHARS,
                Terminal.ZERO: NonTerminal.CHARS,
                Terminal.ONE_NINE: NonTerminal.CHARS,
                (Terminal.CHAR, '\\'): NonTerminal.ESCAPE,
            },
            NonTerminal.CHARS_TAIL: {
                (Terminal.CHAR, '"'): Terminal.EMPTY,
                Terminal.CHAR: NonTerminal.CHARS,
                Terminal.ZERO: NonTerminal.CHARS,
                Terminal.ONE_NINE: NonTerminal.CHARS,
                (Terminal.CHAR, '\\'): NonTerminal.ESCAPE,
            },
            NonTerminal.ESCAPE_TAIL: {
                Terminal.ESCAPE_SPECIAL: NonTerminal.ESCAPE_TAIL,
                Terminal.ESCAPE_HEX: NonTerminal.ESCAPE_HEX_TAIL,
            },
        }
        self.rules = {
            NonTerminal.ELEMENTS: [NonTerminal.VALUE, NonTerminal.ELEMENTS_TAIL],
            NonTerminal.ELEMENTS_TAIL: [(Terminal.CHAR, ','), NonTerminal.VALUE, NonTerminal.ELEMENTS_TAIL],

            NonTerminal.MEMBER: [NonTerminal.VALUE_STRING, (Terminal.CHAR, ':'), NonTerminal.VALUE],
            NonTerminal.MEMBERS: [NonTerminal.MEMBER, NonTerminal.MEMBERS_TAIL],
            NonTerminal.MEMBERS_TAIL: [(Terminal.CHAR, ','), NonTerminal.MEMBER, NonTerminal.MEMBERS_TAIL],

            NonTerminal.VALUE: [NonTerminal.VALUE],
            NonTerminal.VALUE_OBJECT: [(Terminal.CHAR, '{'), NonTerminal.MEMBERS, (Terminal.CHAR, '}')],
            NonTerminal.VALUE_ARRAY: [(Terminal.CHAR, '['), NonTerminal.ELEMENTS, (Terminal.CHAR, ']')],
            NonTerminal.VALUE_STRING: [(Terminal.CHAR, '"'), NonTerminal.CHARS, (Terminal.CHAR, '"')],

            NonTerminal.CHARS: [Terminal.CHAR, NonTerminal.CHARS_TAIL],

            NonTerminal.VALUE_NUMBER: [NonTerminal.INTEGER, NonTerminal.FRACTION, NonTerminal.EXPONENT],
            NonTerminal.INTEGER_DIGIT: [NonTerminal.DIGIT, NonTerminal.DIGITS],
            NonTerminal.INTEGER_ONE_NINE: [Terminal.ONE_NINE, NonTerminal.DIGITS],
            NonTerminal.INTEGER_MINUS: [(Terminal.CHAR, '-'), NonTerminal.INTEGER_MINUS_TAIL],
            NonTerminal.INTEGER_MINUS_DIGIT: [NonTerminal.DIGIT],
            NonTerminal.INTEGER_MINUS_ONE_NINE: [Terminal.ONE_NINE, NonTerminal.DIGITS],
            NonTerminal.FRACTION_TAIL: [(Terminal.CHAR, '.'), NonTerminal.DIGITS],
            NonTerminal.EXPONENT_E: [(Terminal.CHAR, 'E'), NonTerminal.SIGN, NonTerminal.DIGITS],
            NonTerminal.EXPONENT_e: [(Terminal.CHAR, 'e'), NonTerminal.SIGN, NonTerminal.DIGITS],

            NonTerminal.SIGN_MINUS: [(Terminal.CHAR, '-')],
            NonTerminal.SIGN_PLUS: [(Terminal.CHAR, '+')],

            NonTerminal.ESCAPE: [(Terminal.CHAR, '\\'), NonTerminal.ESCAPE_TAIL],
            NonTerminal.ESCAPE_TAIL: [Terminal.ESCAPE_SPECIAL, NonTerminal.CHARS_TAIL],
            NonTerminal.ESCAPE_HEX_TAIL: [Terminal.ESCAPE_SPECIAL, Terminal.HEX, Terminal.HEX, Terminal.HEX, Terminal.HEX,  NonTerminal.CHARS_TAIL],

            NonTerminal.NULL: [(Terminal.CHAR, 'n'),(Terminal.CHAR, 'u'), (Terminal.CHAR, 'l'), (Terminal.CHAR, 'l') ],
            NonTerminal.TRUE: [(Terminal.CHAR, 't'),(Terminal.CHAR, 'r'), (Terminal.CHAR, 'u'), (Terminal.CHAR, 'e') ],
            NonTerminal.FALSE: [(Terminal.CHAR, 'f'),(Terminal.CHAR, 'a'), (Terminal.CHAR, 'l'), (Terminal.CHAR, 's'), (Terminal.CHAR, 'e') ],

            Terminal.ZERO: [Terminal.ZERO],
            Terminal.ONE_NINE: [Terminal.ONE_NINE],

            Terminal.VALUE_NUMBER: [NonTerminal.DIGITS],
            Terminal.EMPTY: [],
        }
        self.ESCAPE_SPECIAL_CHARS = set(['"', '\\', '/', 'b', 'f', 'n', 'r', 't', 'u'])
        self.stack = [Terminal.END, NonTerminal.VALUE]

        ###
        ### TODO: convert into PYTHON data structure
        ### TODO: Make this into a library or module and use in another program
        ###
    def run(self, tokens : list[Tuple[Terminal, object]]):
        logger.debug(tokens)
        position = 0
        while self.stack:
            svalue = self.stack.pop()
            token = tokens[position]
            if isinstance(svalue, Term) or (isinstance(svalue, Tuple) and isinstance(svalue[0], Term)):
                logger.debug(f"{svalue = !s}, {token = !s}")
                if svalue != token[0]:
                    if token[0] == Terminal.ZERO or token[0] == Terminal.ONE_NINE:
                        token = (Terminal.CHAR, token[1])
                    if svalue == Terminal.ESCAPE_SPECIAL and token[1] in self.ESCAPE_SPECIAL_CHARS:
                        token = (Terminal.ESCAPE_SPECIAL, token[1])
                    if svalue == Terminal.HEX:
                        if 'a' <= token[1] <= 'f' or \
                           'A' <= token[1] <= 'F' or \
                           '0' <= token[1] <= '9':
                            token = (Terminal.HEX, token[1])

                logger.debug(f"{svalue = !s}, {token = !s}")
                if svalue == token[0] or svalue == token:
                    position += 1
                    logger.debug(f"pop {svalue}")
                    if token[0] == Terminal.END:
                        logger.info("input accepted")
                else:
                    raise ValueError("bad term on input:", str(token))
            elif isinstance(svalue, Rule):
                if svalue == NonTerminal.ESCAPE_TAIL:
                    if token[1] in self.ESCAPE_SPECIAL_CHARS:
                        if token[1] == 'u': #hex
                            token = (Terminal.ESCAPE_HEX, token[1])
                        else:
                            token = (Terminal.ESCAPE_SPECIAL, token[1])

                logger.debug(f"{svalue = !s}, {token = !s}")
                if token in self.table[svalue]:
                    rule = self.table[svalue][token]
                elif token[0] in self.table[svalue]:
                    rule = self.table[svalue][token[0]]
                else:
                    raise ValueError(f"no rule found: svalue: {str(svalue)} token: {str(token)}")
                logger.debug(f"{rule = }")
                for r in reversed(self.rules[rule]):
                    self.stack.append(r)
            logger.debug("stacks:")
            logger.debug(self.stack)


class JSON_Parser():
    @staticmethod
    def parse(raw_json : str) -> bool:
        my_lexer = Lexer(raw_json)
        my_syntax_analyzer = SyntaticalAnalysis()

        logger.debug(my_syntax_analyzer.run(list(my_lexer.lexical_analysis())))
        return True

#logger.setLevel(logging.DEBUG)
if __name__ =="__main__":
    # JSON_Parser.parse("""
    # "abc"
    # """)
    # sys.exit(0)

    if len(sys.argv) < 2:
        print("Enter filename to parse")
        sys.exit(1)

    contents = []
    with open(sys.argv[1]) as f:
        contents = f.read()
        logger.debug(contents)

    JSON_Parser.parse(contents)
