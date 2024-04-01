# Kindle Highlights to Notion

This project is designed to parse highlights from Kindle books and upload them to a Notion database. It also keeps track of new vocabulary words from the highlights and saves them to a CSV file.

## Code Structure
- utils.py: Contains utility functions for reading file contents, extracting unique column values, and extracting dates from lines of text.
- highlight_processing.py: Defines classes and functions for processing and parsing highlights from Kindle books.
- integrations.py: Contains functions for interacting with the Notion API.
- main.py: The main entry point for the application, handling highlight processing, updating the Notion database, and managing vocabulary.
- validations.py: Provides functions and classes for validating input data.

## Prerequisites

- Python 3.x
- A Notion account and API key
- A Notion database set up for storing book highlights
