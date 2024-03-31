"""
This module contains functions and classes for validating input data.
"""

from typing import List, TypeVar
import re

T = TypeVar('T')


class ParsingError(Exception):
    """
    Exception raised when an error occurs during parsing.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class PatternError(Exception):
    """
    Exception raised when the text format does not match the expected pattern.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)

def check_text_format(text_to_check:str, expected_pattern:str) -> None:
    """
    Checks if a text matches the expected pattern using regular expressions.

    Args:
        text_to_check (str): The text to be checked.
        expected_pattern (str): The regular expression pattern representing the expected format.

    Raises:
        PatternError: If the text does not match the expected pattern.
    """

    if not re.match(expected_pattern, text_to_check):
        raise PatternError(f'{text_to_check} does not match format expected : {expected_pattern}')

def check_single_match(
        matches:List[T], 
        exactly_one:bool = True,
        msg_more_than_one_match: str = '', 
        msg_no_matches:str = '') -> T:
    """
    Validates a list of matches, ensuring there is only one match or raising exceptions accordingly.

    Args:
        matches (List[T]): A list of matches to validate.
        exactly_one (bool, optional): If True, exactly one match is expected. Defaults to True.
        msg_more_than_one_match (str, optional): Error message when more than one match is found. Defaults to ''.
        msg_no_matches (str, optional): Error message when no matches are found. Defaults to ''.

    Returns:
        T: The single match if exactly one match is found.

    Raises:
        ValueError: If no matches are found or if more than one match is found.
    """
    if len(matches)==0 :
        raise ValueError(msg_no_matches)
    elif len(matches)==1:
        single_match = matches[0]
        return single_match
    elif exactly_one:
        raise ValueError(msg_more_than_one_match)