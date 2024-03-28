import requests
from dotenv import load_dotenv
import os

load_dotenv()

NOTION_VERSION = os.getenv('NOTION_VERSION')
PAGE_ID = os.getenv('PAGE_ID')
NOTION_API_KEY = os.getenv('NOTION_API_KEY')


def read_notion_page(page_id, api_key, notion_version = NOTION_VERSION):

    url = f'https://api.notion.com/v1/pages/{page_id}'

    headers = {
            'Authorization': f'Bearer {api_key}',
            'Notion-Version': notion_version,
        }

    response = requests.get(url, headers=headers)

    response.raise_for_status()

    return response.json()

def get_notion_page_contents(page_id, api_key, notion_version = NOTION_VERSION):

    url = f'https://api.notion.com/v1/blocks/{page_id}/children'

    headers = {
            'Authorization': f'Bearer {api_key}',
            'Notion-Version': notion_version,
        }

    response = requests.get(url, headers=headers)

    response.raise_for_status()

    return response.json()

def append_content_to_page(page_id, api_key, content, notion_version = NOTION_VERSION):

    url = f'https://api.notion.com/v1/blocks/{page_id}/children'

    print(url)
    print(api_key)

    headers = {
            'Authorization': f'Bearer {api_key}',
            "Content-Type":"application/json",
            'Notion-Version': notion_version,
        }

    response = requests.patch(url, headers=headers, json=content)

    response.raise_for_status()

    return response.status_code

content = {
	"children": [
		{
			"object": "block",
			"type": "heading_2",
			"heading_2": {
				"rich_text": [{ "type": "text", "text": { "content": "Lacinato kale" } }]
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
							"content": "Lacinato kale is a variety of kale with a long tradition in Italian cuisine, especially that of Tuscany. It is also known as Tuscan kale, Italian kale, dinosaur kale, kale, flat back kale, palm tree kale, or black Tuscan palm.",
							"link": { "url": "https://en.wikipedia.org/wiki/Lacinato_kale" }
						}
					}
				]
			}
		}
	]
}

print(append_content_to_page(PAGE_ID, NOTION_API_KEY, content))