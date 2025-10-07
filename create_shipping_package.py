#!/usr/bin/env python3
"""
Basement Cowboy - Shipping Package Creator
Creates a complete distribution package for Basement Cowboy
"""

import os
import shutil
import zipfile
import json
from datetime import datetime

def create_shipping_package():
    """Create a complete shipping package for Basement Cowboy"""
    
    # Create shipping directory
    shipping_dir = "basement-cowboy-shipping"
    if os.path.exists(shipping_dir):
        shutil.rmtree(shipping_dir)
    os.makedirs(shipping_dir)
    
    # Files and directories to include
    include_files = [
        # Core application files
        "run.py",
        "requirements.txt",
        "README.md",
        "QUICK_START.md",
        "PRODUCTION_GUIDE.md",
        "TECHNICAL_BRIEF.md",
        "SHIPPING_CHECKLIST.md",
        "WP_ENGINE_QUICK_SETUP.md",
        
        # Setup scripts
        "setup-windows.bat",
        "setup-unix.sh",
        "system_check.py",
        
        # WordPress template
        "wordpress-template-with-images.php",
        
        # Application directories
        "app/",
        "config/",
        "data/",
        "scraper/",
        "tests/",
    ]
    
    # Directories to create but leave empty
    create_empty_dirs = [
        "output/news_articles",
        "output/logs",
        "output/wordpress-output",
    ]
    
    print("🚀 Creating Basement Cowboy shipping package...")
    
    # Copy files and directories
    for item in include_files:
        src = item
        dst = os.path.join(shipping_dir, item)
        
        if os.path.isfile(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f"   📄 {item}")
        elif os.path.isdir(src):
            shutil.copytree(src, dst)
            print(f"   📁 {item}")
        else:
            print(f"   ⚠️  Missing: {item}")
    
    # Create empty output directories
    for dir_path in create_empty_dirs:
        full_path = os.path.join(shipping_dir, dir_path)
        os.makedirs(full_path, exist_ok=True)
        # Create .gitkeep file to preserve directory
        with open(os.path.join(full_path, ".gitkeep"), "w") as f:
            f.write("# This file keeps the directory in version control\n")
        print(f"   📁 {dir_path} (created)")
    
    # Create .env template
    env_template = """# Basement Cowboy Environment Configuration
# Copy this file to .env and fill in your values

# OpenAI API Key (required for AI features)
OPENAI_API_KEY=your_openai_api_key_here

# Flask Secret Key (generate a random 32-character string)
FLASK_SECRET_KEY=your_random_32_character_secret_key_here

# Optional: Set Flask environment
FLASK_ENV=development
"""
    
    with open(os.path.join(shipping_dir, ".env.template"), "w") as f:
        f.write(env_template)
    print("   📄 .env.template (created)")
    
    # Create shipping info file
    shipping_info = {
        "name": "Basement Cowboy",
        "version": "1.0.0",
        "description": "AI-powered news aggregation platform",
        "created": datetime.now().isoformat(),
        "python_version_required": "3.8+",
        "setup_instructions": [
            "1. Run setup script for your platform:",
            "   Windows: setup-windows.bat", 
            "   Mac/Linux: ./setup-unix.sh",
            "2. Configure .env file with API keys",
            "3. Run: python run.py",
            "4. Open browser to http://localhost:5000"
        ],
        "included_files": include_files + create_empty_dirs + [".env.template", "SHIPPING_INFO.json"]
    }
    
    with open(os.path.join(shipping_dir, "SHIPPING_INFO.json"), "w") as f:
        json.dump(shipping_info, f, indent=2)
    print("   📄 SHIPPING_INFO.json (created)")
    
    # Create ZIP archive
    zip_filename = f"basement-cowboy-v1.0.0-{datetime.now().strftime('%Y%m%d')}.zip"
    
    print(f"\n📦 Creating ZIP archive: {zip_filename}")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(shipping_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, shipping_dir)
                zipf.write(file_path, arc_path)
                
    # Get ZIP file size
    zip_size = os.path.getsize(zip_filename) / (1024 * 1024)  # Convert to MB
    
    print(f"\n✅ Shipping package created successfully!")
    print(f"   📦 Archive: {zip_filename}")
    print(f"   💾 Size: {zip_size:.1f} MB")
    print(f"   📁 Contents: {shipping_dir}/")
    
    # Quick validation
    print(f"\n🔍 Package validation:")
    with zipfile.ZipFile(zip_filename, 'r') as zipf:
        file_count = len(zipf.namelist())
        print(f"   📄 Files in archive: {file_count}")
        
        # Check for key files
        key_files = ["run.py", "requirements.txt", "QUICK_START.md", "setup-windows.bat"]
        for key_file in key_files:
            if key_file in zipf.namelist():
                print(f"   ✅ {key_file}")
            else:
                print(f"   ❌ {key_file} - MISSING")
    
    print(f"\n🚀 Ready to ship! Send '{zip_filename}' to users.")
    print(f"📋 Users should follow instructions in QUICK_START.md")
    
    return zip_filename

if __name__ == "__main__":
    try:
        zip_file = create_shipping_package()
        print(f"\n🎉 SUCCESS: {zip_file} is ready for distribution!")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()