import re

# Unwanted summary phrases
UNWANTED_SUMMARIES = [
    "Make sense of the day’s news and ideas.",
    "Get what you need to know to start your day.",
    "Analysis that explains politics, policy and everyday life.",
    "Backstories and analysis from our Canadian correspondents.",
    "The most crucial business and policy news you need to know.",
    "Book recommendations from our critics.",
    "Streaming TV and movie recommendations.",
    "Get an easy version of one of the hardest crossword puzzles of the week.",
    "See all newsletters",
     "View the latest news and breaking news today for U.S., world, weather, entertainment, politics and health at CNN.com.",
     "© 2024 Cable News Network. A Warner Bros. Discovery Company. All Rights Reserved.  CNN Sans ™ & © 2016 Cable News Network.",
    "With melanoma rates rising, a skin cancer doctor shares her rules for staying protected."
]

def is_valid_summary(summary):
    """
    Check if the summary is valid (not promotional or generic).
    """
    if not summary or len(summary) < 10:
        return False
    if summary in UNWANTED_SUMMARIES:
        return False
    return True

def is_valid_news_article(headline, link, summary):
    """
    Validate a news article based on headline, link, and summary.
    """
    # Basic validation for headline and link
    if not headline or len(headline) < 10 or "http" not in link:
        return False
    # Check if summary is valid
    if not is_valid_summary(summary):
        return False
    return True
