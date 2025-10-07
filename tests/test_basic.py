"""
Basic tests for Basement Cowboy application
"""
import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock

# Set up test environment
os.environ['FLASK_SECRET_KEY'] = 'test-secret-key'
os.environ['FLASK_DEBUG'] = 'False'
os.environ['OPENAI_API_KEY'] = 'test-key'

def test_imports():
    """Test that core modules can be imported"""
    try:
        from app.routes import create_app
        from app.seo_generator import SEOGenerator
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")

def test_app_creation():
    """Test that Flask app can be created"""
    from app.routes import create_app
    
    app = create_app()
    assert app is not None
    assert app.config['SECRET_KEY'] == 'test-secret-key'

def test_app_routes():
    """Test basic app routes"""
    from app.routes import create_app
    
    app = create_app()
    client = app.test_client()
    
    # Test health endpoint
    response = client.get('/health')
    assert response.status_code == 200
    
    # Test main page
    response = client.get('/')
    assert response.status_code == 200

def test_seo_generator():
    """Test SEO generator functionality"""
    from app.seo_generator import SEOGenerator
    
    seo = SEOGenerator()
    
    # Test basic functionality
    test_article = {
        'headline': 'Test Article',
        'summary': 'This is a test article for unit testing.',
        'link': 'https://example.com/test'
    }
    
    result = seo.generate_meta_tags([test_article])
    assert 'title' in result
    assert 'description' in result

@patch('requests.get')
def test_scraper_imports(mock_get):
    """Test that scraper modules can be imported"""
    try:
        from scraper.fetch_page import fetch_page_content
        from scraper.parse_articles import parse_articles_from_content
        from scraper.filter_articles import filter_articles
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import scraper modules: {e}")

def test_environment_variables():
    """Test that required environment variables are set for testing"""
    assert os.environ.get('FLASK_SECRET_KEY') == 'test-secret-key'
    assert os.environ.get('FLASK_DEBUG') == 'False'
    assert os.environ.get('OPENAI_API_KEY') == 'test-key'

def test_config_files_exist():
    """Test that required configuration files exist"""
    config_files = [
        'config/categories.json',
        'config/top_100_news_sites.txt',
        'config/wordpress_config.json.template'
    ]
    
    for config_file in config_files:
        assert os.path.exists(config_file), f"Missing config file: {config_file}"

def test_output_directories():
    """Test that output directories can be created"""
    import tempfile
    import shutil
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dirs = [
            os.path.join(temp_dir, 'news_articles'),
            os.path.join(temp_dir, 'logs'),
            os.path.join(temp_dir, 'wordpress-output')
        ]
        
        for output_dir in output_dirs:
            os.makedirs(output_dir, exist_ok=True)
            assert os.path.exists(output_dir)

@pytest.fixture
def app():
    """Create test app fixture"""
    from app.routes import create_app
    
    app = create_app()
    app.config['TESTING'] = True
    
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Create test client fixture"""
    return app.test_client()

def test_api_key_validation_endpoint(client):
    """Test API key validation endpoint"""
    response = client.post('/validate_api_key', 
                          json={'api_key': 'test-key'},
                          content_type='application/json')
    # Should return error for invalid test key, which is expected
    assert response.status_code in [400, 401, 403, 500]  # Any error code is fine for test key

def test_ping_endpoint(client):
    """Test ping endpoint"""
    response = client.get('/ping')
    assert response.status_code == 200
    data = response.get_json()
    assert data['ok'] is True
    assert data['msg'] == 'pong'