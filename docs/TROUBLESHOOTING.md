# Troubleshooting Guide

This guide helps you resolve common issues with Basement Cowboy.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Scraping Issues](#scraping-issues)
- [OpenAI Issues](#openai-issues)
- [WordPress Issues](#wordpress-issues)
- [Performance Issues](#performance-issues)

## Installation Issues

### ModuleNotFoundError

**Problem:** `ModuleNotFoundError: No module named 'xxx'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Playwright Installation Fails

**Problem:** Playwright browser installation fails

**Solution:**
```bash
# Install Playwright browsers manually
playwright install chromium

# On Linux, install dependencies
playwright install-deps
```

### Permission Denied

**Problem:** Permission denied when running scripts

**Solution:**
```bash
# Linux/macOS
chmod +x scripts/*.py

# Windows: Run as administrator or check antivirus
```

## Scraping Issues

### No Articles Found

**Problem:** Scraper runs but finds no articles

**Causes & Solutions:**

1. **Source website changed structure**
   - Check if website is accessible
   - Website may have updated HTML structure
   - Try with a different source

2. **Rate limiting**
   - Increase delay between requests:
     ```env
     SCRAPER_DELAY=2.0
     ```

3. **Blocked by website**
   - Enable Playwright for JavaScript rendering
   - Check if site blocks automated access

### Connection Errors

**Problem:** `ConnectionError` or `Timeout` errors

**Solution:**
```python
# Increase timeout in config
SCRAPER_TIMEOUT=60

# Add retry logic is already built-in
# Check your internet connection
```

### SSL Certificate Errors

**Problem:** SSL certificate verification fails

**Solution:**
```bash
# Update certificates
pip install --upgrade certifi

# Or in config (not recommended for production)
# Disable SSL verification as last resort
```

### Cloudflare Blocking

**Problem:** 403 Forbidden or Cloudflare challenge page

**Solution:**
1. Enable Playwright mode for the source
2. Add longer delays between requests
3. Consider using proxies (advanced)

## OpenAI Issues

### Invalid API Key

**Problem:** `AuthenticationError: Invalid API key`

**Solution:**
1. Verify key starts with `sk-`
2. Check key is not expired
3. Regenerate key on OpenAI dashboard
4. Ensure no extra whitespace

### Rate Limit Exceeded

**Problem:** `RateLimitError: Rate limit reached`

**Solution:**
```env
# Reduce concurrent requests
OPENAI_MAX_CONCURRENT=1

# Add delay between requests
# Wait and retry (built-in)
```

### Cost Limit Reached

**Problem:** Daily/monthly cost limit exceeded

**Solution:**
```env
# Increase limits (carefully!)
OPENAI_MAX_DAILY_COST=100.00

# Or wait until next day/month
# Check OpenAI usage dashboard
```

### Timeout on Generation

**Problem:** Image/summary generation times out

**Solution:**
```env
# Increase timeout
OPENAI_TIMEOUT=120

# Try again - may be temporary
# Use smaller model (gpt-3.5-turbo)
```

## WordPress Issues

### Connection Failed

**Problem:** Cannot connect to WordPress

**Checklist:**
1. ✅ URL includes `https://`
2. ✅ REST API is enabled
3. ✅ Application Password is correct
4. ✅ User has publishing permissions

**Test connection:**
```bash
curl -u "username:app_password" https://yoursite.com/wp-json/wp/v2/posts
```

### Authentication Error

**Problem:** 401 Unauthorized

**Solution:**
1. **Enable Application Passwords**
   - WordPress 5.6+ required
   - Go to Users → Profile → Application Passwords
   - Generate new password

2. **Check credentials format**
   - Username: Your WordPress username
   - Password: Application password (with spaces)

### Post Creation Fails

**Problem:** Post created but missing content

**Solution:**
1. Check content HTML is valid
2. Verify user has `publish_posts` capability
3. Check for plugin conflicts

### Media Upload Fails

**Problem:** Featured image doesn't upload

**Causes:**
1. Image URL inaccessible
2. File size too large
3. Unsupported format

**Solution:**
```python
# Check WordPress media settings
# Increase upload limit in wp-config.php:
# define('WP_MEMORY_LIMIT', '256M');
```

## Performance Issues

### Slow Scraping

**Problem:** Scraping takes too long

**Solutions:**
1. **Reduce sources**
   ```env
   SCRAPER_MAX_ARTICLES=50
   ```

2. **Disable Playwright for simple sites**
   - Only use for JavaScript-heavy sites

3. **Parallel processing**
   - Already implemented, but limited by rate limits

### High Memory Usage

**Problem:** Application uses too much memory

**Solutions:**
1. **Clear cache regularly**
   ```bash
   python scripts/cleanup_old_articles.py --cache --days 1
   ```

2. **Reduce cache size**
   ```env
   MEMORY_CACHE_SIZE=500
   ```

3. **Process in batches**

### Slow API Responses

**Problem:** Web interface is slow

**Solutions:**
1. **Enable caching**
2. **Reduce articles per page**
3. **Use pagination**
4. **Check database/storage**

## Logging and Debugging

### Enable Debug Logging

```env
FLASK_DEBUG=true
LOG_LEVEL=DEBUG
```

### Check Logs

```bash
# View recent logs
tail -f output/logs/app.log

# Search for errors
grep -i error output/logs/app.log
```

### Debug Mode

Run with debug mode:
```bash
FLASK_DEBUG=true python run.py
```

## Getting More Help

### Information to Include in Bug Reports

1. **Environment**
   - OS and version
   - Python version
   - Package versions (`pip freeze`)

2. **Error Details**
   - Full error message
   - Stack trace
   - Steps to reproduce

3. **Configuration**
   - Relevant settings (without secrets!)
   - News sources being used

### Resources

- [GitHub Issues](https://github.com/yourusername/basement-cowboy/issues)
- [Documentation](./README.md)
- [API Reference](./API.md)

---

Still stuck? Open an issue on GitHub with detailed information about your problem.
