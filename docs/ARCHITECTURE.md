# Architecture Overview

This document describes the architecture and design decisions of Basement Cowboy.

## System Overview

Basement Cowboy is an AI-powered news aggregation and publishing platform with the following architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Interface                             │
│                    (Flask + Bootstrap 5)                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Flask Application                         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Routes     │  │   Services   │  │   Models     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│  News Sources  │  │   OpenAI API   │  │  WordPress API │
│  (180+ sites)  │  │  (GPT + DALL-E)│  │  (REST/GraphQL)│
└────────────────┘  └────────────────┘  └────────────────┘
```

## Core Components

### 1. Web Scraper (`scraper/`)

The scraping engine handles fetching and parsing news from multiple sources.

**Components:**
- `scrape_news.py` - Main orchestrator
- `fetch_page.py` - HTTP fetching with retry logic
- `parse_articles.py` - HTML parsing and extraction
- `filter_articles.py` - Content filtering and validation
- `dynamic_scraper.py` - Playwright-based JavaScript rendering

**Flow:**
```
News Source → Fetch Page → Parse HTML → Extract Articles → Filter → Save
```

### 2. Flask Application (`app/`)

The web application provides the user interface and API endpoints.

**Layers:**
- **Routes** (`routes.py`) - HTTP endpoints
- **Services** (`services/`) - Business logic
- **Models** (`models/`) - Data structures
- **Utils** (`utils/`) - Helper functions

### 3. Services Layer (`app/services/`)

Business logic is organized into service classes:

| Service | Responsibility |
|---------|---------------|
| `ArticleService` | Article CRUD operations |
| `RankingService` | Multi-factor ranking algorithm |
| `OpenAIService` | AI integration (summaries, images) |
| `WordPressService` | Publishing to WordPress |
| `SEOService` | SEO metadata generation |
| `ScraperService` | Scraping orchestration |
| `StorageService` | File-based storage |
| `CacheService` | In-memory and file caching |

### 4. Data Models (`app/models/`)

Type-safe data structures using Python dataclasses:

```python
@dataclass
class Article:
    id: str
    title: str
    url: str
    source: ArticleSource
    content: str
    status: ArticleStatus
    rank_score: float
    # ...
```

## Data Flow

### Scraping Pipeline

```
1. Load Sources
   └── config/top_100_news_sites.txt

2. Fetch Pages
   └── HTTP requests with retry
   └── Playwright for JS-heavy sites

3. Parse Articles
   └── BeautifulSoup HTML parsing
   └── Extract title, content, images

4. Filter & Validate
   └── Remove duplicates
   └── Check content length
   └── Validate URLs

5. Store Articles
   └── JSON files in output/news_articles/
```

### Ranking Pipeline

```
1. Load Articles
   └── From storage or selection

2. Calculate Scores
   └── Quality (content analysis)
   └── Credibility (source reputation)
   └── Engagement (potential interest)
   └── Visuals (image availability)
   └── Timeliness (article freshness)

3. Apply Weights
   └── Customizable weights
   └── Default balanced weights

4. Sort & Rank
   └── Total score calculation
   └── Position assignment
   └── Diversity adjustment
```

### Publishing Pipeline

```
1. Select Article
   └── User selection from ranked list

2. AI Enhancement (Optional)
   └── Generate summary (GPT)
   └── Generate image (DALL-E)

3. Prepare Post
   └── Format content
   └── Generate SEO metadata
   └── Create WordPress post object

4. Upload Media
   └── Featured image upload
   └── Get media ID

5. Create Post
   └── REST API or GraphQL
   └── Set categories, tags
   └── Apply SEO fields

6. Verify
   └── Check post URL
   └── Update article status
```

## Storage Design

### File-Based Storage

Articles are stored as individual JSON files:

```
output/
├── news_articles/
│   ├── abc123.json
│   ├── def456.json
│   └── ...
├── wordpress-output/
│   └── publish_results.json
├── logs/
│   └── app_2024-01-15.log
└── cache/
    └── {hash}.json
```

**Benefits:**
- No database dependency
- Easy backup/restore
- Human-readable files
- Simple deployment

**Trade-offs:**
- Limited query capabilities
- Manual indexing if needed
- File system performance limits

### Caching Strategy

Two-level caching:
1. **Memory Cache** - Fast, short TTL (5 min)
2. **File Cache** - Persistent, longer TTL (1 hour)

## Security Considerations

### API Keys
- Stored in environment variables
- Never logged or displayed
- Session-scoped in web UI

### Input Validation
- URL validation for sources
- Content sanitization
- Request rate limiting

### External APIs
- HTTPS only
- Retry with backoff
- Cost limits enforced

## Performance Considerations

### Scraping
- Rate limiting (1 req/sec default)
- Concurrent requests limited
- Playwright for heavy sites only

### Ranking
- In-memory processing
- Batch operations
- Cached results

### API Responses
- JSON responses
- Pagination support
- Async operations for long tasks

## Extension Points

### Adding New Sources
1. Add URL to `config/top_100_news_sites.txt`
2. Create custom parser if needed
3. Configure category mapping

### Custom Ranking Weights
1. Create preset in `RankingWeights`
2. Add to UI selection
3. Store user preferences

### Additional AI Features
1. Extend `OpenAIService`
2. Add new endpoints
3. Update cost tracking

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.9+, Flask 3.0 |
| Scraping | BeautifulSoup4, Playwright |
| AI | OpenAI API (GPT, DALL-E) |
| Frontend | Bootstrap 5, Vanilla JS |
| WordPress | REST API, WPGraphQL |
| Storage | JSON files |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Deployment | Docker |
