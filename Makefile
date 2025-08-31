##
# JSON Parser
#
# @file
# @version 0.1
all: parser

parser:
	python parse.py

test:
	python -m pytest -v test_parser.py

# end
