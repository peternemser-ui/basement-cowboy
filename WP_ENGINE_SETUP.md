# WordPress Configuration Guide - WP Engine & Portability Setup

## Overview
This guide shows how to configure Basement Cowboy to work with any WordPress site, including WP Engine hosting, making it highly portable across different environments.

## Step 1: WordPress Site Setup

### For WP Engine Sites:
1. **Get your WP Engine site URL**:
   - Production: `https://yoursite.wpengine.com` or your custom domain
   - Staging: `https://yoursite.staging.wpengine.com`

2. **Create Application Password** (Required for REST API):
   - Log into your WordPress admin dashboard
   - Go to Users → Your Profile
   - Scroll down to "Application Passwords"
   - Enter name: "Basement Cowboy API"
   - Click "Add New Application Password"
   - **COPY THE GENERATED PASSWORD** (format: xxxx xxxx xxxx xxxx)

### For Any WordPress Site:
- Ensure WordPress REST API is enabled (default since WP 4.7)
- Verify: Visit `https://yoursite.com/wp-json/wp/v2/posts` (should return JSON)

## Step 2: Configuration Files

### Primary Config: `config/wordpress_config.json`
```json
{
  "wordpress_url": "https://yoursite.wpengine.com",
  "username": "your-wp-username",
  "application_password": "xxxx xxxx xxxx xxxx",
  "environment": "production"
}
```

### Environment-Specific Configs (Optional):
Create multiple config files for different environments:

#### `config/wordpress_config_production.json`
```json
{
  "wordpress_url": "https://yoursite.com",
  "username": "your-username",
  "application_password": "prod-password-here",
  "environment": "production"
}
```

#### `config/wordpress_config_staging.json`
```json
{
  "wordpress_url": "https://yoursite.staging.wpengine.com",
  "username": "your-username", 
  "application_password": "staging-password-here",
  "environment": "staging"
}
```

#### `config/wordpress_config_local.json`
```json
{
  "wordpress_url": "http://localhost:8888",
  "username": "admin",
  "application_password": "local-password-here",
  "environment": "local"
}
```

## Step 3: Environment Variables (Recommended)

### Create `.env` file for sensitive data:
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-key-here
DALL_E_MODEL=dall-e-3
IMAGE_SIZE=1024x1024

# WordPress Configuration
WP_ENVIRONMENT=production
WP_URL=https://yoursite.wpengine.com
WP_USERNAME=your-username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx

# Flask Configuration
FLASK_SECRET_KEY=your-random-secret-key-here
FLASK_ENV=development
```

## Step 4: WP Engine Specific Considerations

### 1. REST API Access
- WP Engine supports WordPress REST API by default
- No additional configuration needed

### 2. Media Uploads
- Media uploads work normally through REST API
- Files are stored in `/wp-content/uploads/`

### 3. Security Settings
- WP Engine has built-in security that may cache API responses
- If you experience caching issues, add cache-busting headers

### 4. SSL/HTTPS
- WP Engine provides SSL by default
- Always use `https://` in your URLs

## Step 5: Testing Your Configuration

### Test WordPress Connection:
```bash
# From your project directory
python test_wp_connection.py
```

### Test Media Upload:
```bash
python test_wordpress_upload.py
```

## Step 6: Deployment Portability

### For Different Environments:
1. **Development**: Use `wordpress_config_local.json`
2. **Staging**: Use `wordpress_config_staging.json` 
3. **Production**: Use `wordpress_config_production.json`

### Quick Environment Switching:
```bash
# Copy the appropriate config
cp config/wordpress_config_production.json config/wordpress_config.json

# Or use environment variables
export WP_ENVIRONMENT=staging
```

## Step 7: Security Best Practices

### 1. Application Passwords
- Create separate passwords for each environment
- Use descriptive names: "Basement Cowboy - Production"
- Regularly rotate passwords

### 2. Environment Variables
- Never commit `.env` files to version control
- Use different API keys for different environments
- Store sensitive data in environment variables, not JSON files

### 3. WP Engine Security
- Enable two-factor authentication
- Use strong WordPress passwords
- Monitor access logs

## Step 8: Advanced Configuration

### Multiple Site Support:
The system can be extended to support multiple WordPress sites simultaneously by modifying the config loading logic.

### Custom Post Types:
If you use custom post types, modify the publishing endpoint in the configuration.

### Custom Categories:
Map your news categories to WordPress categories or tags.

## Troubleshooting

### Common WP Engine Issues:
1. **403 Forbidden**: Check application password format
2. **Timeout**: WP Engine has request timeouts; ensure efficient API calls
3. **Rate Limiting**: Implement delays between API calls if needed

### Testing Connectivity:
```bash
curl -u "username:app-password" https://yoursite.wpengine.com/wp-json/wp/v2/posts
```

## Environment-Specific URLs

### WP Engine URL Patterns:
- **Production**: `https://yoursite.com` or `https://yoursite.wpengine.com`
- **Staging**: `https://yoursite.staging.wpengine.com`
- **Development**: `https://yoursite.dev.wpengine.com`

### Other Common Hosting:
- **Local (MAMP)**: `http://localhost:8888/yoursite`
- **Local (XAMPP)**: `http://localhost/yoursite`
- **WordPress.com**: `https://yoursite.wordpress.com`
- **Bluehost**: `https://yoursite.com`
- **SiteGround**: `https://yoursite.com`

This setup makes your Basement Cowboy project work seamlessly across any WordPress hosting environment!