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
    LCUR = auto()
    RCUR = auto()
    LBRAC = auto()
    RBRAC = auto()
    COLON = auto()
    COMMA = auto()
    MINUS = auto()
    PLUS = auto()
    PERIOD = auto()
    ZERO = auto()
    ONE_NINE = auto()
    CHAR = auto()
    QUOTE = auto()
    BACKSLASH = auto()
    EXPONENT = auto()
    BOOLEAN = auto()
    NULL = auto()
    INVALID = auto()
    END = auto()
    VALUE_STRING = auto()
    VALUE_NUMBER = auto()
    VALUE_BOOLEAN = auto()
    VALUE_NULL = auto()
    EMPTY = auto()
    ESCAPE_SPECIAL = auto()

    def __str__(self):
        return f"T_{self.name}"


class NonTerminal(Rule):
    """Non Terminals used during syntatical analysis."""
    ELEMENT = auto()
    ELEMENTS = auto()
    ELEMENTS_TAIL = auto()
    VALUE = auto()
    VALUE_OBJECT = auto()
    VALUE_ARRAY = auto()
    VALUE_NUMBER = auto()
    MEMBER = auto()
    MEMBERS = auto()
    MEMBERS_TAIL = auto()
    FRACTION = auto()
    FRACTION_TAIL = auto()
    EXPONENT = auto()
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
    STRING = auto()
    CHARS = auto()
    CHARS_TAIL = auto()
    ESCAPE = auto()

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
                continue
            elif c.isnumeric():
                self.idx += 1
                if c == '0':
                    yield (Terminal.ZERO, c)
                else:
                    yield (Terminal.ONE_NINE, c)
                continue
            elif c in ["t", "f", "n"]:
                if self.input_string[self.idx:self.idx + 4] == "true":
                    self.idx += 4
                    yield (Terminal.BOOLEAN, True)
                    continue
                elif self.input_string[self.idx:self.idx + 5] == "false":
                    self.idx += 5
                    yield (Terminal.BOOLEAN, False)
                    continue
                elif self.input_string[self.idx:self.idx + 4] == "null":
                    self.idx += 4
                    yield (Terminal.NULL, None)
                    continue

            if c >= '\u0020' and c <= '\U0010FFFF':
                self.idx += 1
                match c:
                    case '"':
                        yield (Terminal.QUOTE, c)
                    case '\\':
                        yield (Terminal.BACKSLASH, c)
                    case '{':
                        yield (Terminal.LCUR, c)
                    case '}':
                        yield (Terminal.RCUR, c)
                    case '[':
                        yield (Terminal.LBRAC, c)
                    case ']':
                        yield (Terminal.RBRAC, c)
                    case ':':
                        yield (Terminal.COLON, c)
                    case ',':
                        yield (Terminal.COMMA, c)
                    case '-':
                        yield (Terminal.MINUS, c)
                    case '+':
                        yield (Terminal.PLUS, c)
                    case '.':
                        yield (Terminal.PERIOD, c)
                    case 'e':
                        yield (Terminal.EXPONENT, c)
                    case 'E':
                        yield (Terminal.EXPONENT, c)
                    case _:
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
            NonTerminal.ELEMENT: {
                Terminal.BOOLEAN: NonTerminal.VALUE,
                Terminal.NULL: NonTerminal.VALUE,
                Terminal.QUOTE: NonTerminal.VALUE,
                Terminal.MINUS: NonTerminal.VALUE,
                Terminal.ZERO: NonTerminal.VALUE,
                Terminal.ONE_NINE: NonTerminal.VALUE,
                Terminal.LCUR: NonTerminal.VALUE,
                Terminal.LBRAC: NonTerminal.VALUE,
            },
            NonTerminal.ELEMENTS: {
                Terminal.QUOTE: NonTerminal.ELEMENTS,
                Terminal.ZERO: NonTerminal.ELEMENTS,
                Terminal.ONE_NINE: NonTerminal.ELEMENTS,
                Terminal.LCUR: NonTerminal.ELEMENTS,
                Terminal.COMMA: NonTerminal.ELEMENTS_TAIL,
                Terminal.RBRAC: Terminal.EMPTY
            },
            NonTerminal.ELEMENTS_TAIL: {
                Terminal.COMMA: NonTerminal.ELEMENTS_TAIL,
                Terminal.RBRAC: Terminal.EMPTY
            },
            NonTerminal.VALUE: {
                Terminal.LCUR: NonTerminal.VALUE_OBJECT,
                Terminal.LBRAC: NonTerminal.VALUE_ARRAY,
                Terminal.BOOLEAN: Terminal.VALUE_BOOLEAN,
                Terminal.QUOTE: Terminal.VALUE_STRING,
                Terminal.MINUS: NonTerminal.VALUE_NUMBER,
                Terminal.ZERO: NonTerminal.VALUE_NUMBER,
                Terminal.ONE_NINE: NonTerminal.VALUE_NUMBER,
                Terminal.NULL: Terminal.VALUE_NULL,
            },
            NonTerminal.VALUE_ARRAY: {
                Terminal.RBRAC: Terminal.RBRAC
            },
            NonTerminal.MEMBERS: {
                Terminal.QUOTE: NonTerminal.MEMBERS,
                Terminal.COMMA: NonTerminal.MEMBERS,
                Terminal.RCUR: Terminal.EMPTY
            },
            NonTerminal.MEMBERS_TAIL: {
                Terminal.COMMA: NonTerminal.MEMBERS_TAIL,
                Terminal.RCUR: Terminal.EMPTY,
            },
            NonTerminal.MEMBER: {Terminal.QUOTE: NonTerminal.MEMBER},
            NonTerminal.INTEGER: {
                NonTerminal.DIGIT: NonTerminal.INTEGER_DIGIT,
                Terminal.ONE_NINE: NonTerminal.INTEGER_ONE_NINE,
                Terminal.MINUS: NonTerminal.INTEGER_MINUS,
            },
            NonTerminal.INTEGER_MINUS_TAIL: {
                Terminal.ONE_NINE: NonTerminal.INTEGER_MINUS_ONE_NINE,
            },
            NonTerminal.DIGITS: {
                Terminal.ZERO: NonTerminal.INTEGER_DIGIT,
                Terminal.ONE_NINE: NonTerminal.INTEGER_DIGIT,
                Terminal.PERIOD: Terminal.EMPTY,
                Terminal.COMMA: Terminal.EMPTY,
                Terminal.RCUR: Terminal.EMPTY,
                Terminal.RBRAC: Terminal.EMPTY,
                Terminal.EXPONENT: Terminal.EMPTY,
                Terminal.END: Terminal.EMPTY,
            },
            NonTerminal.DIGIT: {
                Terminal.ZERO: Terminal.ZERO,
                Terminal.ONE_NINE: Terminal.ONE_NINE,
            },
            NonTerminal.FRACTION: {
                Terminal.PERIOD: NonTerminal.FRACTION_TAIL,
                Terminal.COMMA: Terminal.EMPTY,
                Terminal.RCUR: Terminal.EMPTY,
                Terminal.RBRAC: Terminal.EMPTY,
                Terminal.EXPONENT: Terminal.EMPTY,
                Terminal.END: Terminal.EMPTY,
            },
            NonTerminal.EXPONENT: {
                Terminal.EXPONENT: NonTerminal.EXPONENT,
                Terminal.COMMA: Terminal.EMPTY,
                Terminal.RCUR: Terminal.EMPTY,
                Terminal.RBRAC: Terminal.EMPTY,
                Terminal.END: Terminal.EMPTY,
            },
            NonTerminal.SIGN: {
                Terminal.ZERO: Terminal.EMPTY,
                Terminal.ONE_NINE: Terminal.EMPTY,
                Terminal.MINUS: NonTerminal.SIGN_MINUS,
                Terminal.PLUS: NonTerminal.SIGN_PLUS,
            },
            NonTerminal.CHARS: {
                Terminal.QUOTE: Terminal.EMPTY,
                Terminal.CHAR: NonTerminal.CHARS,
                Terminal.BACKSLASH: NonTerminal.ESCAPE,
            },
            NonTerminal.CHARS_TAIL: {
                Terminal.QUOTE: Terminal.EMPTY,
                Terminal.CHAR: NonTerminal.CHARS,
                Terminal.EXPONENT: NonTerminal.CHARS,
                Terminal.BACKSLASH: NonTerminal.ESCAPE,
            },
            NonTerminal.STRING: {
                Terminal.QUOTE: NonTerminal.STRING,
            },
        }
        self.rules = {
            NonTerminal.ELEMENT: [NonTerminal.VALUE],
            NonTerminal.ELEMENTS: [NonTerminal.ELEMENT, NonTerminal.ELEMENTS_TAIL],
            NonTerminal.ELEMENTS_TAIL: [Terminal.COMMA, NonTerminal.ELEMENT, NonTerminal.ELEMENTS_TAIL],

            NonTerminal.MEMBER: [NonTerminal.STRING, Terminal.COLON, NonTerminal.VALUE],
            NonTerminal.MEMBERS: [NonTerminal.MEMBER, NonTerminal.MEMBERS_TAIL],
            NonTerminal.MEMBERS_TAIL: [Terminal.COMMA, NonTerminal.MEMBER, NonTerminal.MEMBERS_TAIL],

            NonTerminal.VALUE: [NonTerminal.VALUE],
            NonTerminal.VALUE_OBJECT: [Terminal.LCUR, NonTerminal.MEMBERS, Terminal.RCUR],
            NonTerminal.VALUE_ARRAY: [Terminal.LBRAC, NonTerminal.ELEMENTS, Terminal.RBRAC],

            NonTerminal.STRING: [Terminal.QUOTE, NonTerminal.CHARS, Terminal.QUOTE],
            NonTerminal.CHARS: [Terminal.CHAR, NonTerminal.CHARS_TAIL],

            NonTerminal.VALUE_NUMBER: [NonTerminal.INTEGER, NonTerminal.FRACTION, NonTerminal.EXPONENT],
            NonTerminal.INTEGER_DIGIT: [NonTerminal.DIGIT, NonTerminal.DIGITS],
            NonTerminal.INTEGER_ONE_NINE: [Terminal.ONE_NINE, NonTerminal.DIGITS],
            NonTerminal.INTEGER_MINUS: [Terminal.MINUS, NonTerminal.INTEGER_MINUS_TAIL],
            NonTerminal.INTEGER_MINUS_DIGIT: [NonTerminal.DIGIT],
            NonTerminal.INTEGER_MINUS_ONE_NINE: [Terminal.ONE_NINE, NonTerminal.DIGITS],
            NonTerminal.FRACTION_TAIL: [Terminal.PERIOD, NonTerminal.DIGITS],
            NonTerminal.EXPONENT: [Terminal.EXPONENT, NonTerminal.SIGN, NonTerminal.DIGITS],

            NonTerminal.SIGN_MINUS: [Terminal.MINUS],
            NonTerminal.SIGN_PLUS: [Terminal.PLUS],

            NonTerminal.ESCAPE: [Terminal.BACKSLASH, Terminal.ESCAPE_SPECIAL, NonTerminal.CHARS_TAIL],

            Terminal.ZERO: [Terminal.ZERO],
            Terminal.ONE_NINE: [Terminal.ONE_NINE],

            Terminal.VALUE_STRING: [NonTerminal.STRING],
            Terminal.VALUE_BOOLEAN: [Terminal.BOOLEAN],
            Terminal.VALUE_NUMBER: [NonTerminal.DIGITS],
            Terminal.VALUE_NULL: [Terminal.NULL],
            Terminal.EMPTY: [],
        }
        self.SPECIAL_CHARS = set(['"', '\\', '{', '}', '[', ']', ':', ',', '-', '+', '.', 'e', 'E',])
        self.ESCAPE_SPECIAL_CHARS = set(['"', '\\', '/', 'b', 'f', 'n', 'r', 't']) # TODO: Add u and hex support
        self.stack = [Terminal.END, NonTerminal.ELEMENT]

        ###
        ### TODO: review above rules and table
        ### TODO: write tests
        ### TODO: convert into PYTHON data structure
        ### TODO: Make this into a library or module and use in another program
        ###
    def run(self, tokens : list[Tuple[Terminal, object]]):
        logger.debug(tokens)
        position = 0
        while self.stack:
            svalue = self.stack.pop()
            token = tokens[position]
            if isinstance(svalue, Term):
                # if svalue != token[0] and token[1] in self.CHAR_TO_SPECIAL_TERM:
                #     print("SPECIAL REPLACE")
                #     token = self.CHAR_TO_SPECIAL_TERM[token[1]]
                #
                logger.debug(f"{svalue = !s}, {token = !s}")
                if svalue != token[0]:
                    if token[1] in self.SPECIAL_CHARS:
                        token = (Terminal.CHAR, token[1])
                    if svalue == Terminal.ESCAPE_SPECIAL and token[1] in self.ESCAPE_SPECIAL_CHARS:
                        token = (Terminal.ESCAPE_SPECIAL, token[1])

                if svalue == token[0]:
                    position += 1
                    logger.debug(f"pop {svalue}")
                    if token[0] == Terminal.END:
                        logger.info("input accepted")
                else:
                    raise ValueError("bad term on input:", str(token))
            elif isinstance(svalue, Rule):
                # if token[1] in self.CHAR_TO_SPECIAL_TERM and self.CHAR_TO_SPECIAL_TERM[token[1]][0] in self.table[svalue]:
                #     print("SPECIAL REPLACE")
                #     token = self.CHAR_TO_SPECIAL_TERM[token[1]]
                #
                # if svalue == NonTerminal.ESCAPE_TAIL:
                #     if token[1] in self.ESCAPE_SPECIAL_CHARS:
                #         token = (Terminal.ESCAPE_SPECIAL, token[1])

                logger.debug(f"{svalue = !s}, {token = !s}")
                rule = self.table[svalue][token[0]]
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

logger.setLevel(logging.DEBUG)
if __name__ =="__main__":
    # JSON_Parser.parse("""
    #     {
    #         "a": ["abc", true, false, null, 5, {"testing": "nesting"}, [1,2,3]]
    #     }
    # """)
    JSON_Parser.parse("""
    "a\\"ok\\"bc"
    """)
    sys.exit(0)

    if len(sys.argv) < 2:
        print("Enter filename to parse")
        sys.exit(1)

    contents = []
    with open(sys.argv[1]) as f:
        contents = f.read()
        logger.debug(contents)

    JSON_Parser.parse(contents)
