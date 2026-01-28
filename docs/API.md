# Basement Cowboy API Documentation

This document describes the REST API endpoints available in Basement Cowboy.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Some endpoints require an OpenAI API key to be configured. This can be set via:
- Environment variable: `OPENAI_API_KEY`
- Session configuration in the web UI
- API endpoint: `POST /api/config/api-key`

## Endpoints

### Articles

#### List Articles

```http
GET /api/articles
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status (scraped, ranked, enhanced, published) |
| `category` | string | Filter by category |
| `source` | string | Filter by source name |
| `limit` | integer | Maximum articles to return (default: 50) |
| `offset` | integer | Pagination offset |

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "abc123",
      "title": "Article Title",
      "url": "https://example.com/article",
      "source": {
        "name": "Example News",
        "domain": "example.com"
      },
      "category": "Technology",
      "scraped_at": "2024-01-15T10:30:00Z",
      "rank_score": 0.85
    }
  ],
  "meta": {
    "total": 150,
    "page": 1,
    "per_page": 50
  }
}
```

#### Get Article

```http
GET /api/articles/{id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "abc123",
    "title": "Article Title",
    "content": "Full article content...",
    "url": "https://example.com/article",
    "source": {...},
    "ranking_details": {
      "quality": 0.85,
      "credibility": 0.90,
      "timeliness": 0.75
    }
  }
}
```

#### Delete Article

```http
DELETE /api/articles/{id}
```

**Response:**
```json
{
  "success": true,
  "message": "Article deleted"
}
```

### Scraping

#### Start Scraper

```http
POST /api/scrape
```

**Request Body:**
```json
{
  "sources": ["https://reuters.com", "https://bbc.com"],
  "max_articles": 100,
  "use_playwright": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "task_id": "scrape_12345",
    "status": "running",
    "message": "Scraping started"
  }
}
```

#### Get Scraper Status

```http
GET /api/scrape/status
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "running",
    "articles_found": 45,
    "sources_completed": 10,
    "sources_total": 20,
    "errors": []
  }
}
```

### Ranking

#### Rank Articles

```http
POST /api/rank
```

**Request Body:**
```json
{
  "article_ids": ["abc123", "def456"],
  "weights": {
    "quality": 0.25,
    "credibility": 0.25,
    "engagement": 0.15,
    "visuals": 0.10,
    "timeliness": 0.15,
    "category_diversity": 0.05,
    "geographic_diversity": 0.05
  },
  "top_n": 10
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "article_id": "abc123",
        "total_score": 0.92,
        "rank_position": 1,
        "scores": {
          "quality": 0.95,
          "credibility": 0.90
        }
      }
    ],
    "processing_time_ms": 150
  }
}
```

### AI Enhancement

#### Enhance Article

```http
POST /api/enhance/{id}
```

**Request Body:**
```json
{
  "generate_summary": true,
  "generate_image": false,
  "summary_style": "concise"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "article_id": "abc123",
    "summary": "Generated summary...",
    "image_url": null,
    "cost": 0.002
  }
}
```

### WordPress Publishing

#### Test Connection

```http
GET /api/wordpress/test
```

**Response:**
```json
{
  "success": true,
  "data": {
    "connected": true,
    "site_name": "My WordPress Site",
    "graphql_available": true
  }
}
```

#### Publish Article

```http
POST /api/publish
```

**Request Body:**
```json
{
  "article_id": "abc123",
  "status": "draft",
  "category_id": 5,
  "tag_ids": [10, 15],
  "generate_image": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "post_id": 1234,
    "post_url": "https://mysite.com/2024/01/15/article-title/",
    "media_id": 5678,
    "ai_cost": 0.045
  }
}
```

#### Get Categories

```http
GET /api/wordpress/categories
```

**Response:**
```json
{
  "success": true,
  "data": [
    {"id": 1, "name": "Uncategorized"},
    {"id": 5, "name": "Technology"},
    {"id": 6, "name": "Business"}
  ]
}
```

### Statistics

#### Get Dashboard Stats

```http
GET /api/stats
```

**Response:**
```json
{
  "success": true,
  "data": {
    "articles": 150,
    "sources": 25,
    "published": 45,
    "ai_cost": 2.35,
    "daily_limit": 50.00,
    "categories": {
      "Technology": 45,
      "Business": 30,
      "Politics": 25
    }
  }
}
```

### Configuration

#### Get Config

```http
GET /api/config
```

**Response:**
```json
{
  "success": true,
  "data": {
    "has_openai_key": true,
    "has_wordpress": true,
    "scraper": {
      "max_articles": 100,
      "request_delay": 1.0
    }
  }
}
```

#### Set API Key

```http
POST /api/config/api-key
```

**Request Body:**
```json
{
  "api_key": "sk-..."
}
```

## Error Responses

All errors follow this format:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid article ID",
    "details": {
      "field": "article_id"
    }
  }
}
```

**Error Codes:**
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `NOT_FOUND` | 404 | Resource not found |
| `UNAUTHORIZED` | 401 | Authentication required |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

## Rate Limiting

- Default: 30 requests per minute
- Scraping operations: 1 request per second
- AI operations: Subject to OpenAI rate limits

## Webhooks (Coming Soon)

Support for webhooks to notify external services when:
- New articles are scraped
- Articles are published
- Errors occur
