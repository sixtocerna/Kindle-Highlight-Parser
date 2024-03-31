"""
This module contains utility functions for reading file contents, extracting unique column values,
and extracting dates from lines of text.
"""

from typing import List, Any
from datetime import datetime
import re
import pandas as pd

def read_file_content(filename:str) -> str:
    """
    Returns the content of a text file

    Args:
        filename (str): The name of the file to read. Should be in the same directory.

    Returns:
        str: The text contained in the file.
    """

    with open(filename, 'r') as file:

        text = file.read()
        
    return text


def get_unique_column_value(partial_df:pd.DataFrame, col_name:str) -> Any:
    """
    Retrieves the unique value from a column in a Pandas DataFrame subset.

    Args:
        partial_df (pandas.DataFrame): A subset of the DataFrame.
        col_name (str): The name of the column to retrieve the unique value from.

    Returns:
        Any: The unique value from the specified column.

    Raises:
        AssertionError: If the column contains more than one unique value.
    """

    try:
        assert partial_df[col_name].nunique()==1, f'More than one different value for {col_name}'
    except AssertionError as e:
        print(partial_df[col_name])
        print(partial_df[col_name].unique())
        raise e
    return partial_df[col_name].values[0]

def extract_dates_from_lines(
        file_content:str, 
        selected_lines_pattern:str, 
        date_pattern:str
        ) -> List[datetime]:
    """
    Extracts dates from lines of text that match a specific pattern.

    Args:
        file_content (str): The content of the file to search.
        selected_lines_pattern (str): The pattern to match lines of interest.
        date_pattern (str): The pattern to match dates within the selected lines.

    Returns:
        List[datetime]: A list of datetime objects representing the extracted dates.
    """
    
    lines_in_text = file_content.splitlines()

    lines_matching_pattern = [line for line in lines_in_text if selected_lines_pattern in line]

    dates_found = []

    for line in lines_matching_pattern:

        date_from_line = re.search(date_pattern, line).group(1)

        date_from_line = datetime.strptime(date_from_line, "%Y-%m-%d %H:%M:%S")

        dates_found.append(date_from_line)

    return dates_found

