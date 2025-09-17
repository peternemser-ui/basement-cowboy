#!/usr/bin/env python3
"""
Setup script for Basement Cowboy News Aggregation System
"""

import os
import sys
import subprocess
import json
import secrets

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def install_playwright():
    """Install Playwright browsers"""
    print("\n🎭 Installing Playwright browsers...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                      check=True, capture_output=True, text=True)
        print("✅ Playwright browsers installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Playwright browsers: {e}")
        return False
    return True

def setup_config_files():
    """Setup configuration files"""
    print("\n⚙️ Setting up configuration files...")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("Creating .env file from template...")
        if os.path.exists('.env.template'):
            with open('.env.template', 'r') as template:
                env_content = template.read()
            
            # Generate a random secret key
            secret_key = secrets.token_hex(16)
            env_content = env_content.replace('your-random-32-character-secret-key', secret_key)
            
            with open('.env', 'w') as env_file:
                env_file.write(env_content)
            print("✅ .env file created (you still need to add your API keys)")
        else:
            print("❌ .env.template not found")
    else:
        print("✅ .env file already exists")
    
    # Check WordPress config
    if not os.path.exists('config/wordpress_config.json'):
        print("⚠️  WordPress config not found - you'll need to create it from the template")
        if os.path.exists('config/wordpress_config.json.template'):
            print("   Template available at: config/wordpress_config.json.template")
    else:
        print("✅ WordPress config file exists")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating necessary directories...")
    directories = [
        'output/news_articles',
        'output/logs', 
        'output/wordpress-output',
        'static',
        'data'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created/verified: {directory}")

def run_basic_tests():
    """Run basic tests to verify setup"""
    print("\n🧪 Running basic tests...")
    
    # Test imports
    try:
        import flask
        import requests
        import openai
        import bs4  # beautifulsoup4 imports as bs4
        from dotenv import load_dotenv
        print("✅ Core imports working")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test Playwright
    try:
        import playwright
        print("✅ Playwright import working")
    except ImportError as e:
        print(f"❌ Playwright import error: {e}")
        return False
    
    return True

def show_next_steps():
    """Show next steps to user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Copy config/wordpress_config.json.template to config/wordpress_config.json")
    print("3. Fill in your WordPress site details in wordpress_config.json")
    print("4. Run: python run.py")
    print("5. Open browser to: http://127.0.0.1:5000")
    print("\n🔧 Optional GraphQL setup:")
    print("1. Install WPGraphQL plugin on your WordPress site")
    print("2. Change api_version to 'graphql' in wordpress_config.json")
    print("3. Install GraphQL dependencies: pip install gql[all] graphql-core")

def main():
    """Main setup function"""
    print("🚀 Basement Cowboy Setup")
    print("=" * 50)
    
    check_python_version()
    
    if not install_dependencies():
        return
    
    if not install_playwright():
        return
    
    setup_config_files()
    create_directories()
    
    if not run_basic_tests():
        print("❌ Basic tests failed - please check the errors above")
        return
    
    show_next_steps()

if __name__ == "__main__":
    main()