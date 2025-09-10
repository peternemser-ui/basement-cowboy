import os
import json
import requests
import logging
from base64 import b64encode

def test_wordpress_upload():
    try:
        # Explicitly set WordPress credentials (update if needed):
        WP_SITE = "https://basementcowboy.com"
        WP_USER = "peter@aupt-industries.com"
        WP_APP_PASSWORD = "g7v0 1gqQ XAmI KV8S YjKi D28w"

        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # File named 'home-image.jpg' in the same directory
        test_file_path = os.path.join(script_dir, 'home-image.jpg')
        if not os.path.exists(test_file_path):
            print("Test file not found:", test_file_path)
            return

        # Prepare headers for WordPress media upload
        auth_header = b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode()).decode()
        wp_headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Disposition": 'attachment; filename="home-image.jpg"',
        }

        # Perform the POST request to upload media
        with open(test_file_path, "rb") as f:
            wp_response = requests.post(
                f"{WP_SITE}/wp-json/wp/v2/media",
                headers=wp_headers,
                files={"file": ("home-image.jpg", f, "image/jpeg")},
            )

        if wp_response.status_code == 201:
            wp_image_url = wp_response.json().get("source_url")
            print("Upload successful:", wp_image_url)
        else:
            print(f"WordPress upload failed: {wp_response.status_code} - {wp_response.text}")

    except Exception as e:
        logging.error(f"Error during WordPress upload test: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    test_wordpress_upload()
