import os
import json
import requests
import logging
from datetime import datetime
from base64 import b64encode
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, session
import subprocess
import traceback
from collections import defaultdict
from bs4 import BeautifulSoup
from io import BytesIO
import openai  
from openai import OpenAI
from dotenv import load_dotenv
from markupsafe import escape  # For safely handling user input in publish_article
# from .wordpress_graphql import create_wordpress_graphql_client  # Commented out temporarily

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

# OpenAI client will be initialized per request using session API key
# No global client initialization with environment variables

def create_app():

    app = Flask(__name__)

    ########################################################################
    # API Key Validation Endpoint
    ########################################################################
    @app.route('/validate_api_key', methods=['POST'])
    def validate_api_key():
        data = request.json
        logging.info("/validate_api_key called")
        try:
            # redact the API key before writing debug info
            redacted = dict(data) if isinstance(data, dict) else {}
            if 'api_key' in redacted:
                k = redacted.get('api_key') or ''
                if isinstance(k, str) and len(k) > 8:
                    redacted['api_key'] = k[:4] + '...' + k[-4:]
                else:
                    redacted['api_key'] = 'REDACTED'
            with open('debug_validate_request_redacted.json', 'w', encoding='utf-8') as f:
                json.dump(redacted, f, indent=2)
        except Exception:
            logging.exception('Failed to write debug_validate_request_redacted.json')
        api_key = data.get('api_key', '').strip()
        if not api_key:
            return jsonify({"success": False, "error": "No API key provided."}), 400
        try:
            # Prefer a direct HTTP call to OpenAI for consistent error payloads
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            resp = requests.get('https://api.openai.com/v1/models', headers=headers, timeout=10)
            # write response for debugging
            try:
                with open('debug_validate_response.log', 'w', encoding='utf-8') as f:
                    f.write(f'STATUS: {resp.status_code}\n')
                    f.write(resp.text)
            except Exception:
                logging.exception('Failed to write debug_validate_response.log')
            # If successful, return a summary of accessible models
            if resp.status_code == 200:
                body = resp.json()
                models = [m.get('id') for m in body.get('data', []) if m.get('id')]
                # Check for common capabilities
                has_chat = any('gpt-4' in m or 'gpt-3.5' in m or 'turbo' in m for m in models)
                has_images = any('image' in m or 'dall' in m or 'dalle' in m for m in models)
                # store validated key in session for subsequent requests
                try:
                    session['OPENAI_API_KEY'] = api_key
                except Exception:
                    logging.exception('Failed to store API key in session')
                return jsonify({
                    'success': True,
                    'models_count': len(models),
                    'models': models[:20],
                    'has_chat': has_chat,
                    'has_images': has_images,
                    'stored_in_session': True
                })
            else:
                # Try to parse JSON error message from OpenAI
                try:
                    err = resp.json()
                    message = err.get('error', {}).get('message') if isinstance(err, dict) else str(err)
                except Exception:
                    message = resp.text or f'Status code {resp.status_code}'
                return jsonify({"success": False, "error": message, 'status_code': resp.status_code}), resp.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/ping', methods=['GET'])
    def ping():
        return jsonify({'ok': True, 'msg': 'pong'})

    @app.route('/logout', methods=['POST', 'GET'])
    def logout():
        """Clear the OpenAI API key from session"""
        session.pop('OPENAI_API_KEY', None)
        if request.method == 'POST':
            return jsonify({"success": True, "message": "API key cleared from session"})
        else:
            return redirect(url_for('index'))

    # Temporary: allow unsafe-eval in development for debugging CSP issues.
    # To enable, set environment variable: ALLOW_UNSAFE_EVAL_FOR_DEV=1
    # WARNING: This weakens CSP and should NEVER be enabled in production.
    if os.getenv('ALLOW_UNSAFE_EVAL_FOR_DEV') == '1':
        @app.after_request
        def add_csp_header(response):
            try:
                # This policy allows eval/use of Function constructor for debugging only
                response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-eval' 'unsafe-inline' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:;"
            except Exception:
                logging.exception('Failed to add CSP header')
            return response

    # Helper function for sorting news article files chronologically
    def sort_files_by_datetime(filename):
        """Sort news article files by datetime, handling both old and new filename formats."""
        try:
            # Extract date and session number from filename like: news_articles_2025-09-17-2.json
            if filename.startswith('news_articles_') and filename.endswith('.json'):
                # Remove prefix and suffix
                date_part = filename[14:-5]  # Remove 'news_articles_' and '.json'
                
                # Handle both old format (YYYY-MM-DD_HH-MM-SS) and new format (YYYY-MM-DD-N)
                if '_' in date_part:
                    # Old format: 2024-12-31_13-13-01
                    date_str, time_str = date_part.split('_', 1)
                    # Convert to datetime for proper sorting
                    from datetime import datetime
                    dt = datetime.strptime(f"{date_str} {time_str.replace('-', ':')}", "%Y-%m-%d %H:%M:%S")
                    return dt
                else:
                    # New format: 2025-09-17-2
                    parts = date_part.split('-')
                    if len(parts) == 4:  # YYYY-MM-DD-N
                        year, month, day, session = parts
                        # Create a datetime with session number as microseconds for sub-day ordering
                        from datetime import datetime
                        dt = datetime(int(year), int(month), int(day))
                        # Add session number as microseconds to ensure proper ordering within the day
                        return dt.replace(microsecond=int(session) * 1000)
            
            # Fallback to filename if parsing fails
            return filename
        except Exception:
            # If parsing fails, fall back to filename sorting
            return filename

    # Helper to create OpenAI client from session key only
    def get_openai_client():
        api_key = session.get('OPENAI_API_KEY')
        if api_key:
            return OpenAI(api_key=api_key)
        else:
            # Return None if no API key in session - calling code should handle this
            return None

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
    # Index Route - Check API Key First
    ########################################################################
    @app.route('/', endpoint='index')
    def index():
        # Check if OpenAI API key is validated in session
        if 'OPENAI_API_KEY' not in session:
            return render_template('api_key_form.html')
        
        # API key exists, proceed to review page
        return redirect(url_for('review'))

    ########################################################################
    # Review Route (formerly index)
    ########################################################################
    @app.route('/review', endpoint='review')
    def review():
        # Ensure API key is still in session
        if 'OPENAI_API_KEY' not in session:
            return redirect(url_for('index'))
            
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
            all_json_files = [f for f in os.listdir(articles_dir) if f.endswith('.json')]
            json_files = sorted(all_json_files, key=sort_files_by_datetime, reverse=True)
            
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
    @app.route('/details', methods=['GET', 'POST'], endpoint='details')
    def details():
        # Ensure API key is still in session
        if 'OPENAI_API_KEY' not in session:
            return redirect(url_for('index'))
            
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        articles_dir = os.path.join(base_dir, 'output', 'news_articles')
        config_file = os.path.join(base_dir, 'config', 'categories.json')

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                categories = json.load(f).get("categories", [])
        except (FileNotFoundError, json.JSONDecodeError):
            categories = ["Uncategorized"]

        try:
            all_json_files = [f for f in os.listdir(articles_dir) if f.endswith('.json')]
            json_files = sorted(all_json_files, key=sort_files_by_datetime, reverse=True)
            latest_file = os.path.join(articles_dir, json_files[0])
            with open(latest_file, encoding='utf-8') as f:
                all_articles = json.load(f)


            # For GET requests, show all articles; for POST, filter by selected
            if request.method == 'POST':
                selected_indices = request.form.getlist('selected_articles')
                selected_articles = []
                for index in selected_indices:
                    try:
                        idx = int(index)
                        if idx < len(all_articles):
                            selected_articles.append(all_articles[idx])
                    except ValueError:
                        logging.error("Index was not an integer, skipping...")
            else:
                selected_articles = all_articles

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
        def stream_logs():
            try:
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                script_path = os.path.join(base_dir, 'scraper', 'scrape_news.py')
                python_exe = r"C:/Users/Peter/AppData/Local/Programs/Python/Python313/python.exe"
                
                logging.info(f"Starting scraper: {script_path}")
                logging.info(f"Using Python executable: {python_exe}")
                
                # Send initial progress
                yield "data: PROGRESS:0:Initializing scraper...\n\n"

                process = subprocess.Popen(
                    [python_exe, script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=base_dir,
                    bufsize=1,  # Line buffered
                    universal_newlines=True
                )

                site_count = 0
                total_sites = 180  # Approximate number of sites
                
                for line in process.stdout:
                    line_stripped = line.strip()
                    if line_stripped:
                        # Check for progress indicators and send structured progress
                        if "Processing site:" in line_stripped:
                            site_count += 1
                            progress = min((site_count / total_sites) * 95, 95)  # Keep some room for completion
                            yield f"data: PROGRESS:{progress}:Processing site {site_count}/{total_sites}\n\n"
                        elif "Scraping complete" in line_stripped:
                            yield "data: PROGRESS:100:Scraping completed successfully!\n\n"
                        elif "Found" in line_stripped and "articles" in line_stripped:
                            yield f"data: INFO:{line_stripped}\n\n"
                        elif "ERROR" in line_stripped or "Error" in line_stripped:
                            yield f"data: ERROR:{line_stripped}\n\n"
                        elif "Saving" in line_stripped:
                            yield "data: PROGRESS:90:Saving articles to file...\n\n"
                        
                        # Send all log output for debugging
                        yield f"data: LOG:{line_stripped}\n\n"
                
                process.wait()
                if process.returncode == 0:
                    yield "data: PROGRESS:100:Scraping completed successfully!\n\n"
                    yield "data: SUCCESS:Scraper finished successfully\n\n"
                else:
                    yield f"data: ERROR:Scraper encountered an error. Exit code: {process.returncode}\n\n"
                    
            except Exception as e:
                logging.error(f"Error regenerating scraper: {e}", exc_info=True)
                import traceback
                tb = traceback.format_exc()
                yield f"data: ERROR:SERVER ERROR: {str(e)}\n\n"
                yield f"data: ERROR:TRACEBACK: {tb}\n\n"

        response = app.response_class(stream_logs(), mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Connection'] = 'keep-alive'
        return response

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
        # Create HTML content with images displayed properly - WordPress theme override
        html_content = """
        <style>
        /* Force display images - override any theme CSS */
        .bc-news-container * {
            box-sizing: border-box !important;
        }
        .bc-news-container {
            width: 100% !important;
            margin: 20px 0 !important;
            padding: 0 !important;
            background: #ffffff !important;
        }
        .bc-news-article {
            margin: 30px 0 !important;
            padding: 25px !important;
            border: 2px solid #e1e5e9 !important;
            border-radius: 12px !important;
            background: #ffffff !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            clear: both !important;
            overflow: hidden !important;
        }
        .bc-news-article img {
            max-width: 100% !important;
            width: auto !important;
            height: auto !important;
            display: block !important;
            margin: 0 0 20px 0 !important;
            border-radius: 8px !important;
            border: none !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
            object-fit: cover !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        .bc-news-article h4 {
            color: #1a1a1a !important;
            font-size: 24px !important;
            font-weight: bold !important;
            margin: 15px 0 12px 0 !important;
            line-height: 1.3 !important;
            display: block !important;
        }
        .bc-news-article p {
            color: #333333 !important;
            font-size: 16px !important;
            line-height: 1.6 !important;
            margin: 0 0 15px 0 !important;
            display: block !important;
        }
        .bc-news-article a {
            color: #0073aa !important;
            text-decoration: underline !important;
            font-weight: bold !important;
        }
        .bc-category-title {
            color: #0073aa !important;
            font-size: 28px !important;
            font-weight: bold !important;
            margin: 40px 0 20px 0 !important;
            border-bottom: 3px solid #0073aa !important;
            padding-bottom: 10px !important;
            display: block !important;
        }
        /* Hide the JSON section by default */
        .bc-raw-data {
            margin-top: 50px !important;
            padding: 20px !important;
            background: #f8f9fa !important;
            border: 1px solid #dee2e6 !important;
            border-radius: 6px !important;
        }
        .bc-raw-data summary {
            font-weight: bold !important;
            cursor: pointer !important;
            padding: 10px !important;
            background: #e9ecef !important;
            border-radius: 4px !important;
        }
        .bc-raw-data pre {
            background: #ffffff !important;
            padding: 15px !important;
            border-radius: 4px !important;
            overflow-x: auto !important;
            font-size: 12px !important;
            border: 1px solid #ced4da !important;
        }
        </style>
        <div class="bc-news-container">
        <h2 style="color: #1a1a1a !important; font-size: 36px !important; font-weight: bold !important; margin: 30px 0 !important; text-align: center !important;">Daily News Roundup</h2>
        """
        
        for category_data in structured_json:
            category = category_data.get("category", "Uncategorized")
            articles = category_data.get("articles", [])
            
            if articles:
                html_content += f'<h3 class="bc-category-title">{category}</h3>\n'
                
                for article in articles:
                    if article.get("publish", False):
                        html_content += '<div class="bc-news-article">\n'
                        
                        # Add image if available with enhanced styling and alt text
                        image_url = article.get("image")
                        if image_url:
                            title = article.get("title", "News Image").replace('"', '&quot;')
                            html_content += f'<img src="{image_url}" alt="{title}" loading="lazy" />\n'
                        
                        # Add title
                        title = article.get('title', 'Untitled')
                        html_content += f"<h4>{title}</h4>\n"
                        
                        # Add summary
                        summary = article.get("summary", "")
                        if summary:
                            html_content += f"<p>{summary}</p>\n"
                        
                        # Add source link if available
                        link = article.get("link")
                        if link:
                            html_content += f'<p><a href="{link}" target="_blank" rel="noopener">📖 Read Full Article</a></p>\n'
                        
                        html_content += "</div>\n"

        html_content += """
        </div>
        
        <div class="bc-raw-data">
            <details>
                <summary>🔧 Technical Data (for developers)</summary>
                <pre id="structured-json">{}</pre>
            </details>
        </div>
        """.format(json.dumps(structured_json, indent=2))

        post_data = {
            "title": "Daily News Roundup",
            "content": html_content,
            "status": "publish"
        }

        headers = {
            "Authorization": f"Basic {b64encode(f'{WP_USER}:{WP_APP_PASSWORD}'.encode()).decode()}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Ch-Ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Origin": "https://basementcowboy.com",
            "Referer": "https://basementcowboy.com/wp-admin/"
        }


        try:
            logging.info(f"Publishing combined article to WordPress: {WP_SITE}")
            
            # Create a session for better Cloudflare handling
            session = requests.Session()
            session.headers.update(headers)
            
            # First, try to get the main site to establish session/cookies
            try:
                logging.info("Establishing session with WordPress site...")
                warmup_response = session.get(f"{WP_SITE}/", timeout=30)
                logging.info(f"Warmup request status: {warmup_response.status_code}")
            except Exception as warmup_error:
                logging.warning(f"Warmup request failed: {warmup_error}")
            
            # Small delay to avoid rate limiting
            import time
            time.sleep(2)
            
            # Now make the actual API request
            api_url = f"{WP_SITE}/wp-json/wp/v2/posts"
            logging.info(f"Making API request to: {api_url}")
            response = session.post(api_url, json=post_data, timeout=60)
            
            logging.info(f"API Response status: {response.status_code}")
            logging.info(f"API Response headers: {dict(response.headers)}")
            
            if response.status_code == 201:
                wp_response = response.json()
                post_url = wp_response.get("link", WP_SITE)
                
                # Count published articles and images
                published_articles = [a for a in articles if a.get("publish", False)]
                total_images = sum(1 for a in published_articles if a.get("image"))
                
                # Enhanced JSON response with detailed information
                enhanced_response = {
                    "success": True,
                    "wordpress": {
                        "post_id": wp_response.get("id"),
                        "post_url": post_url,
                        "post_title": wp_response.get("title", {}).get("rendered", "Daily News Roundup"),
                        "post_status": wp_response.get("status"),
                        "post_date": wp_response.get("date"),
                        "post_modified": wp_response.get("modified")
                    },
                    "publication_stats": {
                        "total_articles_processed": len(articles),
                        "articles_published": len(published_articles),
                        "articles_skipped": len(articles) - len(published_articles),
                        "images_included": total_images,
                        "categories_used": len(set(a["category"] for a in published_articles))
                    },
                    "categories": {
                        category: {
                            "article_count": len(cat_articles),
                            "published_count": len([a for a in cat_articles if a.get("publish", False)]),
                            "image_count": len([a for a in cat_articles if a.get("publish", False) and a.get("image")])
                        }
                        for category, cat_articles in articles_by_category.items()
                    },
                    "published_articles": [
                        {
                            "title": a["title"],
                            "category": a["category"],
                            "has_image": bool(a.get("image")),
                            "image_url": a.get("image"),
                            "has_link": bool(a.get("link")),
                            "link": a.get("link"),
                            "summary_length": len(a.get("summary", "")),
                            "headline_status": a.get("headline", "No")
                        }
                        for a in published_articles
                    ],
                    "content_analysis": {
                        "html_content_length": len(html_content),
                        "json_data_size": len(json.dumps(structured_json)),
                        "total_post_size": len(html_content)
                    },
                    "technical_details": {
                        "wordpress_site": WP_SITE,
                        "publishing_method": "WordPress REST API",
                        "content_format": "HTML with embedded JSON",
                        "image_display_system": "Enhanced CSS with theme override",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                return jsonify(enhanced_response), 201
            else:
                # Enhanced error response
                error_response = {
                    "success": False,
                    "error": {
                        "message": "WordPress publishing failed",
                        "status_code": response.status_code,
                        "response_text": response.text,
                        "wordpress_site": WP_SITE
                    },
                    "attempted_publication": {
                        "total_articles": len(articles),
                        "articles_to_publish": len([a for a in articles if a.get("publish", False)]),
                        "post_title": post_data["title"],
                        "content_length": len(post_data["content"])
                    },
                    "timestamp": datetime.now().isoformat()
                }
                logging.error(f"Failed to publish: {response.status_code} - {response.text}")
                return jsonify(error_response), response.status_code

        except Exception as e:
            # Enhanced exception response
            exception_response = {
                "success": False,
                "error": {
                    "type": "Exception",
                    "message": str(e),
                    "details": "An unexpected error occurred during publishing"
                },
                "context": {
                    "wordpress_site": WP_SITE,
                    "total_articles": len(articles),
                    "articles_to_publish": len([a for a in articles if a.get("publish", False)])
                },
                "timestamp": datetime.now().isoformat()
            }
            logging.error(f"Error publishing: {e}", exc_info=True)
            return jsonify(exception_response), 500

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
            oclient = get_openai_client()
            if not oclient:
                return jsonify({"success": False, "error": "OpenAI API key not available. Please validate your API key first."}), 401
            try:
                summary_response = oclient.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an assistant that summarizes articles concisely."},
                        {"role": "user", "content": f"Provide a clear, concise summary of this article: {content}"}
                    ],
                    max_tokens=250,
                    temperature=0.7
                )
                summary = summary_response.choices[0].message.content.strip()
                logging.info("Summary generated successfully")
                return jsonify({"success": True, "summary": summary})
            except Exception as e:
                logging.error(f"OpenAI error in summarization: {e}", exc_info=True)
                return jsonify({"success": False, "error": str(e)}), 500

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
            logging.info('generate_image called')
            logging.info(f"session keys: {list(session.keys())}")
            try:
                redacted_key = None
                if 'OPENAI_API_KEY' in session:
                    k = session.get('OPENAI_API_KEY') or ''
                    if isinstance(k, str) and len(k) > 8:
                        redacted_key = k[:4] + '...' + k[-4:]
                    else:
                        redacted_key = 'REDACTED'
                logging.info(f"session OPENAI_API_KEY redacted: {redacted_key}")
            except Exception:
                logging.exception('Error reading session key')
            data = request.json
            raw_prompt = data.get("keywords", "").strip()
            logging.info(f"generate_image payload keywords len={len(raw_prompt)}")

            blocked_words = [
                "war", "conflict", "violence", "attack", "terrorism", "terrorist", "political", "protest",
                "Trump", "Biden", "Putin", "Zelenskyy", "military", "election", "government", "politician",
                "weapons", "army", "Russia", "Ukraine", "China", "bomb", "assassination", "dictator",
                "shooting", "gun", "weapon", "murder", "death", "kill", "suicide", "drugs", "alcohol",
                "naked", "nude", "sex", "sexual", "porn", "adult", "controversial", "scandal", "riot",
                "blood", "gore", "disturbing", "hate", "racist", "discrimination", "slavery", "holocaust"
            ]

            # More robust sanitization - replace problematic words and add safe context
            sanitized_words = []
            for word in raw_prompt.split():
                if word.lower() in blocked_words:
                    sanitized_words.append("news")
                else:
                    sanitized_words.append(word)
            
            sanitized_prompt = " ".join(sanitized_words)
            
            # Double check - if any blocked words still exist, use a completely safe prompt
            if any(blocked_word in sanitized_prompt.lower() for blocked_word in blocked_words):
                sanitized_prompt = "A professional news studio with modern equipment and soft lighting"

            # Ensure minimum length and add safe context for news images
            if len(sanitized_prompt) < 10:
                sanitized_prompt = "A modern newsroom with computers and monitors displaying information"
            
            # Add safe, professional context to any prompt
            if not any(safe_word in sanitized_prompt.lower() for safe_word in ["studio", "newsroom", "office", "building", "landscape", "abstract"]):
                sanitized_prompt = f"A professional news-style image representing: {sanitized_prompt}, clean and modern style"

            logging.info(f"Generating image for sanitized prompt: {sanitized_prompt}")

            def _try_parse_image_response(response_obj):
                """Normalize various OpenAI response shapes to (openai_image_url, image_bytes, raw_response)"""
                openai_image_url = None
                image_bytes = None
                try:
                    data_item = None
                    if isinstance(response_obj, dict):
                        data = response_obj.get('data')
                        if data and len(data) > 0:
                            data_item = data[0]
                    else:
                        data = getattr(response_obj, 'data', None)
                        if data and len(data) > 0:
                            data_item = data[0]

                    if data_item is not None:
                        b64_field = None
                        if isinstance(data_item, dict):
                            b64_field = data_item.get('b64_json') or data_item.get('b64')
                            openai_image_url = data_item.get('url') or data_item.get('image_url')
                        else:
                            b64_field = getattr(data_item, 'b64_json', None) or getattr(data_item, 'b64', None)
                            openai_image_url = getattr(data_item, 'url', None) or getattr(data_item, 'image_url', None)

                        if b64_field:
                            import base64
                            image_bytes = base64.b64decode(b64_field)
                    else:
                        logging.debug('No data items in image response')
                except Exception:
                    logging.exception('Error parsing image response')
                return openai_image_url, image_bytes

            def openai_generate(prompt_text):
                """Try multiple methods to generate images: SDK client, openai module, HTTP fallback."""
                api_key = session.get('OPENAI_API_KEY')
                if not api_key:
                    raise RuntimeError('No OpenAI API key available in session. Please validate your API key first.')
                    
                # 1) Try SDK-style client (OpenAI from openai import OpenAI)
                try:
                    oclient = get_openai_client()
                    if oclient and hasattr(oclient, 'images') and hasattr(oclient.images, 'generate'):
                        resp = oclient.images.generate(model=DALL_E_MODEL, prompt=prompt_text, size=IMAGE_SIZE, n=1)
                        url, bts = _try_parse_image_response(resp)
                        if url or bts:
                            return url, bts, resp
                except Exception:
                    logging.exception('SDK client image generation failed')

                # 2) Try the older openai.Image.create method if available
                try:
                    if hasattr(openai, 'Image') and hasattr(openai.Image, 'create'):
                        # set api key for openai module
                        try:
                            openai.api_key = api_key
                        except Exception:
                            logging.debug('Failed to set openai.api_key')
                        resp = openai.Image.create(prompt=prompt_text, n=1, size=IMAGE_SIZE)
                        url, bts = _try_parse_image_response(resp)
                        if url or bts:
                            return url, bts, resp
                except Exception:
                    logging.exception('openai.Image.create fallback failed')

                # 3) HTTP fallback to OpenAI Images API
                try:
                    if not api_key:
                        raise RuntimeError('No OpenAI API key available for HTTP fallback')
                    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
                    payload = {'model': DALL_E_MODEL, 'prompt': prompt_text, 'n': 1, 'size': IMAGE_SIZE}
                    r = requests.post('https://api.openai.com/v1/images/generations', headers=headers, json=payload, timeout=30)
                    if r.status_code == 200:
                        jr = r.json()
                        url, bts = _try_parse_image_response(jr)
                        if url or bts:
                            return url, bts, jr
                        else:
                            logging.debug('HTTP response had no usable image data')
                    else:
                        logging.error(f'HTTP fallback returned {r.status_code}: {r.text}')
                except Exception:
                    logging.exception('HTTP fallback for image generation failed')

                # If all methods failed
                raise RuntimeError('All OpenAI image generation methods failed')

            try:
                openai_image_url, image_bytes, raw_resp = openai_generate(sanitized_prompt)

                # Prefer returning a WordPress-hosted URL when available, but fall back to
                # returning the OpenAI URL or base64 image data so the client can display it
                client_image_url = None
                b64_string = None

                if openai_image_url:
                    logging.info(f"Generated OpenAI image URL: {openai_image_url}")
                    wp_image_url = upload_openai_image_to_wordpress(openai_image_url)
                    client_image_url = wp_image_url or openai_image_url
                elif image_bytes:
                    logging.info('Generated OpenAI image as base64; uploading bytes to WordPress')
                    wp_image_url = upload_openai_image_to_wordpress(image_bytes)
                    if wp_image_url:
                        client_image_url = wp_image_url
                    else:
                        # encode bytes for client-side display
                        import base64
                        b64_string = base64.b64encode(image_bytes).decode('ascii')
                        client_image_url = None
                else:
                    logging.error('No image returned from OpenAI (no url or b64 data)')
                    try:
                        with open('debug_generate_image_error.json', 'w', encoding='utf-8') as f:
                            json.dump({'error': 'no_image_in_response', 'response': repr(raw_resp)}, f, indent=2)
                    except Exception:
                        logging.exception('Failed to write debug_generate_image_error.json')
                    return jsonify({"success": False, "error": "OpenAI returned no image."}), 500

                # If upload failed but we have b64 or openai url, return that to client so UI can show it
                resp_payload = {'success': True}
                if client_image_url:
                    resp_payload['image_url'] = client_image_url
                if b64_string:
                    resp_payload['b64'] = b64_string

                return jsonify(resp_payload)
            except Exception as e:
                logging.error(f"OpenAI image generation error: {e}", exc_info=True)
                try:
                    import traceback as tb
                    info = {'error': str(e), 'traceback': tb.format_exc()}
                    try:
                        k = session.get('OPENAI_API_KEY') or ''
                        if isinstance(k, str) and len(k) > 8:
                            info['openai_key_redacted'] = k[:4] + '...' + k[-4:]
                        elif k:
                            info['openai_key_redacted'] = 'REDACTED'
                    except Exception:
                        info['openai_key_redacted'] = 'ERROR'
                    try:
                        info['payload'] = {'keywords_len': len(data.get('keywords', ''))}
                    except Exception:
                        info['payload'] = 'unavailable'
                    with open('debug_generate_image_error.json', 'w', encoding='utf-8') as f:
                        json.dump(info, f, indent=2)
                except Exception:
                    logging.exception('Failed to write debug_generate_image_error.json')
                return jsonify({"success": False, "error": str(e)}), 500

        except openai.BadRequestError as e:
            logging.error(f"OpenAI rejected the request: {e}")
            return jsonify({"success": False, "error": "OpenAI's safety system blocked the request."}), 400

        except Exception as e:
            logging.error(f"Error generating image: {e}", exc_info=True)
            # write a redacted debug file with traceback and session info
            try:
                import traceback as tb
                info = {
                    'error': str(e),
                    'traceback': tb.format_exc()
                }
                try:
                    k = session.get('OPENAI_API_KEY') or ''
                    if isinstance(k, str) and len(k) > 8:
                        info['openai_key_redacted'] = k[:4] + '...' + k[-4:]
                    elif k:
                        info['openai_key_redacted'] = 'REDACTED'
                except Exception:
                    info['openai_key_redacted'] = 'ERROR'
                try:
                    info['payload'] = { 'keywords_len': len(data.get('keywords','')) }
                except Exception:
                    info['payload'] = 'unavailable'
                with open('debug_generate_image_error.json', 'w', encoding='utf-8') as f:
                    json.dump(info, f, indent=2)
            except Exception:
                logging.exception('Failed to write debug_generate_image_error.json')
            return jsonify({"success": False, "error": "Internal server error. See server logs."}), 500

    ########################################################################
    # Upload Images to WordPress
    ########################################################################
    def upload_openai_image_to_wordpress(image):
        """Uploads an image to WordPress using GraphQL. Accepts either a URL (str) or raw bytes (bytes/BytesIO)."""
        try:
            # Prepare image data
            if isinstance(image, (bytes, bytearray)):
                image_data = BytesIO(image)
            elif hasattr(image, 'read'):
                # file-like
                image.seek(0)
                image_data = image
            elif isinstance(image, str):
                # treat as URL
                response = requests.get(image, stream=True)
                if response.status_code != 200:
                    logging.error(f"Failed to download OpenAI image. Status Code: {response.status_code}")
                    return None
                image_data = BytesIO(response.content)
            else:
                logging.error('upload_openai_image_to_wordpress: unsupported image type')
                return None

            filename = "openai_image.jpg"
            files = {'file': (filename, image_data.read(), 'image/jpeg')}

            headers = {
                "Authorization": "Basic " + b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode(),
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
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
            logging.error(f"Error uploading image to WordPress via GraphQL: {e}", exc_info=True)
            return None

    ########################################################################
    # Prompt persistence helpers and endpoints
    ########################################################################
    PROMPTS_FILE = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'data', 'prompts.json')

    def _ensure_prompts_file():
        dirpath = os.path.dirname(PROMPTS_FILE)
        try:
            os.makedirs(dirpath, exist_ok=True)
        except Exception:
            logging.exception('Failed to create data directory for prompts')
        if not os.path.exists(PROMPTS_FILE):
            try:
                with open(PROMPTS_FILE, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
            except Exception:
                logging.exception('Failed to create prompts file')

    def load_prompts():
        _ensure_prompts_file()
        try:
            with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f) or {}
        except Exception:
            logging.exception('Failed to load prompts file')
            return {}

    def save_prompt(index, prompt_text):
        _ensure_prompts_file()
        try:
            prompts = load_prompts()
            prompts[str(index)] = prompt_text
            with open(PROMPTS_FILE, 'w', encoding='utf-8') as f:
                json.dump(prompts, f, indent=2)
            return True
        except Exception:
            logging.exception('Failed to save prompt')
            return False

    @app.route('/prompts', methods=['GET'])
    def get_prompts():
        prompts = load_prompts()
        return jsonify({'success': True, 'prompts': prompts})

    @app.route('/prompts', methods=['POST'])
    def post_prompt():
        data = request.json or {}
        index = data.get('index')
        prompt_text = data.get('prompt')
        if index is None or prompt_text is None:
            return jsonify({'success': False, 'error': 'index and prompt required'}), 400
        ok = save_prompt(index, prompt_text)
        if ok:
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'failed to save prompt'}), 500

    @app.route('/session_info', methods=['GET'])
    def session_info():
        info = {'has_openai_key': False}
        if 'OPENAI_API_KEY' in session:
            k = session.get('OPENAI_API_KEY') or ''
            if isinstance(k, str) and len(k) > 8:
                info['openai_key_redacted'] = k[:4] + '...' + k[-4:]
            else:
                info['openai_key_redacted'] = 'REDACTED'
            info['has_openai_key'] = True
        return jsonify(info)

    @app.route('/last_debug_generate_image', methods=['GET'])
    def last_debug_generate_image():
        """Returns the contents of debug_generate_image_error.json (redacted) if present."""
        try:
            file_path = os.path.join(os.getcwd(), 'debug_generate_image_error.json')
            if not os.path.exists(file_path):
                return jsonify({'found': False, 'message': 'No debug file found.'}), 404
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify({'found': True, 'debug': data})
        except Exception as e:
            logging.exception('Error reading debug_generate_image_error.json')
            return jsonify({'found': False, 'error': str(e)}), 500

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
            oclient = get_openai_client()
            if not oclient:
                return jsonify({"success": False, "error": "OpenAI API key not available. Please validate your API key first."}), 401
            try:
                ai_response = oclient.chat.completions.create(
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
                logging.error(f"OpenAI error validating title: {e}", exc_info=True)
                return jsonify({"success": False, "error": str(e)}), 500

        except Exception as e:
            logging.error(f"Error validating title: {e}")
            return jsonify({"success": False, "error": str(e)}), 500


        
    ########################################################################
    # Secret Key and Return
    ########################################################################
    app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')
    return app
