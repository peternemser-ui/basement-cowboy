# Daily Scrape Checklist
**Basement Cowboy POC Operations**

---

## Pre-Scrape Checklist (5 minutes)

### System Status
- [ ] **Flask app running:** Navigate to http://127.0.0.1:5000 - should load dashboard
- [ ] **Virtual environment active:** Command prompt shows `(venv)` prefix
- [ ] **API keys valid:** Check OpenAI usage dashboard for any billing issues
- [ ] **Disk space:** Ensure 2GB+ free space in output directory

### Configuration Check
- [ ] **WordPress connection:** Test with curl or check last publish success
- [ ] **News sources list:** Verify `config/top_100_news_sites.txt` is accessible
- [ ] **Previous session cleanup:** Check if yesterday's articles need archiving

---

## Scraping Process (30-45 minutes)

### Method 1: Web Interface (Recommended)
1. [ ] Go to http://127.0.0.1:5000
2. [ ] Click **"Regenerate Scraper"** button
3. [ ] Monitor progress in browser
4. [ ] Wait for completion message (~30 minutes)
5. [ ] Verify new file appears in dropdown menu

### Method 2: Command Line
```bash
# Open terminal
cd basement-cowboy
source venv/bin/activate  # or venv\Scripts\activate on Windows
python scraper/scrape_news.py
```

### Expected Results
- [ ] **Article count:** 450-800 articles per session
- [ ] **Processing time:** 15-30 minutes
- [ ] **Success rate:** 85%+ valid articles
- [ ] **New JSON file:** `news_articles_YYYY-MM-DD-X.json` created

---

## Content Review (15-30 minutes)

### Article Selection
1. [ ] Select latest file from dropdown on dashboard
2. [ ] Review article grid - verify images and summaries loaded
3. [ ] Select 50-100 articles for processing (checkbox selection)
4. [ ] Click **"Review Selected Articles"**

### AI Enhancement (Optional)
- [ ] **Bulk summaries:** Click "Generate Summaries for All" if needed
- [ ] **Image generation:** Select articles needing images, click "Create Images"
- [ ] **Quality check:** Spot-check AI-generated content for accuracy

### Editorial Review
- [ ] **Categories:** Verify articles assigned to correct categories
- [ ] **Headlines:** Check for obvious errors or formatting issues
- [ ] **Duplicate detection:** Look for similar articles, deselect duplicates

---

## Publishing Process (10-15 minutes)

### Pre-Publish
- [ ] **WordPress check:** Verify site is accessible and functioning
- [ ] **Category mapping:** Ensure categories match WordPress categories
- [ ] **Content selection:** 20-50 articles recommended per publish session

### Bulk Publishing
1. [ ] Click **"Select All to Publish"** (or manually select articles)
2. [ ] Set rankings (1-10) for priority articles
3. [ ] Assign headline levels (1-4) for featured content
4. [ ] Click **"Publish to basementcowboy.com"**
5. [ ] Wait for success confirmation

### Post-Publish Verification
- [ ] **WordPress verification:** Check site for new posts
- [ ] **Image verification:** Confirm featured images uploaded correctly
- [ ] **Category verification:** Posts appear in correct categories
- [ ] **Error logging:** Note any failed uploads for investigation

---

## Daily Monitoring & Maintenance

### Performance Metrics
- [ ] **Scraping success rate:** Log in daily tracking sheet
- [ ] **AI enhancement quality:** Spot-check 5-10 summaries
- [ ] **Publishing success rate:** Note any WordPress errors
- [ ] **Total API costs:** Check OpenAI usage (target: $5-15/day)

### File Management
- [ ] **Archive old files:** Move files >7 days old to archive folder
- [ ] **Log rotation:** Clear old logs if >1GB total
- [ ] **Backup configuration:** Weekly backup of config files

### System Health
- [ ] **Memory usage:** Monitor if system becomes slow
- [ ] **Error patterns:** Check logs for recurring issues
- [ ] **Source performance:** Note any consistently failing news sources

---

## Weekly Tasks (Fridays)

### Content Analysis
- [ ] **Traffic review:** Check WordPress analytics for top-performing content
- [ ] **AI quality audit:** Review sample of AI-generated summaries for accuracy
- [ ] **Category performance:** Analyze which categories get most engagement

### System Maintenance
- [ ] **Update news sources:** Add/remove sources based on performance
- [ ] **API key rotation:** Check OpenAI key usage and billing
- [ ] **Configuration backup:** Save copies of all config files
- [ ] **Performance review:** Document any system slowdowns or errors

---

## Troubleshooting Quick Reference

### Common Issues & Fixes

**No articles scraped:**
- [ ] Check internet connection
- [ ] Verify news sources list is accessible
- [ ] Test with smaller source subset

**AI enhancement failures:**
- [ ] Check OpenAI API key and billing
- [ ] Verify rate limits not exceeded
- [ ] Test with single article first

**WordPress publishing errors:**
- [ ] Test WP API connection with curl
- [ ] Verify application password is current
- [ ] Check WordPress site is online

**Performance issues:**
- [ ] Restart Flask application
- [ ] Clear browser cache
- [ ] Check available disk space
- [ ] Monitor Python memory usage

---

## Contact Information

**System Issues:** Check `output/logs/` directory first  
**OpenAI Problems:** https://platform.openai.com/account/usage  
**WordPress Issues:** WP admin dashboard → Tools → Site Health  

---

## Daily Metrics Template

```
Date: ___________
Scrape Start Time: ___________
Scrape End Time: ___________
Articles Scraped: ___________
Articles Published: ___________
AI API Cost: $___________
Issues Encountered: ___________
```

**Estimated Daily Time Investment:** 60-90 minutes
