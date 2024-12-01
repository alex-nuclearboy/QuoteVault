import logging
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from utils import extract_text, parse_date, safe_get
from logger import setup_logger

# Set up the logger for this module
scraping_logger = setup_logger(
    'scraping_logger', 'scraping_logs.log', logging.DEBUG
)


BASE_URL = 'https://quotes.toscrape.com'


def fetch_quotes(soup: BeautifulSoup) -> list[dict]:
    """
    Extract quotes and their related data(author, author's URL, and tags)
    from a page.

    :param soup: The BeautifulSoup object representing the HTML page to scrape
    :type soup: BeautifulSoup

    :return: A list of dictionaries, each containing a quote and its associated
             author, author URL, and tags
    :rtype: list[dict]

    :raises Exception: For any unexpected errors during the extraction process
    """
    quotes = []

    for quote in soup.find_all('div', class_='quote'):
        try:
            # Extract the quote text
            text = extract_text(
                quote.find('span', class_='text'), 'No text available'
            )

            # Extract the quote's author
            author = extract_text(
                quote.find('small', class_='author'), 'Unknown Author'
            )

            # Extract the author's URL
            author_url = safe_get(quote.find('a'), 'href')
            if author_url:
                author_url = BASE_URL + author_url

            # Extract the tags (if any)
            tags = [
                extract_text(tag)
                for tag in quote.find_all('a', class_='tag')
                if tag.text.strip()  # Filter out empty tags
            ]

            # Add quote data to the list
            quotes.append({
                'quote': text,
                'author': author,
                'author_url': author_url,
                'tags': tags
            })

        except Exception as e:
            # Log unexpected errors with additional context
            scraping_logger.error(f"Error processing quote: {e}")
            continue  # Skip to the next quote

    return quotes


async def fetch_author_details(
    session: aiohttp.ClientSession, author_url: str
) -> dict:
    """
    Retrieve an author's detailed information from their page.

    :param session: The aiohttp session used for making requests
    :type session: aiohttp.ClientSession
    :param author_url: The URL of the author's page
    :type author_url: str

    :return: A dictionary containing the author's full name,
             date of birth, place of birth, and biography
    :rtype: dict

    :raises aiohttp.ClientError: If there is a network issue while fetching
                                 author details
    :raises Exception: For any other unforeseen errors that might occur
                       during scraping
    """
    try:
        async with session.get(author_url) as response:
            response.raise_for_status()
            soup = BeautifulSoup(await response.text(), 'lxml')

            # Extracting the author's full name
            fullname = extract_text(
                soup.find('h3', class_='author-title'), 'Unknown Author'
            )

            # Extract the author's birth date
            birth_date = parse_date(
                extract_text(soup.find('span', class_='author-born-date'))
            )

            # Extract the author's birth location
            birth_place = extract_text(
                soup.find('span', class_='author-born-location'),
                'Unknown Location'
            )

            # Extracting the author's biography
            bio = extract_text(
                soup.find('div', class_='author-description'),
                'No bio available'
            )

            return {
                "fullname": fullname,
                "birth_date": birth_date,
                "birth_place": birth_place,
                "bio": bio
            }

    except aiohttp.ClientError as e:
        # Log network-related errors
        scraping_logger.error(
            f"Network error while fetching details for {author_url}: {str(e)}"
        )
        return {}

    except Exception as e:
        # Log unexpected errors
        scraping_logger.error(
            f"Error while fetching details for {author_url}: {str(e)}"
        )
        return {}


async def scrape_page_data(
    session: aiohttp.ClientSession, page_url: str, fetched_authors: set
) -> tuple[list[dict], list[dict]]:
    """
    Scrape the quotes and author details from a single page.

    :param session: The aiohttp session used for making requests
    :type session: aiohttp.ClientSession
    :param page_url: The full URL of the page to scrape
    :type page_url: str
    :param fetched_authors: A set containing URLs of authors whose details
                            have already been fetched
    :type fetched_authors: set

    :return: A tuple containing a list of quotes and a list of authors' details
    :rtype: tuple[list[dict], list[dict]]

    :raises aiohttp.ClientError: If there is a network issue
                                 while fetching the page
    :raises Exception: For any unforeseen errors during the scraping process
    """
    try:
        async with session.get(page_url) as response:
            response.raise_for_status()
            soup = BeautifulSoup(await response.text(), 'lxml')

            # Extract quotes from the page
            quotes = fetch_quotes(soup)

            # Collect unique author URLs from quotes
            authors_urls = {
                quote['author_url'] for quote in quotes if quote['author_url']
                and quote['author_url'] not in fetched_authors
            }

            # Fetch author details asynchronously for each unique URL
            authors_details = await asyncio.gather(
                *[fetch_author_details(session, url) for url in authors_urls]
            )

            # Add the new authors to the fetched_authors set
            fetched_authors.update(authors_urls)

            return quotes, authors_details

    except aiohttp.ClientError as e:
        # Log network-related errors
        scraping_logger.error(
            f"Network error while scraping page {page_url}: {str(e)}"
        )
        return [], []

    except Exception as e:
        # Log unexpected errors
        scraping_logger.error(
            f"Error while scraping page {page_url}: {str(e)}"
        )
        return [], []


async def scrape_all_data() -> tuple[list[dict], list[dict]]:
    """
    Scrape all quotes and authors' details from the entire website.

    :return: A tuple containing a list of all quotes and a list
             of all authors' details
    :rtype: tuple[list[dict], list[dict]]

    :raises aiohttp.ClientError: If there is a network issue
                                 while fetching the website
    :raises Exception: For any unforeseen errors during the scraping process
    """
    scraping_logger.info(
        f"Started scraping quotes and author details from {BASE_URL}"
    )

    all_quotes = []
    all_authors_details = []
    fetched_authors = set()
    current_url = BASE_URL

    async with aiohttp.ClientSession() as session:
        try:
            while current_url:
                # Scrape data from the current page
                quotes, authors_details = await scrape_page_data(
                    session, current_url, fetched_authors
                )
                all_quotes.extend(quotes)
                all_authors_details.extend(authors_details)

                # Fetch the HTML content of the current page
                # to locate the next page
                async with session.get(current_url) as response:
                    response.raise_for_status()
                    soup = BeautifulSoup(await response.text(), 'lxml')

                    # Find the next page URL
                    next_page = soup.find('li', class_='next')
                    if next_page and next_page.find('a', href=True):
                        next_url = next_page.find('a', href=True)['href']

                        # If the next page URL is relative, add the base URL
                        current_url = (
                            next_url if next_url.startswith('http')
                            else BASE_URL + next_url
                        )
                    else:
                        current_url = None

        except aiohttp.ClientError as e:
            # Log network-related errors
            scraping_logger.error(
                f"Network error while scraping page {current_url}: {str(e)}"
            )

        except Exception as e:
            # Log unexpected errors
            scraping_logger.error(f"Error while scraping all data: {str(e)}")

    scraping_logger.info(
        f"Completed scraping quotes and author details from {BASE_URL}"
    )

    return all_quotes, all_authors_details
