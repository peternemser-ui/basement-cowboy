import openai
import logging

# Summarization Function
def extract_summary_with_ai(text, max_length=100):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize this article content in {max_length} words:\n\n{text}",
            max_tokens=200,
            temperature=0.7,
        )
        return response['choices'][0]['text'].strip()
    except Exception as e:
        logging.error(f"AI summarization failed: {e}")
        return None

# Classification Function
def classify_article_with_ai(title, content):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Categorize the following article into one of these categories: Politics, Technology, Health, Economy, Entertainment, or News.\n\n"
                   f"Title: {title}\n"
                   f"Content: {content}\n\n"
                   f"Category:",
            max_tokens=10,
            temperature=0.5,
        )
        return response['choices'][0]['text'].strip()
    except Exception as e:
        logging.error(f"AI classification failed: {e}")
        return "Uncategorized"
