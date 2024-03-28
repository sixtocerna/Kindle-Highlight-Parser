from utils import HighlightFileProcessor, Highlight
import re 
from datetime import datetime
from dotenv import load_dotenv
from integrations import get_books_in_notion_db, add_book_to_db, append_content_to_page
import os
import logging
import pandas as pd
import warnings

logging.basicConfig(filename='application.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

NOTION_VERSION = os.getenv('NOTION_VERSION')
PAGE_ID = os.getenv('PAGE_ID')
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
DATABASE_ID = os.getenv('HIGHLIGHTS_FROM_KINDLE_DB_ID')

def get_common_value(partial_df, col_name):
    try:
        assert partial_df[col_name].nunique() ==1, f'More than one different value for {col_name}'
    except Exception as e:
        print(partial_df[col_name].unique())
        raise e
    return partial_df[col_name].values[0]

def get_last_highlight_date(log_file_name : str):
    """
    Returns the latest date from a highlight loaded into the database
    """

    with open(log_file_name, 'r') as file:
        file_content = file.read()

    if file_content == '':
        return None

    lines = file_content.splitlines()

    pattern = 'uploaded to Notion'
    date_pattern = r'(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})'

    dates_of_update = []

    for line in lines :

        if pattern in line:
            
            date_from_line = re.search(date_pattern, line).group(0)

            date_from_line = datetime.strptime(date_from_line, "%d-%m-%Y %H:%M:%S")

            dates_of_update.append(date_from_line)

    if dates_of_update:

        return max(dates_of_update)
    
    else: 
        return None

def add_missing_pages(books_in_db, new_highlights):

    titles_from_books_in_db = [book['title'].lower() for book in books_in_db]

    titles_from_books_to_upload = new_highlights.document_name.unique()
    titles_from_books_to_upload = [t.lower() for t in titles_from_books_to_upload]

    missing_books = [title for title in titles_from_books_to_upload if title not in titles_from_books_in_db]

    for title in missing_books:

        rows_matching_book = new_highlights[(new_highlights.document_name == title) & (~new_highlights.is_vocabulary)]

        author = get_common_value(rows_matching_book, 'author')
        date = rows_matching_book.date.min()
        num_highlights = len(rows_matching_book)

        add_book_to_db(
                database_id=DATABASE_ID, 
                title=title, 
                author=author, 
                num_highlights=num_highlights, 
                date=date, 
                api_key=NOTION_API_KEY,
                notion_version=NOTION_VERSION
            )

def upload_highlights_from_book(new_highlights_from_book:pd.DataFrame, page_id:str):

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


if __name__ =='__main__':

    last_highlight_date = get_last_highlight_date('application.log')


    # Update the parsed highlights
    df = HighlightFileProcessor.convert_to_table('My Clippings.txt')

    df = df[df.document_name == 'Take Your Shot']

    if last_highlight_date :

        # Only consider the highlights done after the date 
        # of the last highlight logged into the DB

        new_highlights = df[(df.date>last_highlight_date) & (df.is_vocabulary)].copy()
        new_vocabulary = df[(df.date>last_highlight_date) & ~(df.is_vocabulary)].copy()
    else:
        new_highlights  = df[~df.is_vocabulary].copy()
        new_vocabulary = df[df.is_vocabulary].copy()

    new_vocabulary = new_vocabulary[['content', 'date']]

    books_in_db = get_books_in_notion_db(database_id=DATABASE_ID, api_key=NOTION_API_KEY, notion_version=NOTION_VERSION)

    add_missing_pages(books_in_db=books_in_db, new_highlights=new_highlights)

    # Update the variable to get the ids from the new pages

    books_in_db = get_books_in_notion_db(database_id=DATABASE_ID, api_key=NOTION_API_KEY, notion_version=NOTION_VERSION)

    for book_title, highlights_from_book in new_highlights.groupby('document_name'):

        page_id = [book['id'] for book in books_in_db if book['title']==book_title]

        if page_id:
            page_id = page_id[0]
        else:
            raise ValueError()
  
        upload_highlights_from_book(new_highlights_from_book=highlights_from_book, page_id=page_id)

        logging.info(f'Uploaded {len(highlights_from_book)} highlights to Notion to {book_title}.')

    max_date = new_highlights.date.max()
    new_vocabulary.to_csv('vocabulary.csv', mode='a', index=False)

    logging.info(f'Finished uploading highlights. Date from last highlight {max_date}')
        
    raise ValueError

    print(df)



    