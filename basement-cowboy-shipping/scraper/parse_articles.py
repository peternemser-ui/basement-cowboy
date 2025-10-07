from bs4 import BeautifulSoup

def parse_articles_from_soup(soup):
    """
    Parse articles from the BeautifulSoup object.
    """
    articles = []
    for link in soup.find_all('a', href=True):
        headline = link.get_text(strip=True)
        href = link['href']
        summary = extract_summary(link)

        articles.append({
            "headline": headline,
            "link": href,
            "summary": summary or "No summary available"
        })
    return articles

def extract_summary(link_element):
    """
    Extract a summary for a news article.
    """
    # Find adjacent text elements
    paragraph = link_element.find_next('p')
    if paragraph and len(paragraph.text.strip()) > 10:
        return paragraph.text.strip()

    # Find meta description
    meta_description = link_element.find_previous('meta', attrs={"name": "description"})
    if meta_description and meta_description.get("content"):
        return meta_description["content"]

    return None  # Default fallback
