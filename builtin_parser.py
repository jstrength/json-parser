#!/usr/bin/env python3

import json
import sys

contents = []
with open(sys.argv[1]) as f:
    contents = f.read()

print(json.loads(contents))
