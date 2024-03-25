from typing import List, Tuple, Any, TypeVar
import re
from datetime import datetime

T = TypeVar('T')


class ParsingError(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def validate_single_match(
        matches:List[T], 
        exactly_one:bool = True,
        msg_more_than_one_match: str = '', 
        msg_no_matches:str = '') -> T:

    if len(matches)==0 :
        raise ValueError(msg_no_matches)
    elif len(matches)==1:
        single_match = matches[0]
        return single_match
    elif exactly_one:
        raise ValueError(msg_more_than_one_match)


class Highlight():

    def __init__(self, document_name:str, date:datetime, pages:Tuple[int], content:str, author=None) -> None:
        
        self.document_name = document_name
        self.date = date
        self.pages = pages
        self.content = content
        self.author = author

    def __str__(self) -> str:
        return f""" Title : {self.document_name} | Author : {self.author} | Date : {self.date} | Pages : {self.pages}
        {self.content}
        """

    def _parse_title_and_author(text:str, ignore_missing_author = True, ignore_missing_extension = True) -> str:

        pattern = r'\([^)]*\)'
        # Remove text within parentheses using regex
        clean_text = re.sub(pattern, '', text)

        document_name, *extension = clean_text.split('.')

        if len(extension)>1:
            raise ParsingError(("Can't parse title and author : text contains " 
                              "multiple times the sign '.' "))
        elif len(extension)==0:
            if ignore_missing_extension:

                title = document_name
                author = None

                return title, author
            else:
                raise ParsingError

        title, *rest = document_name.split('by')

        if len(rest)>1:
            raise ParsingError(("Can't parse title and author : text contains " 
                              "multiple times the word 'by'."))
        elif len(rest)==0:
            if ignore_missing_author:
                title = document_name
                author = None

                return title, author
            else:
                raise ParsingError()
        
        title = title.strip()
        
        author, *remaing_text = rest[0].split('(')

        if len(remaing_text)>1:
            raise ParsingError(("Can't parse title and author : text contains" 
                              "multiple times the sign '('."))
        
        return title, author

    def _parse_date(text:str) -> str:

        date_pattern = r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b"
        matches = re.findall(date_pattern, text)

        date_string = validate_single_match(matches=matches, 
                                       msg_no_matches='Text must contain a date',
                                       msg_more_than_one_match='Text can only contain a single date')

        return datetime.strptime(date_string, "%B %d, %Y").date()


    def _parse_pages(text:str) -> Tuple[int]:
        pattern = r'(\d+-\d+)'
        matches = re.findall(pattern, text)

        try: 

            pages = validate_single_match(matches=matches, msg_more_than_one_match='Too many pages to parse', msg_no_matches='No pages found')
            start_page, end_page = pages.split('-')

        except ValueError:

            pattern = r'page (\d+)'
            matches = re.findall(pattern, text)
            page = validate_single_match(matches=matches, msg_more_than_one_match='Too many pages to parse', msg_no_matches='No pages found')
            start_page, end_page = page, page

        return int(start_page), int(end_page)

    @classmethod
    def from_text(cls, raw_text:str):
        """
        Magic Words (Jonah Berger) (Z-Library)  
        - Your Highlight on page 141-141 | Added on Thursday, March 21, 2024 4:20:33 AM

        again—and mixing up moments—leveraging emotional volatility —can help turn any story into a great one
        """
        raw_text = raw_text.strip()
        raw_document_name, details, *content = raw_text.splitlines()
        #print('DETAILS : ', details)

        try : 
            date = cls._parse_date(details)
        except:
            print('Error in date parsing', details)
            raise Exception
        title, author = cls._parse_title_and_author(raw_document_name)
        pages = cls._parse_pages(details)

        return cls(document_name =title, date=date, pages=pages, content = ''.join(content), author=author)


def read_file(filename:str = 'My Clippings.txt') -> str:
    """
    Returns the text contains in file

    Parameters : 
    - filename (str): Name of the file. Should be in the same directory
    Returns
    - str
    """

    with open(filename, 'r') as file:

        text = file.read()
        
    return text


def split_into_highlights(file_content:str) -> List[str]:
    """
    Returns the list of highlights

    """

    highlights_data =  file_content.split('==========')

    for data in highlights_data:

        print(data)

        h  = Highlight.from_text(data)

        print(str(h))
        print('='*50)
        print()
        print()


print(split_into_highlights(read_file()))