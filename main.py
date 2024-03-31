"""
This module is the main entry point for the application. It handles the processing of highlights,
updating the Notion database, and managing vocabulary.
"""

from highlight_processing import HighlightFileProcessor, Highlight
from dotenv import load_dotenv
from integrations import get_books_in_notion_db, add_book_to_db, append_content_to_page, update_number_of_highlights
import os
import logging
import pandas as pd
from utils import get_unique_column_value, read_file_content, extract_dates_from_lines
from typing import Dict, List, Union
from datetime import datetime

logging.basicConfig(filename='application.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

NOTION_VERSION = os.getenv('NOTION_VERSION')
PAGE_ID = os.getenv('PAGE_ID')
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
DATABASE_ID = os.getenv('HIGHLIGHTS_FROM_KINDLE_DB_ID')

def log_errors(
        func, 
        log_file,
        log_error_message, 
        log_sucessful_message
        ):

    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logging.basicConfig(filename=log_file, level=logging.ERROR)
            logging.error(f"{log_error_message} {str(e)}")
            return
        else:
            logging.basicConfig(filename=log_file, level=logging.INFO)
            logging.info(log_sucessful_message)
            return result

    return wrapper

def parse_last_highlight_date_from_log(log_file_name : str) -> Union[None, datetime]:
    """
    Returns the latest date from a highlight loaded into the database.

    Args:
        log_file_name (str): The name of the log file.

    Returns:
        datetime or None: The latest date from a highlight loaded into the database, or None if no highlights were uploaded.
    """

    file_content = read_file_content(filename=log_file_name)

    if file_content == '':
        return None

    line_pattern = 'Finished uploading highlights.'
    date_pattern = r'Date from last highlight is (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'

    dates_of_update = extract_dates_from_lines(
        file_content=file_content, 
        selected_lines_pattern=line_pattern, 
        date_pattern=date_pattern
    )

    if dates_of_update:
        return max(dates_of_update)
    else: 
        return None

def get_missing_books(books_in_db:List[Dict[str,str]], new_highlights:pd.DataFrame)->List[str]:
    """
    Returns a list of book titles that are not present in the Notion database.

    Args:
        books_in_db (List[Dict[str, str]]): A list of dictionaries representing books in the Notion database.
        new_highlights (pd.DataFrame): A DataFrame containing new highlights.

    Returns:
        List[str]: A list of book titles that are not present in the Notion database.
    """

    titles_from_books_in_db = [book['title'].lower() for book in books_in_db]

    titles_from_books_to_upload = new_highlights.document_name.unique()

    missing_books = [title for title in titles_from_books_to_upload if title.lower() not in titles_from_books_in_db]

    return missing_books


def add_missing_books_to_db(books_in_db:List[Dict[str,str]], new_highlights:pd.DataFrame) -> None:
    """
    Adds missing books to the Notion database.

    Args:
        books_in_db (List[Dict[str, str]]): A list of dictionaries representing books in the Notion database.
        new_highlights (pd.DataFrame): A DataFrame containing new highlights.
    """

    missing_books = get_missing_books(books_in_db, new_highlights)

    for title in missing_books:

        print(f'Adding {title} to database in Notion...')

        rows_matching_book = new_highlights[(new_highlights.document_name == title) & (~new_highlights.is_vocabulary)]

        author = get_unique_column_value(rows_matching_book, 'author')
        date = rows_matching_book.date.min()
        num_highlights = 0

        add_book_to_db(
                database_id=DATABASE_ID, 
                title=title, 
                author=author, 
                num_highlights=num_highlights, 
                date=date, 
                api_key=NOTION_API_KEY,
                notion_version=NOTION_VERSION
            )

def upload_highlights_from_book(new_highlights_from_book:pd.DataFrame, page_id:str) -> None:
    """
    Uploads highlights from a book to the Notion page.

    Args:
        new_highlights_from_book (pd.DataFrame): A DataFrame containing highlights from a book.
        page_id (str): The ID of the Notion page representing the book.
    """
    highlights_to_upload = []

    for highlight_data in new_highlights_from_book.to_dict('records'):
        pages = (highlight_data.pop('start_page'), highlight_data.pop('end_page'))
        highlight_data.pop('is_vocabulary')
        highlight = Highlight(pages=pages, **highlight_data)
        highlights_to_upload.append(highlight)

    children = []

    for h in highlights_to_upload:

        children.extend(h.to_notion_block(structure='quote_paragraph'))

    content_to_upload = {"children":children}

    append_content_to_page(
        page_id=page_id, 
        content=content_to_upload, 
        api_key=NOTION_API_KEY, 
        notion_version=NOTION_VERSION
    )

    update_number_of_highlights(
        page_id=page_id, 
        highlights_added=len(new_highlights_from_book), 
        api_key=NOTION_API_KEY, 
        notion_version=NOTION_VERSION
    )

def upload_new_highlights_to_notion(new_highlights:pd.DataFrame) -> None:
    """
    Uploads new highlights to the Notion database.

    Args:
        new_highlights (pd.DataFrame): A DataFrame containing new highlights.
    """

    books_in_db = get_books_in_notion_db(database_id=DATABASE_ID, api_key=NOTION_API_KEY, notion_version=NOTION_VERSION)

    print()
    print('Adding missing books to database'.center(60, '-'))
    print()

    add_missing_books_to_db(books_in_db=books_in_db, new_highlights=new_highlights)

    print()
    print('Updating database'.center(60, '-'))
    print()

    books_in_db = get_books_in_notion_db(database_id=DATABASE_ID, api_key=NOTION_API_KEY, notion_version=NOTION_VERSION)

    print('Uploading highlights to Notion'.center(60, '-'))
    print()
    print(f'Highlights from {new_highlights.date.min()} to {new_highlights.date.max()}')
    print()

    for book_title, highlights_from_book in new_highlights.groupby('document_name'):

        page_id = [book['id'] for book in books_in_db if book['title']==book_title]

        if page_id:
            page_id = page_id[0]
        else:
            raise ValueError()
        
        print(f'\t- Uploading {len(highlights_from_book)} highlights to {book_title}...')

        upload_highlights_from_book(new_highlights_from_book=highlights_from_book, page_id=page_id)

        logging.info((f'Uploaded {len(highlights_from_book)} highlights to {book_title}' 
                        f'ranging from {highlights_from_book.date.min()} to {highlights_from_book.date.max()}'))
        
    logging.info(f'Finished uploading highlights. Date from last highlight is {new_highlights.date.max()}')
            

def update_vocabulary_db(new_vocabulary:pd.DataFrame) -> None:
    """
    Updates the vocabulary database with new words.

    Args:
        new_vocabulary (pd.DataFrame): A DataFrame containing new vocabulary words.
    """

    print()
    print('Adding new vocabulary to CSV'.center(60, '-'))
    print()

    starting_num_words = len(new_vocabulary)
    new_vocabulary = new_vocabulary[['content', 'date']]
    empty = new_vocabulary.content.str.strip()
    empty = (empty.isna())|(empty=='')
    
    new_vocabulary = new_vocabulary.loc[~empty]
    end_num_words = len(new_vocabulary)
    print(f'\t- Dropped {starting_num_words - end_num_words} words.')

    new_vocabulary.to_csv('vocabulary.csv', mode='a', index=False, header=False)
    print(f'\t- Added {len(new_vocabulary)} words of vocabulary to CSV')

    logging.info(f'Finished updating vocabulary. Date from last vocabulary word is {new_vocabulary.date.max()}')


def select_new_highlights_and_vocabulary(df:pd.DataFrame, last_highlight_date:datetime):
    """
    Selects new highlights and vocabulary from a DataFrame based on the last highlight date.

    Selects only the highlights done after the most recent highlight uploaded to the Notion database.

    Args:
        df (pd.DataFrame): The DataFrame containing highlights.
        last_highlight_date (datetime): The date of the last highlight loaded into the database.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing two DataFrames, one for new highlights and one for new vocabulary.
    """

    if last_highlight_date :

        # Only consider the highlights done after the date 
        # of the last highlight logged into the DB

        new_highlights = df.loc[(df.date>last_highlight_date) & ~(df.is_vocabulary)].copy()
        new_vocabulary = df.loc[(df.date>last_highlight_date) & (df.is_vocabulary)].copy()
    else:
        new_highlights  = df[~df.is_vocabulary].copy()
        new_vocabulary = df[df.is_vocabulary].copy()

    return new_highlights, new_vocabulary

if __name__ =='__main__':

    df = HighlightFileProcessor.convert_to_table('My Clippings.txt')
    
    last_highlight_date = parse_last_highlight_date_from_log('application.log')
    new_highlights, new_vocabulary = select_new_highlights_and_vocabulary(df, last_highlight_date=last_highlight_date)
    
    if not new_highlights.empty:

        upload_new_highlights_to_notion(new_highlights=new_highlights)
            
        updated_last_highlight_date = new_highlights.date.max()

        print()
        print(f'Last highlight date udpated is {updated_last_highlight_date}')

        update_vocabulary_db(new_vocabulary=new_vocabulary)
        
        print()
        print('Process completed succesfully.')
        print()

    else:
        print()
        print('-'*60)
        print(f'No highlights uploaded : no remaining highlights after {last_highlight_date}')
        print('-'*60)
        print()
        logging.warning(f'No highlights uploaded : no remaining highlights after {last_highlight_date}')
