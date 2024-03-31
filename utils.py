from typing import List
from datetime import datetime
import re

def read_file_content(filename) -> str:
    """
    Reads the contents of a text file and returns the text.

    Args:
        filename (str): The name of the file to read. Should be in the same directory. Defaults to 'My Clippings.txt'.

    Returns:
        str: The text contained in the file.
    """

    with open(filename, 'r') as file:

        text = file.read()
        
    return text


def get_unique_column_value(partial_df, col_name):
    try:
        assert partial_df[col_name].nunique()==1, f'More than one different value for {col_name}'
    except AssertionError as e:
        print(partial_df[col_name])
        print(partial_df[col_name].unique())
        raise e
    return partial_df[col_name].values[0]

def extract_dates_from_lines(file_content:str, selected_lines_pattern:str, date_pattern:str) -> List[datetime]:
    
    lines_in_text = file_content.splitlines()

    lines_matching_pattern = [line for line in lines_in_text if selected_lines_pattern in line]

    dates_found = []

    for line in lines_matching_pattern:

        date_from_line = re.search(date_pattern, line).group(1)

        date_from_line = datetime.strptime(date_from_line, "%Y-%m-%d %H:%M:%S")

        dates_found.append(date_from_line)

    return dates_found

