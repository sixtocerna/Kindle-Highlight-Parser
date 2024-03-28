from validations import check_single_match, check_text_format
from typing import Tuple, List, Literal
import re
import pandas as pd
from datetime import datetime

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
        return f""" Title : {self.document_name} | Author : {self.author} | Date : {self.date} | Pages : {self.pages}
        {self.content}
        """
    
    def to_notion_block(self, structure : Literal['quote_paragraph']) -> dict :

        page_start, page_end = self.pages

        if page_start==page_end:
            page_text = f'p. {page_start}'
        else:
            page_text = f'p. {page_start}-{page_end}'

        quote_content = f'"{self.content}" \n\n{page_text}'

        match structure:

            case 'quote_paragraph':
                content = {
                    "children": [
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
                }

            case _:
                
                raise TypeError(f'structure `{structure}` for Notion content not implemented.')

        return content


class HighlightParser():

    def _parse_title_and_author(text:str) -> str:
        """
        Parses the title and author from the given text.

        Expects the following formats :
            - 'Title by author.extension'

        Args:
            text (str): The text containing the title and author information.
            ignore_missing_author (bool, optional): Whether to ignore missing author information. Defaults to True.
            ignore_missing_extension (bool, optional): Whether to ignore missing file extension. Defaults to True.

        Returns:
            Tuple[str]: The parsed title and author.

        Raises:
            ParsingError: If the are multiple dots, 'by' or '(' inside the text.
        """

        pattern = r'^.* by .*$'

        check_text_format(text_to_check=text, expected_pattern=pattern)

        content, *extension = text.split('.')

        title, author = content.split('by')

        return title, author

    def _parse_date(text:str) -> str:
        """
        Parses the date from the given text.

        Args:
            text (str): The text containing the date information.

        Returns:
            str: The parsed date.

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

    @staticmethod
    def read_file(filename:str = 'My Clippings.txt') -> str:
        """
        Reads the contents of a text file and returns the text.

        Args:
            filename (str, optional): The name of the file to read. Should be in the same directory. Defaults to 'My Clippings.txt'.

        Returns:
            str: The text contained in the file.

        """

        with open(filename, 'r') as file:

            text = file.read()
            
        return text

    @staticmethod
    def parse_highlights_file(filename) -> List[Highlight]:

        file_content = HighlightFileProcessor.read_file(filename)

        raw_highlights =  file_content.split('==========')

        output = []

        for highlight in raw_highlights:

            # Only parse non empty highlights
            if len(highlight.strip())==0:
                continue

            highlight_processed  = HighlightParser.from_text(highlight)

            output.append(highlight_processed)

        return output

    @staticmethod
    def convert_to_table(filename) -> pd.DataFrame:

        all_parsed_highlights = HighlightFileProcessor.parse_highlights_file(filename)

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
 
print(HighlightFileProcessor.convert_to_table('My Clippings updated.txt').iloc[0].to_dict())