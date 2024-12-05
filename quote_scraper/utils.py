import re
import aiohttp
from datetime import datetime
from typing import Optional, List
from bs4 import Tag, BeautifulSoup
from urllib.parse import urlparse, urljoin


def extract_text(tag: Optional[Tag], default: str = '') -> str:
    """
    Safely extract text from a BeautifulSoup tag.

    :param tag: The BeautifulSoup tag to extract text from
    :type tag: Optional[Tag]
    :param default: The default value to return if no text is found
    :type default: str

    :return: The extracted text or the default value if no text is found
    :rtype: str
    """
    if tag:
        # Join stripped strings and clean spaces around punctuation marks
        text = ' '.join(tag.stripped_strings)

        # Clean unnecessary spaces before punctuation marks
        text = re.sub(r'\s([.,;!?])', r'\1', text)

        return text
    return default


def parse_date(
    date_string: str, date_format: str = "%B %d, %Y"
) -> Optional[str]:
    """
    Parse the date string into a standard format.

    :param date_str: The date string to parse
    :type date_str: str
    :param date_format: The format to parse the date string in,
                        default is "%B %d, %Y"
    :type date_format: str

    :return: A formatted date string or None if the date is not valid
    :rtype: Optional[str]
    """
    try:
        return (
            datetime.strptime(date_string.strip(), date_format)
            .strftime("%Y-%m-%d")
        )
    except ValueError:
        return None


def extract_url(
    tag: Optional[Tag], attribute: str = 'href', default: Optional[str] = None,
    base_url: Optional[str] = None
) -> Optional[str]:
    """
    Safely extract and validate a URL from a BeautifulSoup tag.

    :param tag: The BeautifulSoup tag to extract the URL from
    :type tag: Optional[Tag]
    :param attribute: The attribute that contains the URL, default is 'href'
    :type attribute: str
    :param default: The default value to return if the attribute is missing
                    or invalid
    :type default: Optional[str]
    :param base_url: The base URL to prepend if the URL is relative
    :type base_url: Optional[str]

    :return: The extracted and validated URL, or the default value if invalid
             or missing.
    :rtype: Optional[str]
    """
    if not tag or not tag.has_attr(attribute):
        return default

    url = tag.get(attribute)

    if not url:
        return default

    if base_url and not urlparse(url).netloc:
        url = urljoin(base_url, url)  # Add the base URL to the relative one

    return url if is_valid_url(url) else default


def is_valid_url(url: Optional[str]) -> bool:
    """
    Check if a string is a valid URL.

    :param url: The string to validate as a URL
    :type url: Optional[str]

    :return: True if the string is a valid URL, False otherwise
    :rtype: bool
    """
    if not url:
        return False

    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)


async def get_next_page_url(
    session: aiohttp.ClientSession, current_url: str, base_url: str,
    selectors: List[str] = None, attribute: str = 'href'
) -> Optional[str]:
    """
    Fetch the next page URL from the current page.

    :param session: The aiohttp session used for making requests
    :type session: aiohttp.ClientSession
    :param current_url: The URL of the current page to fetch
    :type current_url: str
    :param base_url: The base URL to construct absolute URLs from relative ones
    :type current_url: str
    :param selectors: A list of CSS selectors to search for the next page link
    :type selectors: List[str], optional
    :param attribute: The attribute to extract the URL from the link element
    :type attribute: str, optional

    :return: The next page URL or None if there is no next page
    :rtype: Optional[str]
    """
    if selectors is None:
        selectors = ['li.next a', 'a.next_page']

    async with session.get(current_url) as response:
        response.raise_for_status()
        soup = BeautifulSoup(await response.text(), 'lxml')

    # Try fetching the next URL from the selectors
    next_url = await find_next_url(
        soup, selectors, current_url, base_url, attribute
    )
    if next_url:
        return next_url

    # If not found, try the fallback method
    return await find_next_url_fallback(soup, current_url, base_url, attribute)


async def find_next_url(
    soup: BeautifulSoup, selectors: List[str], current_url: str,
    base_url: str, attribute: str
) -> Optional[str]:
    """
    Find the next page URL using the provided CSS selectors.

    :param soup: The BeautifulSoup object representing the parsed HTML page
    :type soup: BeautifulSoup
    :param selectors: A list of CSS selectors to search for the next page link
    :type selectors: List[str]
    :param current_url: The URL of the current page
    :type current_url: str
    :param base_url: The base URL to construct absolute URLs from relative ones
    :type base_url: str
    :param attribute: The attribute to extract the URL from the link element
    :type attribute: str

    :return: The next page URL or None if no valid link is found
    :rtype: Optional[str]
    """
    for selector in selectors:
        next_element = soup.select_one(selector)
        if next_element:
            next_url = extract_url(
                next_element, attribute, default=None, base_url=base_url
            )
            if next_url and next_url != current_url:
                return next_url
    return None


async def find_next_url_fallback(
    soup: BeautifulSoup, current_url: str, base_url: str, attribute: str
) -> Optional[str]:
    """
    Fallback method to find the next page URL in case no selectors match.

    :param soup: The BeautifulSoup object representing the parsed HTML page
    :type soup: BeautifulSoup
    :param current_url: The URL of the current page
    :type current_url: str
    :param base_url: The base URL to construct absolute URLs from relative ones
    :type base_url: str
    :param attribute: The attribute to extract the URL from the link element
    :type attribute: str

    :return: The next page URL or None if no valid link is found
    :rtype: Optional[str]
    """
    next_li = soup.find('li', class_='next')
    if next_li:
        next_link = next_li.find('a', href=True)
        if next_link:
            next_url = extract_url(
                next_link, attribute, default=None, base_url=base_url
            )
            if next_url and next_url != current_url:
                return next_url
    return None
