#!/usr/bin/env python3
"""
Basement Cowboy - Environment and System Check
This script validates that all dependencies and configurations are correct.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header(title):
    print("\n" + "="*60)
    print(f"   {title}")
    print("="*60)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def print_info(message):
    print(f"📋 {message}")

def check_python_version():
    """Check if Python version is compatible"""
    print_info("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} - Need Python 3.8+")
        return False

def check_virtual_environment():
    """Check if running in virtual environment"""
    print_info("Checking virtual environment...")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_success("Running in virtual environment ✓")
        return True
    else:
        print_warning("Not running in virtual environment")
        print("  Recommendation: Create and activate virtual environment")
        return False

def check_required_packages():
    """Check if all required packages are installed"""
    print_info("Checking required packages...")
    
    required_packages = [
        'flask', 'requests', 'beautifulsoup4', 'openai', 
        'playwright', 'python-dotenv', 'markupsafe'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} ✓")
        except ImportError:
            print_error(f"{package} - MISSING")
            missing.append(package)
    
    if missing:
        print_error(f"Missing packages: {', '.join(missing)}")
        print("  Run: pip install -r requirements.txt")
        return False
    else:
        print_success("All required packages installed ✓")
        return True

def check_environment_file():
    """Check if .env file exists and has required variables"""
    print_info("Checking environment configuration...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print_error(".env file not found")
        print("  Copy .env.template to .env and configure your API keys")
        return False
    
    # Read .env file
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except Exception as e:
        print_error(f"Failed to read .env file: {e}")
        return False
    
    # Check required variables
    required_vars = ['OPENAI_API_KEY', 'FLASK_SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if var not in env_vars:
            missing_vars.append(var)
            print_error(f"{var} - MISSING")
        elif env_vars[var].startswith('your-') or not env_vars[var].strip():
            print_warning(f"{var} - NOT CONFIGURED")
            missing_vars.append(var)
        else:
            print_success(f"{var} ✓")
    
    if missing_vars:
        print_error("Environment variables need configuration")
        return False
    else:
        print_success("Environment variables configured ✓")
        return True

def check_project_structure():
    """Check if all required project files exist"""
    print_info("Checking project structure...")
    
    required_files = [
        'run.py', 'requirements.txt', 'app/__init__.py', 'app/routes.py',
        'scraper/scrape_news.py', 'config/categories.json'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"{file_path} ✓")
        else:
            print_error(f"{file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print_error("Missing required project files")
        return False
    else:
        print_success("Project structure complete ✓")
        return True

def check_output_directories():
    """Check if output directories exist and are writable"""
    print_info("Checking output directories...")
    
    directories = ['output/news_articles', 'output/logs']
    
    for dir_path in directories:
        dir_obj = Path(dir_path)
        try:
            dir_obj.mkdir(parents=True, exist_ok=True)
            # Test write permission
            test_file = dir_obj / 'test_write.tmp'
            test_file.write_text('test')
            test_file.unlink()
            print_success(f"{dir_path} ✓")
        except Exception as e:
            print_error(f"{dir_path} - CANNOT WRITE: {e}")
            return False
    
    print_success("Output directories ready ✓")
    return True

def check_network_connectivity():
    """Check basic network connectivity"""
    print_info("Checking network connectivity...")
    
    try:
        import requests
        response = requests.get('https://httpbin.org/status/200', timeout=10)
        if response.status_code == 200:
            print_success("Network connectivity ✓")
            return True
        else:
            print_error("Network connectivity - FAILED")
            return False
    except Exception as e:
        print_error(f"Network connectivity - FAILED: {e}")
        return False

def check_playwright_browser():
    """Check if Playwright browser is installed"""
    print_info("Checking Playwright browser...")
    
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        print_success("Playwright browser ✓")
        return True
    except Exception as e:
        print_error(f"Playwright browser - FAILED: {e}")
        print("  Run: playwright install chromium")
        return False

def run_basic_tests():
    """Run basic functionality tests"""
    print_info("Running basic functionality tests...")
    
    try:
        # Test Flask import
        from app.routes import create_app
        app = create_app()
        print_success("Flask app creation ✓")
        
        # Test scraper import
        sys.path.append('scraper')
        import scrape_news
        print_success("Scraper module ✓")
        
        return True
    except Exception as e:
        print_error(f"Basic functionality test failed: {e}")
        return False

def main():
    """Run all system checks"""
    print_header("BASEMENT COWBOY - SYSTEM CHECK")
    
    checks = [
        check_python_version,
        check_virtual_environment,
        check_required_packages,
        check_environment_file,
        check_project_structure,
        check_output_directories,
        check_network_connectivity,
        check_playwright_browser,
        run_basic_tests
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
    
    print_header("SYSTEM CHECK RESULTS")
    
    if passed == total:
        print_success(f"ALL CHECKS PASSED! ({passed}/{total})")
        print_success("🚀 Basement Cowboy is ready to run!")
        print_info("Start with: python run.py")
    else:
        print_error(f"SOME CHECKS FAILED ({passed}/{total})")
        print_warning("Please fix the issues above before running Basement Cowboy")
    
    print("\n" + "="*60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)