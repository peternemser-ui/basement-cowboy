import os
import json
import requests
import logging
from base64 import b64encode
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
import subprocess
import traceback
from collections import defaultdict
from bs4 import BeautifulSoup
from io import BytesIO
import openai  
from openai import OpenAI
from dotenv import load_dotenv
from markupsafe import escape  # For safely handling user input in publish_article

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_app():
    app = Flask(__name__)

    # Constants for OpenAI API
    DALL_E_MODEL = os.getenv("DALL_E_MODEL", "dall-e-3")
    IMAGE_SIZE = os.getenv("IMAGE_SIZE", "1024x1024")

    ########################################################################
    # Load WordPress Configuration
    ########################################################################
    def load_wordpress_config():
        """
        Loads WordPress credentials from config/wordpress_config.json
        """
        config_path = os.path.join(os.path.dirname(__file__), '../config/wordpress_config.json')
        logging.info(f"Attempting to load WP config from: {config_path}")
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                wp_data = json.load(file)
                logging.info(f"Loaded WP config -> URL:{wp_data.get('wordpress_url')}, "
                             f"user:{wp_data.get('username')}")
                return wp_data
        except Exception as e:
            logging.error(f"Error loading WordPress config: {e}", exc_info=True)
            return {"wordpress_url": "", "username": "", "application_password": ""}

    wordpress_config = load_wordpress_config()
    WP_SITE = wordpress_config["wordpress_url"]
    WP_USER = wordpress_config["username"]
    WP_APP_PASSWORD = wordpress_config["application_password"]

    ########################################################################
    # Index / Review Route
    ########################################################################
    @app.route('/', endpoint='index')
    def index():
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        articles_dir = os.path.join(base_dir, 'output', 'news_articles')
        config_file = os.path.join(base_dir, 'config', 'categories.json')

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                categories = json.load(f).get("categories", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.warning(f"Error loading categories: {e}")
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

    ########################################################################
    # Load Articles
    ########################################################################
    @app.route('/load_articles', methods=['POST'], endpoint='load_articles')
    def load_articles():
        file_name = request.json.get('file_name')
        logging.info(f"Loading articles from file: {file_name}")

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        articles_dir = os.path.join(base_dir, 'output', 'news_articles')
        file_path = os.path.join(articles_dir, file_name)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)

            organized_data = defaultdict(list)
            for article in articles:
                cat = article.get('category', 'Uncategorized')
                organized_data[cat].append(article)

            output = [
                {"category": category, "articles": art_list}
                for category, art_list in organized_data.items()
            ]

            return jsonify({"success": True, "organized_articles": output})

        except Exception as e:
            logging.error(f"Error loading articles: {e}")
            return jsonify({"success": False, "error": str(e)})

    ########################################################################
    # Details Route
    ########################################################################
    @app.route('/details', methods=['POST'], endpoint='details')
    def details():
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        articles_dir = os.path.join(base_dir, 'output', 'news_articles')
        config_file = os.path.join(base_dir, 'config', 'categories.json')

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
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
            selected_articles = []
            for index in selected_indices:
                try:
                    idx = int(index)
                    if idx < len(all_articles):
                        selected_articles.append(all_articles[idx])
                except ValueError:
                    logging.error("Index was not an integer, skipping...")

        except Exception as e:
            flash(f"Error loading articles: {e}")
            logging.error(f"Error loading articles: {e}")
            selected_articles = []

        articles_by_category = {}
        for article in selected_articles:
            cat = article.get('category', 'Uncategorized')
            if cat not in articles_by_category:
                articles_by_category[cat] = []
            articles_by_category[cat].append(article)

        return render_template('details.html', articles_by_category=articles_by_category, categories=categories)

    ########################################################################
    # Regenerate Scraper
    ########################################################################
    @app.route('/regenerate_scraper', methods=['POST'], endpoint='regenerate_scraper')
    def regenerate_scraper():
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            script_path = os.path.join(base_dir, 'scraper', 'scrape_news.py')
            logging.info(f"Starting scraper: {script_path}")

            process = subprocess.Popen(
                ['python', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            def stream_logs():
                for line in process.stdout:
                    yield f"data: {line.strip()}\n\n"
                process.wait()
                if process.returncode == 0:
                    yield "data: Scraping completed successfully!\n\n"
                else:
                    yield f"data: Scraper encountered an error. Exit code: {process.returncode}\n\n"

            return app.response_class(stream_logs(), mimetype='text/event-stream')

        except Exception as e:
            logging.error(f"Error regenerating scraper: {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 500

    ########################################################################
    # Publish to WordPress
    ########################################################################

    

    @app.route('/publish_article', methods=['POST'], endpoint='publish_article')
    def publish_article():
        """
        Combine selected articles into one post and publish to WordPress.
        """
        articles = []
        for key, value in request.form.items():
            if key.startswith('title-'):
                index = key.split('-')[1]
                title = value.strip()
                publish_flag = request.form.get(f'publish-{index}') == '1'
                summary = request.form.get(f'summary-{index}', '').strip()
                link = request.form.get(f'link-{index}', '').strip()
                category = request.form.get(f'category-{index}', 'Uncategorized')
                headline = request.form.get(f'headline-{index}', 'No')
                ranking = request.form.get(f'ranking-{index}', '0')
                image_url = request.form.get(f'image-{index}', '').strip()

                if not title or not summary:
                    logging.warning(f"Skipping article index {index} (missing title or summary).")
                    continue

                articles.append({
                    "title": escape(title),
                    "publish": publish_flag,
                    "summary": escape(summary),
                    "link": escape(link) if link else None,
                    "category": category,
                    "headline": headline,
                    "ranking": ranking,
                    "image": image_url if image_url else None
                })

        if not articles:
            return jsonify({"success": False, "error": "No articles selected for publishing."}), 400

        # Load WordPress credentials
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        config_path = os.path.join(base_dir, 'config', 'wordpress_config.json')

        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                wp_conf = json.load(file)
            WP_SITE = wp_conf["wordpress_url"]
            WP_USER = wp_conf["username"]
            WP_APP_PASSWORD = wp_conf["application_password"]
        except Exception as e:
            logging.error(f"Error loading WordPress config: {e}", exc_info=True)
            return jsonify({"success": False, "error": "Failed to load WordPress configuration."}), 500

        # Structure JSON data
        structured_json = []
        articles_by_category = {}

        for article in articles:
            category = article["category"]
            if category not in articles_by_category:
                articles_by_category[category] = []
            articles_by_category[category].append(article)

        for category, cat_articles in articles_by_category.items():
            structured_json.append({"category": category, "articles": cat_articles})

        # Prepare the post content with JSON embedded
        post_data = {
            "title": "Daily News Roundup",
            "content": f"""
                <h2>Daily News Roundup</h2>
                <pre id="structured-json">{json.dumps(structured_json)}</pre>
            """,
            "status": "publish"
        }

        headers = {
            "Authorization": f"Basic {b64encode(f'{WP_USER}:{WP_APP_PASSWORD}'.encode()).decode()}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }


        try:
            logging.info(f"Publishing combined article to WordPress: {WP_SITE}")
            response = requests.post(f"{WP_SITE}/wp-json/wp/v2/posts", json=post_data, headers=headers)

            if response.status_code == 201:
                wp_response = response.json()
                post_url = wp_response.get("link", WP_SITE)
                return jsonify({"success": True, "post_url": post_url}), 201
            else:
                logging.error(f"Failed to publish: {response.status_code} - {response.text}")
                return jsonify({"success": False, "error": response.text}), response.status_code

        except Exception as e:
            logging.error(f"Error publishing: {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 500

        # ✅ Print JSON to Flask logs for debugging
        print("🔍 JSON Sent to WordPress:")
        print(json.dumps(post_data, indent=4))

        # Save JSON to a file for debugging
        with open("debug_json_output.json", "w", encoding="utf-8") as f:
            json.dump(post_data, f, indent=4)

        print("✅ JSON output saved to debug_json_output.json")


  



    ########################################################################
    # AI Route
    ########################################################################
    @app.route('/ai_summarize', methods=['POST'])
    def ai_summarize():
        """
        Summarize an article using OpenAI.
        """
        data = request.json
        link = data.get('link', '')

        if not link:
            return jsonify({"success": False, "error": "No link provided."}), 400

        logging.info(f"Summarizing article from: {link}")

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(link, headers=headers)

            if response.status_code == 403:
                logging.error("403 Forbidden: Website is blocking bots.")
                return jsonify({"success": False, "error": "Website is blocking automated access."}), 403

            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract meta description (fallback)
            meta_desc = soup.find("meta", attrs={"name": "description"})
            content = meta_desc["content"] if meta_desc else soup.get_text(separator=' ', strip=True)

            if len(content) > 4000:
                content = content[:4000]

            logging.info("Generating summary with OpenAI")

            summary_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that summarizes articles concisely."
                    },
                    {
                        "role": "user",
                        "content": f"Provide a clear, concise summary of this article: {content}"
                    }
                ],
                max_tokens=250,
                temperature=0.7
            )

            summary = summary_response.choices[0].message.content.strip()
            logging.info("Summary generated successfully")

            return jsonify({"success": True, "summary": summary})

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching article content: {e}")
            return jsonify({"success": False, "error": "Failed to fetch article. Website may be blocking bots."}), 500



    ########################################################################
    # AI Generate Image & Upload to WordPress
    ########################################################################
    @app.route('/generate_image', methods=['POST'])
    def generate_image():
        """Generates an AI-generated image using OpenAI DALL-E, uploads it to WordPress, and returns the WordPress URL."""
        try:
            data = request.json
            raw_prompt = data.get("keywords", "").strip()

            blocked_words = [
                "war", "conflict", "violence", "attack", "terrorism", "political", "protest",
                "Trump", "Biden", "Putin", "Zelenskyy", "military", "election", "government",
                "weapons", "army", "Russia", "Ukraine", "China", "bomb", "assassination", "dictator"
            ]

            sanitized_prompt = " ".join(
                ["event" if word.lower() in blocked_words else word for word in raw_prompt.split()]
            )

            if any(word in sanitized_prompt.lower() for word in blocked_words):
                sanitized_prompt = "A futuristic city skyline at sunset"

            if len(sanitized_prompt) < 10:
                sanitized_prompt = "A beautiful landscape with mountains and a lake"

            logging.info(f"Generating image for sanitized prompt: {sanitized_prompt}")

            response = client.images.generate(
                model="dall-e-3",
                prompt=sanitized_prompt,
                size="1024x1024",
                n=1
            )

            openai_image_url = response.data[0].url
            logging.info(f"Generated OpenAI image URL: {openai_image_url}")

            # Upload image to WordPress
            wp_image_url = upload_openai_image_to_wordpress(openai_image_url)
            if not wp_image_url:
                return jsonify({"success": False, "error": "Failed to upload image to WordPress"}), 500

            return jsonify({"success": True, "image_url": wp_image_url})

        except openai.BadRequestError as e:
            logging.error(f"OpenAI rejected the request: {e}")
            return jsonify({"success": False, "error": "OpenAI's safety system blocked the request."}), 400

        except Exception as e:
            logging.error(f"Error generating image: {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 500

    ########################################################################
    # Upload Images to WordPress
    ########################################################################
    def upload_openai_image_to_wordpress(image_url):
        """Downloads an OpenAI-generated image and uploads it to WordPress Media Library."""
        try:
            response = requests.get(image_url, stream=True)
            if response.status_code != 200:
                logging.error(f"Failed to download OpenAI image. Status Code: {response.status_code}")
                return None

            image_data = BytesIO(response.content)
            filename = "openai_image.jpg"
            files = {'file': (filename, image_data.read(), 'image/jpeg')}

            headers = {
                "Authorization": "Basic " + b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode(),
                "User-Agent": "Mozilla/5.0"
            }

            wp_response = requests.post(f"{WP_SITE}/wp-json/wp/v2/media", headers=headers, files=files)

            if wp_response.status_code == 201:
                wp_image_url = wp_response.json().get("source_url")
                logging.info(f"✅ Image uploaded successfully: {wp_image_url}")
                return wp_image_url
            else:
                logging.error(f"❌ WordPress Upload Failed: {wp_response.status_code} - {wp_response.text}")
                return None

        except Exception as e:
            logging.error(f"Error uploading image to WordPress: {e}", exc_info=True)
            return None

    ########################################################################
    # Generate AI Title Check
    ########################################################################
    @app.route('/ai_validate_title', methods=['POST'])
    def ai_validate_title():
        data = request.json
        title = data.get('title', '')

        if not title:
            return jsonify({"success": False, "error": "No title provided."}), 400

        try:
            ai_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant that checks news headlines for logical correctness and grammatical accuracy."},
                    {"role": "user", "content": f"Check this news title for logical correctness and syntax:\n\n'{title}'\n\nIs this title logically sound and grammatically correct? Respond briefly with your analysis."}
                ],
                max_tokens=100,
                temperature=0.3
            )

            validation_result = ai_response.choices[0].message.content.strip()
            return jsonify({"success": True, "validation_result": validation_result})

        except Exception as e:
            logging.error(f"Error validating title: {e}")
            return jsonify({"success": False, "error": str(e)}), 500


        
    ########################################################################
    # Secret Key and Return
    ########################################################################
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')
    return app
