#!/usr/bin/env python3

import pytest # type: ignore

from parser import JSONParser

def test_string():
    json_example = """
    "hello this is a string"
    """
    assert JSONParser().parse(json_example) == "hello this is a string"

def test_object():
    json_example = """
    {
        "abc": 123
    }
    """
    assert JSONParser().parse(json_example) == {"abc":123}

def test_weird_spaces_object():
    json_example = """
    {
    \u0020
    \u000A
    \u000D
    \u0009
    }
    """
    assert JSONParser().parse(json_example) == {}

def test_unicode_and_escaped_hex_string():
    json_example = """
    "This is a string containing Unicode characters like °C and accents like é and like \\u8A12"
    """
    assert JSONParser().parse(json_example) == "This is a string containing Unicode characters like °C and accents like é and like 訒"

def test_escaped_string():
    json_example = """
    "he said \\"hello\\""
    """
    assert JSONParser().parse(json_example) == "he said \"hello\""

def test_escaped_bad_hex_string():
    json_example = """
    "he said \\u8Z12"
    """
    with pytest.raises(ValueError):
        JSONParser().parse(json_example)

def test_empty_object():
    json_example = """
    {
    }
    """
    assert JSONParser().parse(json_example) == {}

def test_array():
    json_example = """
    [
        "abc", 123
    ]
    """
    assert JSONParser().parse(json_example) == ["abc", 123]

def test_empty_array():
    json_example = """
    [
    ]
    """
    assert JSONParser().parse(json_example) == []

def test_number():
    json_example = """
        123
    """
    assert JSONParser().parse(json_example) == 123

def test_negative_number():
    json_example = """
        -123
    """
    assert JSONParser().parse(json_example) == -123

def test_fract():
    json_example = """
        123.123
    """
    assert JSONParser().parse(json_example) == 123.123

def test_negative_fract():
    json_example = """
        -123.123
    """
    assert JSONParser().parse(json_example) == -123.123

def test_exponent():
    json_example = """
        123e23
    """
    assert JSONParser().parse(json_example) == float("123e23")

def test_fraction_exponent():
    json_example = """
        123.123e23
    """
    assert JSONParser().parse(json_example) == float("123.123e23")

def test_fraction_sign_exponent():
    json_example = """
        123.123e-23
    """
    assert JSONParser().parse(json_example) == float("123.123e-23")

def test_plus_sign_exponent():
    json_example = """
        123e+23
    """
    assert JSONParser().parse(json_example) == float("123e+23")

def test_minus_sign_exponent():
    json_example = """
        123e-23
    """
    assert JSONParser().parse(json_example) == float("123e-23")

def test_null():
    json_example = """
    null
    """
    assert JSONParser().parse(json_example) is None

def test_bool():
    json_example = """
    true
    """
    assert JSONParser().parse(json_example)

def test_nesting():
    json_example = """
    {
        "a": ["abc", true, false, null, 5, {"testing": "nesting"}, [1,2,3]]
    }
    """
    assert JSONParser().parse(json_example) == {"a": ["abc", True, False, None, 5, {"testing": "nesting"}, [1,2,3]]}
