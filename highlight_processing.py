"""
This module contains classes and functions for processing and parsing highlights from Kindle books.
"""

from validations import check_single_match, check_text_format
from typing import Tuple, List, Literal, Dict, Any
import re
import pandas as pd
from datetime import datetime
import logging
import json
from utils import read_file_content

class Highlight():
    """
    Represents a highlighted section from a document.

    Attributes:
        document_name (str): The name of the document.
        date (datetime): The date the highlight was made.
        pages (Tuple[int]): A tuple representing the start and end pages of the highlight.
        content (str): The content of the highlight.
        author (str, optional): The author of the document. Defaults to None.
    """


    def __init__(self, document_name:str, date:datetime, pages:Tuple[int], content:str, author=None) -> None:
        """
        Initializes a Highlight object.

        Args:
            document_name (str): The name of the document.
            date (datetime): The date the highlight was made.
            pages (Tuple[int]): A tuple representing the start and end pages of the highlight.
            content (str): The content of the highlight.
            author (str, optional): The author of the document. Defaults to None.
        """
        
        self.document_name = document_name
        self.date = date
        self.pages = pages
        self.content = content
        self.author = author

    def __str__(self) -> str:
        """
        Returns a string representation of the Highlight object.
        """
        return f""" Title : {self.document_name} | Author : {self.author} | Date : {self.date} | Pages : {self.pages}
        {self.content}
        """
    
    def to_notion_block(self, structure : Literal['quote_paragraph']) -> List[Dict[str, Any]]:
        """
        Converts the Highlight object to a Notion block structure.

        Args:
            structure (Literal['quote_paragraph']): The structure of the Notion block.

        Returns:
            dict: The Notion block structure representing the highlight.

        Raises:
            TypeError: If the specified structure is not implemented.
        """

        page_start, page_end = self.pages

        if page_start==page_end:
            page_text = f'p. {page_start}'
        else:
            page_text = f'p. {page_start}-{page_end}'

        quote_content = f'"{self.content}" \n\n{page_text}'

        match structure:

            case 'quote_paragraph':
                content = [
                        {
                            "object": "block",
                            "type": "quote",
                            "quote": {
                                "rich_text": [{
                                "type": "text",
                                "text": {
                                    "content": quote_content,
                                    "link": None
                                },
                                }],
                                "color": "default"
                            }
                        },
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": "",
                                            "link": None
                                        }
                                    }
                                ]
                            }
                        }
                    ]

            case _:
                
                raise TypeError(f'structure `{structure}` for Notion content not implemented.')

        return content


class HighlightParser():
    """
    A class for parsing highlight details from raw text.
    """

    def _parse_title_and_author(text:str) -> Tuple[str]:
        """
        Parses the title and author from the given text.

        Expects the following format :
            - 'Title by author.extension'

        Args:
            text (str): The text containing the title and author information.

        Returns:
            Tuple[str]: The parsed title and author.

        Raises:
            ParsingError: If the text does not match the expected format.
        """

        pattern = r'^.* by .*$'

        check_text_format(text_to_check=text, expected_pattern=pattern)

        content, *extension = text.split('.')

        title, author = content.split('by')

        return title.strip(), author.strip()

    def _parse_date(text:str) -> datetime:
        """
        Parses the date from the given text.

        Expects the following format :
            - 'Month day year hour:minutes:seconds PM'
            - 'Month day year hour:minutes:seconds AM'

        Args:
            text (str): The text containing the date information.

        Returns:
            datetime: The parsed date.

        Raises:
            ParsingError: If no date in the format 'Month date year' is found within the text
        """

        date_pattern = r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+(?:AM|PM)\b"
        matches = re.findall(date_pattern, text)

        date_string = check_single_match(matches=matches, 
                                       msg_no_matches='Text must contain a date',
                                       msg_more_than_one_match='Text can only contain a single date')

        return datetime.strptime(date_string, "%B %d, %Y %I:%M:%S %p")


    def _parse_pages(text:str) -> Tuple[int]:
        """
        Parses the pages from the given text.

        Expects one of following format:
            * Page Num - Page Num
            * Page Num

        Args:
            text (str): The text containing the page information.

        Returns:
            Tuple[int]: A tuple representing the start and end pages.

        Raises:
            ParsingError: If no pages in the format 'digit' or 'digits-digits' is found
        """
        pattern = r'(\d+-\d+)'
        matches = re.findall(pattern, text)

        try: 

            pages = check_single_match(matches=matches, msg_more_than_one_match='Too many pages to parse', msg_no_matches='No pages found')
            start_page, end_page = pages.split('-')

        except ValueError:

            pattern = r'page (\d+)'
            matches = re.findall(pattern, text)
            page = check_single_match(matches=matches, msg_more_than_one_match='Too many pages to parse', msg_no_matches='No pages found')
            start_page, end_page = page, page

        return int(start_page), int(end_page)

    @staticmethod
    def from_text(raw_text:str) -> Highlight:
        """
        Creates a Highlight object from raw text.

        Args:
            raw_text (str): The raw text containing highlight details.

        Returns:
            Highlight: A Highlight object created from the raw text.
        """

        raw_text = raw_text.strip()
        raw_document_name, details, *content = raw_text.splitlines()


        date = HighlightParser._parse_date(details)
        title, author = HighlightParser._parse_title_and_author(raw_document_name)
        pages = HighlightParser._parse_pages(details)

        return Highlight(document_name =title, date=date, pages=pages, content = ''.join(content), author=author)
    

class HighlightFileProcessor:
    """
    A class for processing highlight files and converting them to a table.
    """

    @staticmethod
    def _update_book_titles(prev_file_contents:str, updated_titles:Dict[str, str]) -> str:
        """
        Updates the book titles in the file contents based on a dictionary of updated titles.

        Args:
            prev_file_contents (str): The previous file contents.
            updated_titles (Dict[str, str]): A dictionary mapping old titles to new titles.

        Returns:
            str: The updated file contents with the titles replaced.
        """
        new_file_content = prev_file_contents

        for old_title, updated_title in updated_titles.items():

            new_file_content = new_file_content.replace(old_title, updated_title)

        return new_file_content

    @staticmethod
    def process_highlights_file(filename:str) -> List[Highlight]:
        """
        Processes a highlight file and returns a list of Highlight objects.

        Args:
            filename (str): The name of the highlight file.

        Returns:
            List[Highlight]: A list of Highlight objects parsed from the file.
        """

        file_content = read_file_content(filename)

        # Replace the titles specified in the updated_titles.json file

        with open('updated_titles.json', 'r') as json_file:
            updated_titles = json.load(json_file)

        file_content = HighlightFileProcessor._update_book_titles(prev_file_contents=file_content, updated_titles=updated_titles)

        raw_highlights =  file_content.split('==========')

        output = []

        for highlight in raw_highlights:

            # Only parse non empty highlights
            if len(highlight.strip())==0:
                continue

            highlight_processed  = HighlightParser.from_text(highlight)

            output.append(highlight_processed)

        logging.info(f'{filename} processed')

        return output

    @staticmethod
    def convert_to_table(filename:str) -> pd.DataFrame:
        """
        Converts the highlights from a file into a Pandas DataFrame.

        Args:
            filename (str): The name of the highlight file.

        Returns:
            pd.DataFrame: A DataFrame containing the parsed highlight information.
        """

        try:
            all_parsed_highlights = HighlightFileProcessor.process_highlights_file(filename)
        except Exception as e:
            logging.error(f'Error {e} raise while processing {filename}.')
            raise e

        rows = []

        for h in all_parsed_highlights:

            start_page, end_page = h.pages

            new_row = dict(document_name=h.document_name, date=h.date, start_page=start_page, end_page=end_page, content=h.content, author=h.author)

            rows.append(new_row)

        output = pd.DataFrame(rows)

        get_num_words = lambda text : len(text.strip().split(' '))

        is_vocabulary = [get_num_words(content)==1 for content in output['content']]

        output['is_vocabulary'] = is_vocabulary

        return output
    
    @staticmethod
    def save_table_to_csv(filename) -> None:
        """
        Saves the highlight table to a CSV file.

        Args:
            filename (str): The name of the highlight file.
        """

        table = HighlightFileProcessor.convert_to_table(filename)

        last_highlight_date = datetime.strftime(table['date'].max(), "%d-%m-%Y %H:%M:%S")

        logging.info(f'Parsed highlights table updated. Last highlight is from {last_highlight_date}')

        table.to_csv(f'parsed_highlights.csv', index=False)
