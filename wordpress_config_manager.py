#!/usr/bin/env python3
"""
Enhanced WordPress configuration loader for maximum portability
Supports multiple environments and hosting providers including WP Engine
"""

import json
import os
from pathlib import Path

class WordPressConfig:
    def __init__(self, environment=None):
        self.base_dir = Path(__file__).parent
        self.config_dir = self.base_dir / 'config'
        self.environment = environment or os.getenv('WP_ENVIRONMENT', 'production')
        self.config = self.load_config()
    
    def load_config(self):
        """Load WordPress configuration with environment-specific overrides"""
        config_files = [
            f'wordpress_config_{self.environment}.json',  # Environment-specific
            'wordpress_config.json',  # Default
        ]
        
        config = {}
        
        for config_file in config_files:
            config_path = self.config_dir / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        file_config = json.load(f)
                        config.update(file_config)
                        print(f"✅ Loaded config from: {config_file}")
                        break
                except Exception as e:
                    print(f"❌ Error loading {config_file}: {e}")
        
        # Override with environment variables if present
        env_overrides = {
            'wordpress_url': os.getenv('WP_URL'),
            'username': os.getenv('WP_USERNAME'),
            'application_password': os.getenv('WP_APP_PASSWORD'),
        }
        
        for key, value in env_overrides.items():
            if value:
                config[key] = value
                print(f"✅ Override from environment: {key}")
        
        # Validate required fields
        required_fields = ['wordpress_url', 'username', 'application_password']
        missing_fields = [field for field in required_fields if not config.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required WordPress config fields: {missing_fields}")
        
        # Clean up URL format
        config['wordpress_url'] = config['wordpress_url'].rstrip('/')
        
        return config
    
    def get_wp_site(self):
        return self.config['wordpress_url']
    
    def get_wp_user(self):
        return self.config['username']
    
    def get_wp_password(self):
        return self.config['application_password']
    
    def get_environment(self):
        return self.config.get('environment', self.environment)
    
    def is_wp_engine(self):
        """Detect if this is a WP Engine site"""
        url = self.get_wp_site().lower()
        return 'wpengine.com' in url or 'staging.wpengine.com' in url
    
    def is_local(self):
        """Detect if this is a local development site"""
        url = self.get_wp_site().lower()
        return 'localhost' in url or '127.0.0.1' in url
    
    def get_api_headers(self):
        """Get headers optimized for the hosting environment"""
        headers = {
            "User-Agent": "Basement-Cowboy/1.0 (WordPress API Client)",
            "Content-Type": "application/json"
        }
        
        # WP Engine specific optimizations
        if self.is_wp_engine():
            headers["Cache-Control"] = "no-cache"
            headers["X-WP-Engine-API"] = "true"
        
        return headers
    
    def test_connection(self):
        """Test WordPress API connectivity"""
        import requests
        from base64 import b64encode
        
        try:
            auth_header = f"Basic {b64encode(f'{self.get_wp_user()}:{self.get_wp_password()}'.encode()).decode()}"
            headers = self.get_api_headers()
            headers["Authorization"] = auth_header
            
            # Test basic API access
            response = requests.get(f"{self.get_wp_site()}/wp-json/wp/v2/posts?per_page=1", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ WordPress API connection successful!")
                print(f"   Site: {self.get_wp_site()}")
                print(f"   Environment: {self.get_environment()}")
                print(f"   WP Engine: {'Yes' if self.is_wp_engine() else 'No'}")
                return True
            else:
                print(f"❌ WordPress API connection failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ WordPress connection error: {e}")
            return False
    
    def create_sample_configs(self):
        """Create sample configuration files for different environments"""
        configs = {
            'wordpress_config_wpengine_production.json': {
                "wordpress_url": "https://yoursite.wpengine.com",
                "username": "your-wp-username",
                "application_password": "xxxx xxxx xxxx xxxx",
                "environment": "wpengine_production",
                "hosting_provider": "WP Engine"
            },
            'wordpress_config_wpengine_staging.json': {
                "wordpress_url": "https://yoursite.staging.wpengine.com", 
                "username": "your-wp-username",
                "application_password": "xxxx xxxx xxxx xxxx",
                "environment": "wpengine_staging",
                "hosting_provider": "WP Engine"
            },
            'wordpress_config_local.json': {
                "wordpress_url": "http://localhost:8888",
                "username": "admin",
                "application_password": "xxxx xxxx xxxx xxxx",
                "environment": "local",
                "hosting_provider": "Local Development"
            }
        }
        
        for filename, config in configs.items():
            config_path = self.config_dir / filename
            if not config_path.exists():
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                print(f"✅ Created sample config: {filename}")

if __name__ == "__main__":
    print("🔧 WordPress Configuration Manager")
    print("=" * 50)
    
    # Create sample configs
    wp_config = WordPressConfig()
    wp_config.create_sample_configs()
    
    print("\n🧪 Testing current configuration...")
    try:
        wp_config = WordPressConfig()
        wp_config.test_connection()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Setup instructions:")
        print("1. Copy wordpress_config_wpengine_production.json to wordpress_config.json")
        print("2. Update with your WP Engine site details")
        print("3. Run this script again to test")