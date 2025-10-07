import requests
from bs4 import BeautifulSoup

def fetch_page_content(url):
    """
    Fetch the HTML content of a URL and return a BeautifulSoup object.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {url}: {e}")
        return None
