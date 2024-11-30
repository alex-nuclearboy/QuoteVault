import os
import json
import logging
from logger import setup_logger

# Set up the logger for the saving module
saving_logger = setup_logger('saving_logger', 'saving_logs.log', logging.DEBUG)

# Define the path to the 'data' folder
DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'data'
)

# Ensure the 'data' folder exists, create it if it doesn't
os.makedirs(DATA_DIR, exist_ok=True)


def write_quotes_to_json(quotes: list, filename: str = 'quotes.json') -> None:
    """
    Write the list of quotes to a JSON file in the 'data' directory.

    :param quotes: The list of quotes to be saved
    :type quotes: list[dict]
    :param filename: The name of the file to save the data to
    :type filename: str

    :return: None

    :raises IOError: If there is an issue opening or writing to the file
    :raises json.JSONDecodeError: If there is an issue with the format
                                  of the data being saved
    """
    try:
        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(quotes, file, ensure_ascii=False, indent=2)
        saving_logger.info(f"Quotes successfully written to {file_path}")
    except IOError as e:
        saving_logger.error(f"Error writing quotes to JSON: {e}")
        raise
    except json.JSONDecodeError as e:
        saving_logger.error(f"Error decoding JSON data: {e}")
        raise


def write_authors_to_json(
    authors: list, filename: str = 'authors.json'
) -> None:
    """
    Write the list of authors to a JSON file in the 'data' directory.

    :param authors: The list of authors to be saved
    :type authors: list[dict]
    :param filename: The name of the file to save the data to
    :type filename: str

    :return: None

    :raises IOError: If there is an issue opening or writing to the file
    :raises json.JSONDecodeError: If there is an issue with the format
                                  of the data being saved
    """
    try:
        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(authors, file, ensure_ascii=False, indent=2)
        saving_logger.info(f"Authors successfully written to {file_path}")
    except IOError as e:
        saving_logger.error(f"Error writing authors to JSON: {e}")
        raise
    except json.JSONDecodeError as e:
        saving_logger.error(f"Error decoding JSON data: {e}")
        raise
