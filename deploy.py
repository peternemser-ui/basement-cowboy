#!/usr/bin/env python3
"""
Deployment script for Basement Cowboy News Aggregation System
"""

import os
import sys
import shutil
import zipfile
from datetime import datetime

def create_deployment_package():
    """Create a deployment package"""
    print("📦 Creating deployment package...")
    
    # Create deployment directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    deploy_dir = f"deployment_basement_cowboy_{timestamp}"
    
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    
    os.makedirs(deploy_dir)
    
    # Files and directories to include
    include_items = [
        'app/',
        'scraper/',
        'config/',
        'static/',
        'requirements.txt',
        'run.py',
        'setup.py',
        'README.md',
        '.env.template',
        '.gitignore'
    ]
    
    # Copy files
    for item in include_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.copytree(item, os.path.join(deploy_dir, item))
            else:
                shutil.copy2(item, deploy_dir)
            print(f"✅ Copied: {item}")
        else:
            print(f"⚠️  Not found: {item}")
    
    # Create necessary directories
    directories = [
        'output/news_articles',
        'output/logs',
        'output/wordpress-output',
        'data',
        'tests'
    ]
    
    for directory in directories:
        dir_path = os.path.join(deploy_dir, directory)
        os.makedirs(dir_path, exist_ok=True)
        # Create .gitkeep files
        with open(os.path.join(dir_path, '.gitkeep'), 'w') as f:
            f.write('')
        print(f"✅ Created directory: {directory}")
    
    # Create deployment instructions
    instructions = """
# Basement Cowboy Deployment Instructions

## Quick Start
1. Run setup: python setup.py
2. Configure .env file with your OpenAI API key
3. Configure config/wordpress_config.json with your WordPress details
4. Start application: python run.py
5. Access at: http://127.0.0.1:5000

## Requirements
- Python 3.8+
- OpenAI API Key
- WordPress site with Application Passwords enabled

## Optional GraphQL Setup
1. Install WPGraphQL plugin on WordPress
2. Set "api_version": "graphql" in wordpress_config.json
3. Install GraphQL deps: pip install gql[all] graphql-core

See README.md for detailed instructions.
"""
    
    with open(os.path.join(deploy_dir, 'DEPLOYMENT.md'), 'w') as f:
        f.write(instructions)
    
    # Create production config template
    prod_env = """# Production Environment Configuration
OPENAI_API_KEY=your-openai-api-key-here
FLASK_SECRET_KEY=your-random-32-character-secret-key
FLASK_DEBUG=False
"""
    with open(os.path.join(deploy_dir, '.env.production'), 'w') as f:
        f.write(prod_env)
    
    print(f"\n✅ Deployment package created: {deploy_dir}")
    
    # Create ZIP file
    zip_name = f"{deploy_dir}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, deploy_dir)
                zipf.write(file_path, arc_name)
    
    print(f"✅ ZIP package created: {zip_name}")
    
    # Calculate package size
    size_mb = os.path.getsize(zip_name) / (1024 * 1024)
    print(f"📏 Package size: {size_mb:.2f} MB")
    
    return deploy_dir, zip_name

def verify_package(deploy_dir):
    """Verify the deployment package"""
    print(f"\n🔍 Verifying deployment package: {deploy_dir}")
    
    # Check required files
    required_files = [
        'run.py',
        'setup.py', 
        'requirements.txt',
        'README.md',
        'DEPLOYMENT.md',
        '.env.template',
        '.env.production',
        'app/routes.py',
        'scraper/main.py',
        'config/wordpress_config.json.template'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(deploy_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {missing_files}")
        return False
    
    print("\n✅ Package verification passed!")
    return True

def main():
    """Main deployment function"""
    print("🚀 Basement Cowboy Deployment Packager")
    print("=" * 50)
    
    if not os.path.exists('run.py'):
        print("❌ Must run from the project root directory")
        sys.exit(1)
    
    deploy_dir, zip_name = create_deployment_package()
    
    if verify_package(deploy_dir):
        print(f"\n🎉 Deployment package ready!")
        print(f"📁 Directory: {deploy_dir}")
        print(f"📦 ZIP file: {zip_name}")
        print("\n📋 Next steps:")
        print("1. Extract the ZIP file on your target server")
        print("2. Run: python setup.py")
        print("3. Configure .env and wordpress_config.json")
        print("4. Run: python run.py")
    else:
        print("\n❌ Package verification failed")

if __name__ == "__main__":
    main()