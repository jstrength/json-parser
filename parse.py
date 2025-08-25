from collections.abc import Generator
from enum import Enum, auto
from sys import exit
from typing import Tuple

WS = [' ', '0x20', '0x0A', '0x0D', '0x09']

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
    NUMB = auto()
    STRING = auto()
    BOOLEAN = auto()
    NULL = auto()
    INVALID = auto()
    END = auto()
    VALUE_STRING = auto()
    VALUE_NUMB = auto()
    VALUE_BOOLEAN = auto()
    VALUE_NULL = auto()
    EMPTY = auto()

    def __str__(self):
        return f"T_{self.name}"


class NonTerminal(Rule):
    """Non Terminals used during syntatical analysis."""
    JSON = auto()
    ELEMENT = auto()
    ELEMENTS = auto()
    ELEMENTS_TAIL = auto()
    VALUE = auto()
    VALUE_OBJECT = auto()
    VALUE_ARRAY = auto()
    MEMBER = auto()
    MEMBERS = auto()
    MEMBERS_TAIL = auto()

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

    def parse_number(self) -> int:
        curr_numb = ""

        while self.input_string[self.idx].isnumeric():
            curr_numb += self.input_string[self.idx]
            self.idx += 1

        return int(curr_numb)

    def lexical_analysis(self) -> Generator[Tuple[Terminal,object]]:

        print("Lexical Analysis (LEXXER)")

        while self.idx < len(self.input_string):
            c = self.input_string[self.idx]
            if c in WS + ['\n']:
                self.idx += 1  # ignore
            elif c == '"':
                yield (Terminal.STRING, self.parse_string())
            elif c.isnumeric():
                yield (Terminal.NUMB, self.parse_number())
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
            NonTerminal.JSON: {Terminal.LCUR: NonTerminal.VALUE},
            NonTerminal.ELEMENT: {
                Terminal.STRING: NonTerminal.VALUE,
                Terminal.BOOLEAN: NonTerminal.VALUE,
                Terminal.NULL: Terminal.VALUE_NULL,
                Terminal.NUMB: NonTerminal.VALUE,
                Terminal.LCUR: NonTerminal.VALUE_OBJECT,
                Terminal.LBRAC: NonTerminal.VALUE_ARRAY,
            },
            NonTerminal.ELEMENTS: {
                Terminal.STRING: NonTerminal.ELEMENTS,
                Terminal.NUMB: NonTerminal.ELEMENTS,
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
                Terminal.NUMB: Terminal.VALUE_NUMB,
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
        }
        self.rules = {
            NonTerminal.JSON: [NonTerminal.ELEMENT],

            NonTerminal.ELEMENT: [NonTerminal.VALUE],
            NonTerminal.ELEMENTS: [NonTerminal.ELEMENT, NonTerminal.ELEMENTS_TAIL],
            NonTerminal.ELEMENTS_TAIL: [Terminal.COMMA, NonTerminal.ELEMENT, NonTerminal.ELEMENTS_TAIL],

            NonTerminal.MEMBER: [Terminal.STRING, Terminal.COLON, NonTerminal.VALUE],
            NonTerminal.MEMBERS: [NonTerminal.MEMBER, NonTerminal.MEMBERS_TAIL],
            NonTerminal.MEMBERS_TAIL: [Terminal.COMMA, NonTerminal.MEMBER, NonTerminal.MEMBERS_TAIL],

            NonTerminal.VALUE: [NonTerminal.VALUE],
            NonTerminal.VALUE_OBJECT: [Terminal.LCUR, NonTerminal.MEMBERS, Terminal.RCUR],
            NonTerminal.VALUE_ARRAY: [Terminal.LBRAC, NonTerminal.ELEMENTS, Terminal.RBRAC],

            Terminal.VALUE_STRING: [Terminal.STRING],
            Terminal.VALUE_BOOLEAN: [Terminal.BOOLEAN],
            Terminal.VALUE_NUMB: [Terminal.NUMB],
            Terminal.VALUE_NULL: [Terminal.NULL],
            Terminal.EMPTY: [],
        }
        self.stack = [Terminal.END, NonTerminal.JSON]

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


contents = []
with open("simple_example.json") as f:
    contents = f.read()
    print(contents)

my_lexer = Lexer(contents)
my_syntax_analyzer = SyntaticalAnalysis()

print(my_syntax_analyzer.run(list(my_lexer.lexical_analysis())))
