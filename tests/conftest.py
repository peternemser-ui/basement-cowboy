# Test configuration for pytest
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set test environment variables
os.environ['FLASK_SECRET_KEY'] = 'test-secret-key-for-ci-cd'
os.environ['FLASK_DEBUG'] = 'False'
os.environ['OPENAI_API_KEY'] = 'test-openai-key-for-testing'
os.environ['FLASK_ENV'] = 'testing'

# Disable Playwright for basic tests (to avoid installation issues in CI)
os.environ['PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD'] = '1'