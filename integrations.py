import requests
from datetime import datetime
from typing import Dict
import warnings


def get_notion_page_info(page_id, api_key:str, notion_version) -> Dict:

    url = f'https://api.notion.com/v1/pages/{page_id}'

    headers = {
            'Authorization': f'Bearer {api_key}',
            'Notion-Version': notion_version,
        }

    response = requests.get(url, headers=headers)

    response.raise_for_status()

    return response.json()

def get_notion_page_contents(page_id, api_key:str, notion_version) -> Dict:

    url = f'https://api.notion.com/v1/blocks/{page_id}/children'

    headers = {
            'Authorization': f'Bearer {api_key}',
            'Notion-Version': notion_version,
        }

    response = requests.get(url, headers=headers)

    response.raise_for_status()

    return response.json()

def append_content_to_page(page_id, content, api_key:str, notion_version) -> Dict:

    url = f'https://api.notion.com/v1/blocks/{page_id}/children'

    headers = {
            'Authorization': f'Bearer {api_key}',
            "Content-Type":"application/json",
            'Notion-Version': notion_version,
        }
    
    if len(content['children'])<100:

        response = requests.patch(url, headers=headers, json=content)

        response.raise_for_status()

    else:

        all_children = content['children']

        warnings.warn(f'Batching content for uploading {len(all_children)} elements...')

        batch_size = 100

        for i in range(0, len(all_children)+1, batch_size):

            start_idx = i
            end_idx = min(i + batch_size, len(all_children))

            batch_children = all_children[start_idx:end_idx]

            batch_content = {'children':batch_children}

            response = requests.patch(url, headers=headers, json=batch_content)

            response.raise_for_status()


def retrieve_database_rows(database_id, api_key:str, notion_version) -> Dict:
    url = f'https://api.notion.com/v1/databases/{database_id}/query'

    headers = {
            'Authorization': f'Bearer {api_key}',
            "Content-Type":"application/json",
            'Notion-Version': notion_version,
        }
    
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()

def create_new_row_properties(title, author, date, num_highlights):

    string_date = datetime.strftime(date, '%Y-%m-%d')

    prop_title = {
                'title': [
                    {
                        'text': {
                            'content': title
                        }
                    }
                ]
            }
    
    prop_author = {
                'rich_text': [
                    {
                        'text': {
                            'content': author
                        }
                    }
                ]
            }
    
    prop_date = {
                'date': {
                    'start': string_date
                }
            }
    
    prop_num_highlights = {
                'number': num_highlights
    }

    new_properties = {
        'Title':prop_title,
        'Author':prop_author,
        'Date':prop_date,
        'Number of Highlights':prop_num_highlights
    }

    return new_properties

def add_book_to_db(database_id, title, author, num_highlights, date:datetime, api_key, notion_version) -> None:
    url = 'https://api.notion.com/v1/pages'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Notion-Version': notion_version,
    }
   
    data = {
        'parent': {'database_id': database_id},
        'properties': create_new_row_properties(title, author, date, num_highlights)
    }
    response = requests.post(url, headers=headers, json=data)

    response.raise_for_status()
    

def get_books_in_notion_db(database_id, api_key, notion_version) -> Dict:

    response = retrieve_database_rows(database_id, api_key=api_key, notion_version=notion_version)

    output = []

    if response['next_cursor'] is None :
        for result in response['results']:
            id = result['id']
            title = result['properties']['Title']['title'][0]['text']['content']
            author = result['properties']['Author']['rich_text']
            if author == []:
                author = None
            else:
                author = author[0]['text']['content']

            output.append({'title':title, 'id':id, 'author':author})

    else:
        raise NotImplementedError(msg = 'Pagination handling not implemented')
    
    return output

def update_number_of_highlights(page_id: str, highlights_added:int, api_key, notion_version):
    
    url = f'https://api.notion.com/v1/pages/{page_id}'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Notion-Version': notion_version,
    }

    page_details = get_notion_page_info(page_id=page_id, api_key=api_key, notion_version=notion_version)

    prev_properties = page_details['properties']

    prev_num_highlights = prev_properties['Number of Highlights']['number']
    new_num_highlights = highlights_added + prev_num_highlights

    updated_properties = prev_properties
    updated_properties['Number of Highlights']['number'] = new_num_highlights

    data = {
        'properties': updated_properties
    }

    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()
