from highlight_processing import HighlightFileProcessor, Highlight
import re 
from datetime import datetime
from dotenv import load_dotenv
from integrations import get_books_in_notion_db, add_book_to_db, append_content_to_page, update_number_of_highlights
import os
import logging
import pandas as pd

logging.basicConfig(filename='application.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

NOTION_VERSION = os.getenv('NOTION_VERSION')
PAGE_ID = os.getenv('PAGE_ID')
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
DATABASE_ID = os.getenv('HIGHLIGHTS_FROM_KINDLE_DB_ID')

def get_unique_column_value(partial_df, col_name):
    try:
        assert partial_df[col_name].nunique()==1, f'More than one different value for {col_name}'
    except Exception as e:
        print(partial_df[col_name])
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

    pattern = 'Finished uploading highlights.'
    date_pattern = r'Date from last highlight is (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'

    dates_of_update = []

    for line in lines :

        if pattern in line:
            
            date_from_line = re.search(date_pattern, line).group(1)

            date_from_line = datetime.strptime(date_from_line, "%Y-%m-%d %H:%M:%S")

            dates_of_update.append(date_from_line)

    if dates_of_update:

        return max(dates_of_update)
    
    else: 
        return None

def add_missing_pages(books_in_db, new_highlights):

    titles_from_books_in_db = [book['title'].lower() for book in books_in_db]

    titles_from_books_to_upload = new_highlights.document_name.unique()

    missing_books = [title for title in titles_from_books_to_upload if title.lower() not in titles_from_books_in_db]

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

    update_number_of_highlights(
        page_id=page_id, 
        highlights_added=len(new_highlights_from_book), 
        api_key=NOTION_API_KEY, 
        notion_version=NOTION_VERSION
    )

if __name__ =='__main__':

    last_highlight_date = get_last_highlight_date('application.log')

    # Update the parsed highlights
    df = HighlightFileProcessor.convert_to_table('My Clippings.txt')

    df.date = pd.to_datetime(df.date)

    if last_highlight_date :

        # Only consider the highlights done after the date 
        # of the last highlight logged into the DB

        new_highlights = df.loc[(df.date>last_highlight_date) & ~(df.is_vocabulary)].copy()
        new_vocabulary = df.loc[(df.date>last_highlight_date) & (df.is_vocabulary)].copy()
    else:
        new_highlights  = df[~df.is_vocabulary].copy()
        new_vocabulary = df[df.is_vocabulary].copy()
    
    if not new_highlights.empty:

        books_in_db = get_books_in_notion_db(database_id=DATABASE_ID, api_key=NOTION_API_KEY, notion_version=NOTION_VERSION)

        print()
        print('Adding missing books to database'.center(60, '-'))
        print()

        add_missing_pages(books_in_db=books_in_db, new_highlights=new_highlights)

        # Update the variable to get the ids from the new pages
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
            
        max_date = new_highlights.date.max()
        print()
        print('New max date is ', max_date)

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

        logging.info(f'Finished uploading highlights. Date from last highlight is {max_date}')
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
