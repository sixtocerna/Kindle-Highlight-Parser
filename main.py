from datetime import datetime
from utils import HighlightParser
import logging


def save_parsed_highlights(filename) -> None:

    table = HighlightParser.convert_to_table(filename)

    last_highlight_date = datetime.strftime(table['date'].max(), "%d_%m_%Y_%H_%M_%S")

    table.to_csv(f'highlights_up_to_{last_highlight_date}.csv', index=False)

save_parsed_highlights('My Clippings updated.txt')