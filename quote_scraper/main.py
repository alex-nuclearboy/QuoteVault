import logging
import asyncio
from save import write_quotes_to_json, write_authors_to_json
from scraper import scrape_all_data
from logger import setup_logger

# Set up the logger for the main module
main_logger = setup_logger('main_logger', 'main_logs.log', logging.DEBUG)


async def main() -> None:
    """
    Main function to scrape data and write it to JSON files.

    This function:
    - Calls `scrape_all_data` to retrieve both quotes and authors.
    - Calls `write_quotes_to_json` to save the scraped quotes to a JSON file.
    - Calls `write_authors_to_json` to save the scraped authors to a JSON file.

    :raises Exception: If any error occurs during the scraping
                       or writing process.

    """
    main_logger.info('Main process started...')
    try:
        quotes, authors = await scrape_all_data()

        write_quotes_to_json(quotes)
        write_authors_to_json(authors)

        main_logger.info('Process completed successfully.')

    except Exception as e:
        main_logger.error(f"An error occurred: {e}")


if __name__ == '__main__':
    asyncio.run(main())
