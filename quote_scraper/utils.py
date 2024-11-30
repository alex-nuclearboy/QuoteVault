from datetime import datetime
from typing import Optional
from bs4 import Tag


def extract_text(tag: Optional[Tag], default: str = '') -> str:
    """
    Safely extract text from a BeautifulSoup tag.

    :param tag: The BeautifulSoup tag to extract text from.
    :type tag: Optional[Tag]
    :param default: The default value to return if no text is found
    :type default: str

    :return: The extracted text or the default value if no text is found
    :rtype: str
    """
    if tag:
        return tag.get_text(strip=True)
    return default


def parse_date(date_string: str) -> Optional[str]:
    """
    Parse the date string into a standard format.

    :param date_str: The date string to parse
    :type date_str: str

    :return: A formatted date string or None if the date is not valid
    :rtype: Optional[str]
    """
    try:
        return (
            datetime.strptime(date_string.strip(), "%B %d, %Y")
            .strftime("%Y-%m-%d")
        )
    except ValueError:
        return None


def safe_get(tag: Optional[Tag], attribute: str) -> Optional[str]:
    """
    Safely retrieve an attribute value from a BeautifulSoup tag.

    :param tag: The BeautifulSoup tag to retrieve the attribute from
    :type tag: Optional[Tag]
    :param attribute: The attribute to retrieve
    :type attribute: str

    :return: The attribute value or None if the attribute is missing
    :rtype: Optional[str]
    """
    return tag.get(attribute) if tag else None
