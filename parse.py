#!/usr/bin/env python3

from collections.abc import Generator
from enum import Enum, auto
from typing import Tuple
import re
import codecs
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)
#logger.setLevel(logging.DEBUG)

WS = [' ', '\u0020', '\u000A', '\u000D', '\u0009']

# Handle stupid mixings of unicode and escaped unicode characaters
# https://stackoverflow.com/questions/4020539/process-escape-sequences-in-a-string-in-python
ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)

def decode_escapes(s):
    def decode_match(match):
        try:
            return codecs.decode(match.group(0), 'unicode-escape')
        except UnicodeDecodeError:
            # In case we matched the wrong thing after a double-backslash
            return match.group(0)

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)

########################################

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
    NEW_VALUE = auto()
    VALUE_END = auto()
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
    WS = auto()

    def __str__(self):
        return f"T_{self.name}"

class Lexer():

    def __init__(self, input_string):
        self.idx = 0
        self.input_string = input_string

    def lexical_analysis(self) -> Generator[Tuple[Terminal,object]]:

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Lexical Analysis (LEXXER)")

        while self.idx < len(self.input_string):
            c = self.input_string[self.idx]

            if c in WS + ['\n']:
                self.idx += 1  # ignore
                yield (Terminal.CHAR, ' ')
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
                raise ValueError(f"got invalid input {c}")
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
                (Terminal.CHAR, ']'): Terminal.EMPTY,
            },
            NonTerminal.ELEMENTS_TAIL: {
                (Terminal.CHAR, ','): NonTerminal.ELEMENTS_TAIL,
                (Terminal.CHAR, ']'): Terminal.EMPTY,
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
                (Terminal.CHAR, ' '): NonTerminal.VALUE,
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
                (Terminal.CHAR, '}'): Terminal.EMPTY,
            },
            NonTerminal.MEMBERS_TAIL: {
                (Terminal.CHAR, ','): NonTerminal.MEMBERS_TAIL,
                (Terminal.CHAR, '}'): Terminal.EMPTY,
            },
            NonTerminal.MEMBER: {
                (Terminal.CHAR, '"'): NonTerminal.MEMBER,
                (Terminal.CHAR, ' '): NonTerminal.MEMBER
            },
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
                (Terminal.CHAR, ' '): Terminal.EMPTY,
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
                (Terminal.CHAR, ' '): Terminal.EMPTY,
                Terminal.END: Terminal.EMPTY,
            },
            NonTerminal.EXPONENT: {
                (Terminal.CHAR, 'E'): NonTerminal.EXPONENT_E,
                (Terminal.CHAR, 'e'): NonTerminal.EXPONENT_e,
                (Terminal.CHAR, ','): Terminal.EMPTY,
                (Terminal.CHAR, '}'): Terminal.EMPTY,
                (Terminal.CHAR, ']'): Terminal.EMPTY,
                (Terminal.CHAR, ' '): Terminal.EMPTY,
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
            NonTerminal.WS: {
                (Terminal.CHAR, ' '): NonTerminal.WS,
                Terminal.ONE_NINE: Terminal.EMPTY,
                Terminal.ZERO: Terminal.EMPTY,
                Terminal.END: Terminal.EMPTY,
                Terminal.CHAR: Terminal.EMPTY,
            },
        }
        self.rules = {
            NonTerminal.ELEMENTS: [NonTerminal.VALUE, NonTerminal.WS, NonTerminal.ELEMENTS_TAIL],
            NonTerminal.ELEMENTS_TAIL: [NonTerminal.WS, (Terminal.CHAR, ','), NonTerminal.VALUE,  NonTerminal.ELEMENTS_TAIL],

            NonTerminal.MEMBER: [NonTerminal.WS, NonTerminal.VALUE_STRING, NonTerminal.WS, (Terminal.CHAR, ':'), NonTerminal.VALUE],
            NonTerminal.MEMBERS: [NonTerminal.MEMBER, NonTerminal.MEMBERS_TAIL],
            NonTerminal.MEMBERS_TAIL: [(Terminal.CHAR, ','), NonTerminal.MEMBER, NonTerminal.MEMBERS_TAIL],

            NonTerminal.VALUE: [NonTerminal.WS, NonTerminal.VALUE, NonTerminal.WS],
            NonTerminal.VALUE_OBJECT: [(Terminal.NEW_VALUE, list), (Terminal.CHAR, '{'), NonTerminal.WS, NonTerminal.MEMBERS, (Terminal.CHAR, '}'), (Terminal.VALUE_END, NonTerminal.VALUE_OBJECT)],
            NonTerminal.VALUE_ARRAY: [(Terminal.NEW_VALUE, list), (Terminal.CHAR, '['), NonTerminal.WS, NonTerminal.ELEMENTS, (Terminal.CHAR, ']'), (Terminal.VALUE_END, NonTerminal.VALUE_ARRAY)],
            NonTerminal.VALUE_STRING: [(Terminal.NEW_VALUE, str), (Terminal.CHAR, '"'), NonTerminal.CHARS, (Terminal.CHAR, '"'), (Terminal.VALUE_END, NonTerminal.VALUE_STRING)],

            NonTerminal.CHARS: [Terminal.CHAR, NonTerminal.CHARS_TAIL],

            NonTerminal.VALUE_NUMBER: [(Terminal.NEW_VALUE, str), NonTerminal.INTEGER, NonTerminal.FRACTION, NonTerminal.EXPONENT, (Terminal.VALUE_END, NonTerminal.VALUE_NUMBER)],
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

            NonTerminal.NULL: [(Terminal.NEW_VALUE, None), (Terminal.CHAR, 'n'),(Terminal.CHAR, 'u'), (Terminal.CHAR, 'l'), (Terminal.CHAR, 'l'), (Terminal.VALUE_END, None) ],
            NonTerminal.TRUE: [(Terminal.NEW_VALUE, True), (Terminal.CHAR, 't'),(Terminal.CHAR, 'r'), (Terminal.CHAR, 'u'), (Terminal.CHAR, 'e'), (Terminal.VALUE_END, None) ],
            NonTerminal.FALSE: [(Terminal.NEW_VALUE, False), (Terminal.CHAR, 'f'),(Terminal.CHAR, 'a'), (Terminal.CHAR, 'l'), (Terminal.CHAR, 's'), (Terminal.CHAR, 'e'), (Terminal.VALUE_END, None) ],

            NonTerminal.WS: [(Terminal.CHAR, ' '), NonTerminal.WS],

            Terminal.ZERO: [Terminal.ZERO],
            Terminal.ONE_NINE: [Terminal.ONE_NINE],

            Terminal.VALUE_NUMBER: [NonTerminal.DIGITS],
            Terminal.EMPTY: [],
        }
        self.ESCAPE_SPECIAL_CHARS = set(['"', '\\', '/', 'b', 'f', 'n', 'r', 't', 'u'])
        self.stack = [Terminal.END, NonTerminal.WS, NonTerminal.VALUE]
        self.values_stack = []

    def add_value(self, value1, value2):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"adding value {value1} and {value2}")
        match value1.__class__.__name__:
            case "str":
                value1 += value2
            case "list":
                value1.append(value2)
        return value1

    def convert_list_to_dict(self, list_value):
        l = iter(list_value)
        return dict(zip(l, l))

        ###
        ### TODO: convert into PYTHON data structure
        ### TODO: Make this into a library or module and use in another program
        ###
    def run(self, tokens : list[Tuple[Terminal, object]]):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(tokens)
        position = 0
        while self.stack:
            svalue = self.stack.pop()
            token = tokens[position]
            if isinstance(svalue, Term) or (isinstance(svalue, Tuple) and isinstance(svalue[0], Term)):
                if logger.isEnabledFor(logging.DEBUG):
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

                # Handle conversion to python data structure
                if isinstance(svalue, Tuple):
                    if svalue[0] == Terminal.VALUE_END:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"********** adding VALUE END {svalue} -- {self.values_stack}")
                        if svalue[1] == NonTerminal.VALUE_NUMBER:
                            value = self.values_stack.pop()
                            if '.' in value or 'e' in value:
                                self.values_stack.append(float(value))
                            else:
                                self.values_stack.append(int(value))
                        if svalue[1] == NonTerminal.VALUE_STRING:
                            value = self.values_stack.pop()
                            self.values_stack.append(decode_escapes(value))
                        if svalue[1] == NonTerminal.VALUE_OBJECT:
                            value = self.values_stack.pop()
                            self.values_stack.append(self.convert_list_to_dict(value))
                        if len(self.values_stack) > 1:
                            value = self.values_stack.pop()
                            self.add_value(self.values_stack[-1], value)
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"********** add VALUE END {self.values_stack}")
                        continue
                    elif svalue[0] == Terminal.NEW_VALUE:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"********** adding NEW VALUE {self.values_stack}")
                        if callable(svalue[1]):
                            self.values_stack.append(svalue[1]())
                        else:
                            self.values_stack.append(svalue[1])
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"********** adding NEW VALUE {self.values_stack}")
                        continue
                if not isinstance(svalue, Tuple) or svalue[1] in ['-', '+', 'e', 'E', '.', '\\']:
                    if isinstance(self.values_stack[-1], str):
                        if token[0] in [Terminal.CHAR, Terminal.ONE_NINE, Terminal.ZERO, Terminal.HEX, Terminal.ESCAPE_SPECIAL]:
                            if logger.isEnabledFor(logging.DEBUG):
                                logger.debug(f"********** adding char {token}")
                            value = self.values_stack.pop()
                            new_value = self.add_value(value, token[1])
                            self.values_stack.append(new_value)

                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"TERM: {svalue = !s}, {token = !s}")
                if svalue == token[0] or svalue == token:
                    position += 1
                    if logger.isEnabledFor(logging.DEBUG):
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

                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"RULE: {svalue = !s}, {token = !s}")
                if token in self.table[svalue]:
                    rule = self.table[svalue][token]
                elif token[0] in self.table[svalue]:
                    rule = self.table[svalue][token[0]]
                else:
                    raise ValueError(f"no rule found: svalue: {str(svalue)} token: {str(token)}")
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"{rule = }")
                for r in reversed(self.rules[rule]):
                    self.stack.append(r)

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("stacks:")
                logger.debug(self.stack)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(self.values_stack)
        assert len(self.values_stack) == 1
        return self.values_stack[0]


class JSON_Parser():
    @staticmethod
    def parse(raw_json : str) -> object:
        my_lexer = Lexer(raw_json)
        my_syntax_analyzer = SyntaticalAnalysis()

        parsed_json_value = my_syntax_analyzer.run(list(my_lexer.lexical_analysis()))
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(parsed_json_value)
        return parsed_json_value

if __name__ =="__main__":
    # assert JSON_Parser.parse("""
    # ["abc", "wow", ["nested", "stuff"]]
    # """) == ["abc", "wow", ["nested", "stuff"]]
    # sys.exit(0)
    # json_example = """
    # "he said \\u8A12"
    # """
    # assert JSON_Parser.parse(json_example) == "he said 訒"
    # json_example = """
    # "he said \\u8A12"
    # """
    # JSON_Parser.parse(json_example)
    # sys.exit(0)


    # sys.argv.append('./5MB.json')

    if len(sys.argv) < 2:
        print("Enter filename to parse")
        sys.exit(1)

    contents = []
    with open(sys.argv[1]) as f:
        contents = f.read()
        #logger.debug(contents)

    print(JSON_Parser.parse(contents))
