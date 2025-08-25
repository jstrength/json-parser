#!/usr/bin/env python3

from collections.abc import Generator
from enum import Enum, auto
from sys import exit
from typing import Tuple

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
    STRING = auto()
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

        print("Lexical Analysis (LEXXER)")

        while self.idx < len(self.input_string):
            c = self.input_string[self.idx]
            if c in WS + ['\n']:
                self.idx += 1  # ignore
            elif c == '"':
                yield (Terminal.STRING, self.parse_string())
            elif c.isnumeric():
                self.idx += 1
                if c == '0':
                    yield (Terminal.ZERO, c)
                else:
                    yield (Terminal.ONE_NINE, c)
            elif c in ["t", "f", "n"]:
                if self.input_string[self.idx:self.idx + 4] == "true":
                    self.idx += 4
                    yield (Terminal.BOOLEAN, True)
                elif self.input_string[self.idx:self.idx + 5] == "false":
                    self.idx += 5
                    yield (Terminal.BOOLEAN, False)
                elif self.input_string[self.idx:self.idx + 4] == "null":
                    self.idx += 4
                    yield (Terminal.NULL, None)
                else:
                    print("got invalid input ", c)
                    exit(1)
                    yield (Terminal.INVALID, None)
            else:
                self.idx += 1
                match c:
                    case '{':
                        yield (Terminal.LCUR, None)
                    case '}':
                        yield (Terminal.RCUR, None)
                    case '[':
                        yield (Terminal.LBRAC, None)
                    case ']':
                        yield (Terminal.RBRAC, None)
                    case ':':
                        yield (Terminal.COLON, None)
                    case ',':
                        yield (Terminal.COMMA, None)
                    case '-':
                        yield (Terminal.MINUS, None)
                    case '+':
                        yield (Terminal.PLUS, None)
                    case '.':
                        yield (Terminal.PERIOD, None)
                    case 'e':
                        yield (Terminal.EXPONENT, None)
                    case 'E':
                        yield (Terminal.EXPONENT, None)
                    case _:
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
                Terminal.STRING: NonTerminal.VALUE,
                Terminal.BOOLEAN: NonTerminal.VALUE,
                Terminal.NULL: NonTerminal.VALUE,
                Terminal.MINUS: NonTerminal.VALUE,
                Terminal.ZERO: NonTerminal.VALUE,
                Terminal.ONE_NINE: NonTerminal.VALUE,
                Terminal.LCUR: NonTerminal.VALUE,
                Terminal.LBRAC: NonTerminal.VALUE,
            },
            NonTerminal.ELEMENTS: {
                Terminal.STRING: NonTerminal.ELEMENTS,
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
                Terminal.STRING: Terminal.VALUE_STRING,
                Terminal.MINUS: NonTerminal.VALUE_NUMBER,
                Terminal.ZERO: NonTerminal.VALUE_NUMBER,
                Terminal.ONE_NINE: NonTerminal.VALUE_NUMBER,
                Terminal.NULL: Terminal.VALUE_NULL,
            },
            NonTerminal.VALUE_ARRAY: {
                Terminal.RBRAC: Terminal.RBRAC
            },
            NonTerminal.MEMBERS: {
                Terminal.STRING: NonTerminal.MEMBERS,
                Terminal.COMMA: NonTerminal.MEMBERS,
                Terminal.RCUR: Terminal.EMPTY
            },
            NonTerminal.MEMBERS_TAIL: {
                Terminal.COMMA: NonTerminal.MEMBERS_TAIL,
                Terminal.RCUR: Terminal.EMPTY,
            },
            NonTerminal.MEMBER: {Terminal.STRING: NonTerminal.MEMBER},
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
        }
        self.rules = {
            NonTerminal.ELEMENT: [NonTerminal.VALUE],
            NonTerminal.ELEMENTS: [NonTerminal.ELEMENT, NonTerminal.ELEMENTS_TAIL],
            NonTerminal.ELEMENTS_TAIL: [Terminal.COMMA, NonTerminal.ELEMENT, NonTerminal.ELEMENTS_TAIL],

            NonTerminal.MEMBER: [Terminal.STRING, Terminal.COLON, NonTerminal.VALUE],
            NonTerminal.MEMBERS: [NonTerminal.MEMBER, NonTerminal.MEMBERS_TAIL],
            NonTerminal.MEMBERS_TAIL: [Terminal.COMMA, NonTerminal.MEMBER, NonTerminal.MEMBERS_TAIL],

            NonTerminal.VALUE: [NonTerminal.VALUE],
            NonTerminal.VALUE_OBJECT: [Terminal.LCUR, NonTerminal.MEMBERS, Terminal.RCUR],
            NonTerminal.VALUE_ARRAY: [Terminal.LBRAC, NonTerminal.ELEMENTS, Terminal.RBRAC],

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

            Terminal.ZERO: [Terminal.ZERO],
            Terminal.ONE_NINE: [Terminal.ONE_NINE],

            Terminal.VALUE_STRING: [Terminal.STRING],
            Terminal.VALUE_BOOLEAN: [Terminal.BOOLEAN],
            Terminal.VALUE_NUMBER: [NonTerminal.DIGITS],
            Terminal.VALUE_NULL: [Terminal.NULL],
            Terminal.EMPTY: [],
        }
        self.stack = [Terminal.END, NonTerminal.ELEMENT]

        ###
        ### TODO: review above rules and table
        ### TODO: write tests
        ### TODO: convert into PYTHON data structure
        ### TODO: Make this into a library or module and use in another program
        ###
    def run(self, tokens : list[Tuple[Terminal, object]]):
        print(tokens)
        position = 0
        while self.stack:
            svalue = self.stack.pop()
            token = tokens[position]
            if isinstance(svalue, Term):
                if svalue == token[0]:
                    position += 1
                    print("pop", svalue)
                    if token[0] == Terminal.END:
                        print("input accepted")
                else:
                    raise ValueError("bad term on input:", str(token))
            elif isinstance(svalue, Rule):
                print(f"{svalue = !s}, {token = !s}")
                rule = self.table[svalue][token[0]]
                print(f"{rule = }")
                for r in reversed(self.rules[rule]):
                    self.stack.append(r)
            print("stacks:", end=" ")
            print(*self.stack, sep=", ")


class JSON_Parser():
    @staticmethod
    def parse(raw_json : str) -> bool:
        my_lexer = Lexer(raw_json)
        my_syntax_analyzer = SyntaticalAnalysis()

        print(my_syntax_analyzer.run(list(my_lexer.lexical_analysis())))
        return True

if __name__ == "__main__":
    contents = []
    with open("./simple_example.json") as f:
        contents = f.read()
        print(contents)
    JSON_Parser.parse(contents)
