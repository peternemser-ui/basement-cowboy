# 🚀 WP Engine Setup for Basement Cowboy

## Quick Setup (2 minutes)

### Option 1: Interactive Setup (Recommended)
Run the setup script and follow the prompts:
```bash
python setup_wp_engine.py
```

### Option 2: Manual Configuration
1. **Copy your current working config as a template**:
   ```bash
   cp config/wordpress_config.json config/wordpress_config_wpengine.json
   ```

2. **Edit the config file** with your WP Engine details:
   ```json
   {
     "wordpress_url": "https://yoursite.wpengine.com",
     "username": "your-wp-username", 
     "application_password": "xxxx xxxx xxxx xxxx",
     "environment": "wpengine_production"
   }
   ```

3. **Use the new config**:
   ```bash
   cp config/wordpress_config_wpengine.json config/wordpress_config.json
   ```

## WP Engine Site URLs

### Production Sites:
- `https://yoursite.wpengine.com` (temporary URL)
- `https://yoursite.com` (custom domain)

### Staging Sites:
- `https://yoursite.staging.wpengine.com`

### Development Sites:
- `https://yoursite.dev.wpengine.com`

## WordPress Application Password Setup

1. **Log into WordPress Admin** on your WP Engine site
2. **Go to Users → Your Profile**
3. **Scroll to "Application Passwords"** section
4. **Enter Description**: "Basement Cowboy API"
5. **Click "Add New Application Password"**
6. **Copy the generated password** (format: `xxxx xxxx xxxx xxxx`)
7. **Paste into your config file**

## Testing Your Setup

### Test WordPress Connection:
```bash
python wordpress_config_manager.py
```

### Test Everything:
```bash
python run.py
# Visit http://127.0.0.1:5000
# Generate articles and publish to WP Engine
```

## Multiple Environment Support

Create different config files for different sites:

```bash
# Production WP Engine site
config/wordpress_config_wpengine_prod.json

# Staging WP Engine site  
config/wordpress_config_wpengine_staging.json

# Development/Local WordPress
config/wordpress_config_local.json
```

Switch between them by copying to `wordpress_config.json`:
```bash
cp config/wordpress_config_wpengine_prod.json config/wordpress_config.json
```

## Environment Variables (Optional)

Create `.env` file for even more flexibility:
```env
WP_ENVIRONMENT=wpengine_production
WP_URL=https://yoursite.wpengine.com
WP_USERNAME=your-username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

## Troubleshooting

### Connection Issues:
- ✅ Verify WordPress REST API: `https://yoursite.com/wp-json/wp/v2/posts`
- ✅ Check application password format (has spaces)
- ✅ Ensure user has proper permissions

### WP Engine Specific:
- ✅ WP Engine supports REST API by default
- ✅ Use full HTTPS URLs
- ✅ Application passwords work normally

### Quick Test:
```bash
curl -u "username:xxxx xxxx xxxx xxxx" https://yoursite.wpengine.com/wp-json/wp/v2/posts?per_page=1
```

## That's It! 🎉

Your Basement Cowboy is now portable and works with:
- ✅ WP Engine (all environments)
- ✅ Any WordPress hosting provider
- ✅ Local WordPress development
- ✅ WordPress.com Business plans
- ✅ Self-hosted WordPress sites

Just change the config file and you're ready to go!