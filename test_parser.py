#!/usr/bin/env python3

import pytest # type: ignore

from parse import JSON_Parser


def test_object():
    json_example = """
    {
        "abc": 123
    }
    """
    assert JSON_Parser.parse(json_example)

def test_weird_spaces_object():
    json_example = """
    {
    \u0020
    \u000A
    \u000D
    \u0009
    }
    """
    assert JSON_Parser.parse(json_example)

def test_escaped_string():
    json_example = """
    "he said \\"hello\\""
    """
    assert JSON_Parser.parse(json_example)

def test_escaped_hex_string():
    json_example = """
    "he said \\u8A12"
    """
    assert JSON_Parser.parse(json_example)

def test_escaped_bad_hex_string():
    json_example = """
    "he said \\u8Z12"
    """
    with pytest.raises(ValueError):
        JSON_Parser.parse(json_example)

def test_empty_object():
    json_example = """
    {
    }
    """
    assert JSON_Parser.parse(json_example)

def test_array():
    json_example = """
    [
        "abc", 123
    ]
    """
    assert JSON_Parser.parse(json_example)

def test_empty_array():
    json_example = """
    [
    ]
    """
    assert JSON_Parser.parse(json_example)

def test_number():
    json_example = """
        123
    """
    assert JSON_Parser.parse(json_example)

def test_negative_number():
    json_example = """
        -123
    """
    assert JSON_Parser.parse(json_example)

def test_fract():
    json_example = """
        123.123
    """
    assert JSON_Parser.parse(json_example)

def test_negative_fract():
    json_example = """
        -123.123
    """
    assert JSON_Parser.parse(json_example)

def test_exponent():
    json_example = """
        123e23
    """
    assert JSON_Parser.parse(json_example)

def test_fraction_exponent():
    json_example = """
        123.123e23
    """
    assert JSON_Parser.parse(json_example)

def test_fraction_sign_exponent():
    json_example = """
        123.123e-23
    """
    assert JSON_Parser.parse(json_example)

def test_plus_sign_exponent():
    json_example = """
        123e+23
    """
    assert JSON_Parser.parse(json_example)

def test_minus_sign_exponent():
    json_example = """
        123e-23
    """
    assert JSON_Parser.parse(json_example)

def test_string():
    json_example = """
    "abc"
    """
    assert JSON_Parser.parse(json_example)

def test_null():
    json_example = """
    null
    """
    assert JSON_Parser.parse(json_example)

def test_bool():
    json_example = """
    true
    """
    assert JSON_Parser.parse(json_example)

def test_nesting():
    json_example = """
    {
        "a": ["abc", true, false, null, 5, {"testing": "nesting"}, [1,2,3]]
    }
    """
    assert JSON_Parser.parse(json_example)
