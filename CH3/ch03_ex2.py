#!/usr/bin/env python3
"""Functional Python Programming

Chapter 3, Example Set 2
"""
###########################################
# Strings as immutable objects
###########################################

from decimal import Decimal
from typing import Text, Optional

# Mixing prefix and suffix notation

def clean_decimal_1(text: Text) -> Optional[Decimal]:
    """
    Remove $ and , from a string, return a Decimal.

    >>> clean_decimal_1("$1,234.56")
    Decimal('1234.56')
    """
    if text is None:
        return None
    return Decimal(text.replace("$", "").replace(",", ""))

# Converting string methods to prefix functions

def replace(text: Text, a: Text, b: Text) -> Text:
    """Prefix function for str.replace(a,b)."""
    return text.replace(a, b)


def clean_decimal_2(text: Text) -> Optional[Decimal]:
    """
    Remove $ and , from a string, return a Decimal.

    >>> clean_decimal_2("$1,234.56")
    Decimal('1234.56')
    """
    if text is None: return None
    return Decimal(replace(replace(text, "$", ""), ",", ""))

# Using string methods in recursive functions

def remove(text: Text, characters: Text) -> Text:
    """Remove all of the given characters from a string."""
    if characters:
        return remove(text.replace(characters[0], ""), characters[1:])
    return text


def clean_decimal_3(text: Text) -> Optional[Decimal]:
    """
    Remove $ and , from a string, return a Decimal.

    >>> clean_decimal_3("$1,234.56")
    Decimal('1234.56')
    """
    if text is None: return None
    return Decimal(remove(text, "$,"))
