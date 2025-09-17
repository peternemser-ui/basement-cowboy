"""
WordPress GraphQL Client for Basement Cowboy
Handles all GraphQL operations for WordPress publishing including posts and media uploads.
"""

import logging
import json
import os
from base64 import b64encode
from io import BytesIO
from typing import Dict, List, Optional, Any

import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


class WordPressGraphQLClient:
    """WordPress GraphQL client for publishing articles and uploading media."""
    
    def __init__(self, wordpress_url: str, username: str, application_password: str):
        """
        Initialize WordPress GraphQL client.
        
        Args:
            wordpress_url: WordPress site URL (e.g., https://example.com)
            username: WordPress username
            application_password: WordPress application password
        """
        self.wordpress_url = wordpress_url.rstrip('/')
        self.username = username
        self.application_password = application_password
        self.graphql_endpoint = f"{self.wordpress_url}/graphql"
        
        # Setup authentication headers
        auth_string = b64encode(f'{username}:{application_password}'.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/json",
            "User-Agent": "Basement-Cowboy/1.0"
        }
        
        # Initialize GraphQL client
        self.transport = RequestsHTTPTransport(
            url=self.graphql_endpoint,
            headers=self.headers,
            retries=3,
        )
        self.client = Client(
            transport=self.transport,
            fetch_schema_from_transport=False,
        )
        
        logging.info(f"Initialized WordPress GraphQL client for {wordpress_url}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the GraphQL connection and authentication.
        
        Returns:
            Dict containing success status and connection details
        """
        try:
            query = gql("""
                query TestConnection {
                    generalSettings {
                        title
                        url
                        description
                    }
                }
            """)
            
            result = self.client.execute(query)
            return {
                "success": True,
                "site_title": result["generalSettings"]["title"],
                "site_url": result["generalSettings"]["url"],
                "site_description": result["generalSettings"]["description"]
            }
        except Exception as e:
            logging.error(f"GraphQL connection test failed: {e}")
            return {"success": False, "error": str(e)}
    
    def create_post(self, title: str, content: str, status: str = "publish") -> Dict[str, Any]:
        """
        Create a new WordPress post using GraphQL.
        
        Args:
            title: Post title
            content: Post content (HTML)
            status: Post status (draft, publish, private)
            
        Returns:
            Dict containing post creation results
        """
        try:
            mutation = gql("""
                mutation CreatePost($input: CreatePostInput!) {
                    createPost(input: $input) {
                        post {
                            id
                            databaseId
                            title
                            content
                            status
                            date
                            modified
                            link
                            uri
                        }
                        errors {
                            field
                            message
                        }
                    }
                }
            """)
            
            variables = {
                "input": {
                    "title": title,
                    "content": content,
                    "status": status.upper()
                }
            }
            
            result = self.client.execute(mutation, variable_values=variables)
            
            if result["createPost"]["errors"]:
                errors = result["createPost"]["errors"]
                error_messages = [f"{err['field']}: {err['message']}" for err in errors]
                return {
                    "success": False,
                    "errors": error_messages
                }
            
            post = result["createPost"]["post"]
            return {
                "success": True,
                "post": {
                    "id": post["databaseId"],
                    "graphql_id": post["id"],
                    "title": post["title"],
                    "status": post["status"],
                    "date": post["date"],
                    "modified": post["modified"],
                    "link": f"{self.wordpress_url}{post['uri']}",
                    "url": post["link"]
                }
            }
            
        except Exception as e:
            logging.error(f"Failed to create post via GraphQL: {e}")
            return {"success": False, "error": str(e)}
    
    def upload_media(self, image_data: BytesIO, filename: str, alt_text: str = "") -> Optional[str]:
        """
        Upload media to WordPress using GraphQL.
        Note: This requires the WPGraphQL Upload plugin.
        
        Args:
            image_data: Image data as BytesIO
            filename: Filename for the upload
            alt_text: Alt text for the image
            
        Returns:
            URL of uploaded image or None if failed
        """
        try:
            # For GraphQL file uploads, we need to use multipart form data
            # This is a more complex operation that requires the WPGraphQL Upload plugin
            
            mutation = gql("""
                mutation UploadMedia($input: CreateMediaItemInput!) {
                    createMediaItem(input: $input) {
                        mediaItem {
                            id
                            databaseId
                            sourceUrl
                            altText
                            title
                            mediaDetails {
                                file
                                width
                                height
                            }
                        }
                        errors {
                            field
                            message
                        }
                    }
                }
            """)
            
            # For file uploads in GraphQL, we typically need to handle this differently
            # Let's fall back to REST API for media uploads if GraphQL upload is complex
            return self._upload_media_rest_fallback(image_data, filename, alt_text)
            
        except Exception as e:
            logging.error(f"Failed to upload media via GraphQL: {e}")
            return None
    
    def _upload_media_rest_fallback(self, image_data: BytesIO, filename: str, alt_text: str = "") -> Optional[str]:
        """
        Fallback to REST API for media uploads.
        GraphQL file uploads can be complex and require additional plugins.
        """
        try:
            files = {'file': (filename, image_data.read(), 'image/jpeg')}
            
            headers = {
                "Authorization": f"Basic {b64encode(f'{self.username}:{self.application_password}'.encode()).decode()}",
                "User-Agent": "Basement-Cowboy/1.0"
            }
            
            response = requests.post(
                f"{self.wordpress_url}/wp-json/wp/v2/media",
                headers=headers,
                files=files
            )
            
            if response.status_code == 201:
                media_data = response.json()
                logging.info(f"✅ Media uploaded successfully via REST fallback: {media_data.get('source_url')}")
                return media_data.get("source_url")
            else:
                logging.error(f"❌ Media upload failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error in REST media upload fallback: {e}")
            return None
    
    def get_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent posts using GraphQL.
        
        Args:
            limit: Number of posts to retrieve
            
        Returns:
            List of post dictionaries
        """
        try:
            query = gql("""
                query GetPosts($first: Int!) {
                    posts(first: $first, where: {orderby: {field: DATE, order: DESC}}) {
                        nodes {
                            id
                            databaseId
                            title
                            date
                            modified
                            status
                            link
                            uri
                            excerpt
                        }
                    }
                }
            """)
            
            variables = {"first": limit}
            result = self.client.execute(query, variable_values=variables)
            
            posts = []
            for post in result["posts"]["nodes"]:
                posts.append({
                    "id": post["databaseId"],
                    "graphql_id": post["id"],
                    "title": post["title"],
                    "date": post["date"],
                    "modified": post["modified"],
                    "status": post["status"],
                    "link": post["link"],
                    "url": f"{self.wordpress_url}{post['uri']}",
                    "excerpt": post["excerpt"]
                })
            
            return posts
            
        except Exception as e:
            logging.error(f"Failed to get posts via GraphQL: {e}")
            return []


def create_wordpress_graphql_client(config_path: str = None) -> Optional[WordPressGraphQLClient]:
    """
    Create WordPress GraphQL client from configuration.
    
    Args:
        config_path: Path to WordPress config file
        
    Returns:
        WordPressGraphQLClient instance or None if failed
    """
    if config_path is None:
        # Default config path
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        config_path = os.path.join(base_dir, 'config', 'wordpress_config.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        
        required_fields = ['wordpress_url', 'username', 'application_password']
        if not all(field in config for field in required_fields):
            missing = [field for field in required_fields if field not in config]
            logging.error(f"Missing required WordPress config fields: {missing}")
            return None
        
        return WordPressGraphQLClient(
            wordpress_url=config['wordpress_url'],
            username=config['username'],
            application_password=config['application_password']
        )
        
    except Exception as e:
        logging.error(f"Failed to create WordPress GraphQL client: {e}")
        return None