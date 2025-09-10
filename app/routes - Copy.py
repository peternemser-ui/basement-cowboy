import os
import json
import requests
import logging
from base64 import b64encode
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import subprocess  # For improved scraper execution
import openai  # For AI integration
from tenacity import retry, stop_after_attempt, wait_fixed

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Load WordPress configuration
def load_wordpress_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config/wordpress_config.json')
    try:
        with open(config_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading WordPress configuration: {e}")
        raise RuntimeError("Failed to load WordPress configuration.")

wordpress_config = load_wordpress_config()
WP_SITE = wordpress_config["wordpress_url"]
WP_USER = wordpress_config["username"]
WP_APP_PASSWORD = wordpress_config["application_password"]

# Load OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

    @app.route('/')
    def index():
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        articles_dir = os.path.join(base_dir, 'output', 'news_articles')
        config_file = os.path.join(base_dir, 'config', 'categories.json')

        try:
            with open(config_file, 'r') as f:
                categories = json.load(f).get("categories", [])
        except (FileNotFoundError, json.JSONDecodeError):
            categories = ["Uncategorized"]

        try:
            os.makedirs(articles_dir, exist_ok=True)
            json_files = sorted(
                [f for f in os.listdir(articles_dir) if f.endswith('.json')],
                reverse=True
            )
        except Exception as e:
            flash("Failed to load articles directory.")
            logging.error(f"Error accessing directory {articles_dir}: {e}")
            json_files = []

        articles = []
        if json_files:
            try:
                latest_file = os.path.join(articles_dir, json_files[0])
                with open(latest_file, encoding='utf-8') as f:
                    articles = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                flash(f"Error loading articles: {e}")
                logging.error(f"Error loading articles: {e}")

        return render_template('review.html', articles=articles, files=json_files, categories=categories)

    @app.route('/load_articles', methods=['POST'])
    def load_articles():
        """Load articles from the selected JSON file."""
        file_name = request.json.get('file_name')
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        articles_dir = os.path.join(base_dir, 'output', 'news_articles')
        file_path = os.path.join(articles_dir, file_name)

        try:
            with open(file_path, encoding='utf-8') as f:
                articles = json.load(f)
            return jsonify({"success": True, "articles": articles})
        except Exception as e:
            logging.error(f"Error loading articles from {file_name}: {e}")
            return jsonify({"success": False, "error": str(e)})

    @app.route('/details', methods=['POST'])
    def details():
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        articles_dir = os.path.join(base_dir, 'output', 'news_articles')
        config_file = os.path.join(base_dir, 'config', 'categories.json')

        try:
            with open(config_file, 'r') as f:
                categories = json.load(f).get("categories", [])
        except (FileNotFoundError, json.JSONDecodeError):
            categories = ["Uncategorized"]

        try:
            json_files = sorted(
                [f for f in os.listdir(articles_dir) if f.endswith('.json')],
                reverse=True
            )
            latest_file = os.path.join(articles_dir, json_files[0])
            with open(latest_file, encoding='utf-8') as f:
                all_articles = json.load(f)

            selected_indices = request.form.getlist('selected_articles')
            selected_articles = [all_articles[int(index)] for index in selected_indices]
        except Exception as e:
            flash(f"Error loading articles: {e}")
            logging.error(f"Error loading articles: {e}")
            selected_articles = []

        articles_by_category = {}
        for article in selected_articles:
            category = article.get('category', 'Uncategorized')
            if category not in articles_by_category:
                articles_by_category[category] = []
            articles_by_category[category].append(article)

        return render_template('details.html', articles_by_category=articles_by_category, categories=categories)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def generate_summary_with_retry(link):
        response = requests.get(link)
        response.raise_for_status()
        content = response.text
        ai_response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Summarize this article:\n\n{content}",
            max_tokens=150,
        )
        return ai_response.choices[0].text.strip()

    @app.route('/regenerate_scraper', methods=['POST'])
    def regenerate_scraper():
        """Run the scraper script to regenerate articles."""
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        scraper_script = os.path.join(base_dir, 'scraper', 'scrape_news.py')

        try:
            logging.info(f"Running scraper script: {scraper_script}")
            result = subprocess.run(
                ['python', scraper_script],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logging.info("Scraper executed successfully.")
                return jsonify({"success": True, "message": "Scraper executed successfully."}), 200
            else:
                logging.error(f"Scraper failed: {result.stderr}")
                return jsonify({"success": False, "error": result.stderr}), 500
        except Exception as e:
            logging.error(f"Error during scraper execution: {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 500


    @app.route('/ai_summarize', methods=['POST'])
    def ai_summarize():
        """Generate a summary for the given article."""
        data = request.json
        link = data.get('link')

        if not link:
            return jsonify({"success": False, "error": "No link provided."}), 400

        try:
            summary = generate_summary_with_retry(link)
            return jsonify({"success": True, "summary": summary})
        except Exception as e:
            logging.error(f"Error generating summary: {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/ai_categorize', methods=['POST'])
    def ai_categorize():
        """Categorize an article headline using AI."""
        data = request.json
        headline = data.get('headline')

        if not headline:
            return jsonify({"success": False, "error": "No headline provided."}), 400

        try:
            ai_response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Categorize this headline into: News, Politics, Technology, Health, Economy, Entertainment:\n\n{headline}\n\nCategory:",
                max_tokens=10,
            )
            category = ai_response.choices[0].text.strip()
            return jsonify({"success": True, "category": category})
        except Exception as e:
            logging.error(f"Error categorizing headline: {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/publish_article', methods=['POST'])
    def publish_article():
        """Combine selected articles into one post and publish to WordPress."""
        from markupsafe import escape

        # Parse form data
        articles = []
        for key, value in request.form.items():
            if key.startswith('title-'):
                index = key.split('-')[1]
                title = value.strip()
                publish = request.form.get(f'publish-{index}') == '1'
                summary = request.form.get(f'summary-{index}', '').strip()
                image = request.form.get(f'image-{index}', '').strip()
                link = request.form.get(f'link-{index}', '').strip()

                if not title or not summary:
                    logging.warning(f"Skipping article with missing title or summary at index {index}")
                    continue

                articles.append({
                    "title": escape(title),
                    "publish": publish,
                    "summary": escape(summary),
                    "image": escape(image) if image else None,
                    "link": escape(link) if link else None,
                })

        # Helper function to generate HTML
        def generate_combined_content(articles):
            combined_html = "<ul>\n"
            for article in articles:
                if article["publish"]:
                    combined_html += "<li>\n"
                    if article["link"]:
                        combined_html += f'  <a href="{article["link"]}" target="_blank" rel="noopener noreferrer">\n'
                    if article["image"]:
                        combined_html += (
                            f'    <img src="{article["image"]}" alt="{article["title"]}" '
                            f'style="max-width:100px; height:auto; display:block; margin-bottom:10px;">\n'
                        )
                    combined_html += f'    <strong>{article["title"]}</strong>\n'
                    combined_html += f'    <p>{article["summary"]}</p>\n'
                    if article["link"]:
                        combined_html += "  </a>\n"
                    combined_html += "</li>\n"
            combined_html += "</ul>\n"
            return combined_html

        # Generate combined content
        combined_content = generate_combined_content(articles)

        if combined_content.strip() != "<ul>\n</ul>":  # Check if there's content to publish
            wp_data = {
                "title": "Daily News Roundup",
                "content": "<ul><li>Test content without links</li></ul>",
                "status": "publish",
            }
            headers = {
                "Authorization": f"Basic {b64encode(f'{WP_USER}:{WP_APP_PASSWORD}'.encode()).decode()}",
                "Content-Type": "application/json",
            }

            # Enhanced logging and error handling
            try:
                logging.debug(f"Publishing to WordPress: {wp_data}")
                response = requests.post(f"{WP_SITE}/wp-json/wp/v2/posts", json=wp_data, headers=headers)

                if response.status_code == 201:
                    logging.info("Successfully published combined post.")
                    flash("Successfully published combined post.")
                else:
                    logging.error(f"Failed to publish combined post: {response.status_code} - {response.text}")
                    logging.error(f"Response Headers: {response.headers}")
                    flash(f"Failed to publish combined post: {response.status_code}")
            except requests.RequestException as e:
                logging.error(f"Error during WordPress API call: {e}", exc_info=True)
                flash("An error occurred while publishing the article. Please try again.")
        else:
            flash("No articles selected for publishing.")

        return redirect(url_for('index'))


    @app.route('/proxy/<path:url>')
    def proxy(url):
        from urllib.parse import urlparse

        ALLOWED_DOMAINS = ["example.com", "trusted.com"]

        parsed_url = urlparse(url)
        if parsed_url.netloc not in ALLOWED_DOMAINS:
            return "Forbidden domain", 403

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.content, response.status_code, response.headers.items()
        except Exception as e:
            logging.error(f"Proxy error: {e}", exc_info=True)
            return "Failed to fetch content", 500

    return app
