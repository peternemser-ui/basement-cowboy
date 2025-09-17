# WordPress GraphQL Integration Guide

## Overview

The Basement Cowboy application has been successfully converted from WordPress REST API to GraphQL API. This provides better performance, more flexible queries, and improved type safety.

## What Changed

### 1. **New Dependencies Added**
- `gql[requests]` - GraphQL client library
- `graphql-core` - Core GraphQL implementation

### 2. **New Files Created**
- `app/wordpress_graphql.py` - GraphQL client implementation
- `test_graphql_wordpress.py` - GraphQL integration tests

### 3. **Modified Files**
- `app/routes.py` - Updated to use GraphQL instead of REST API
- `config/wordpress_config.json` - Added GraphQL endpoint configuration
- `requirements.txt` - Added GraphQL dependencies

## WordPress Requirements

### Required WordPress Plugins

1. **WPGraphQL** (Required)
   - Download: https://wordpress.org/plugins/wp-graphql/
   - Provides GraphQL endpoint at `/graphql`
   - Enables GraphQL queries and mutations

2. **WPGraphQL Upload** (Optional)
   - For advanced media upload handling via GraphQL
   - Fallback to REST API for media uploads if not available

### Installation Steps

1. **Install WPGraphQL Plugin:**
   ```bash
   # Via WordPress Admin
   Plugins → Add New → Search "WPGraphQL" → Install & Activate
   
   # Or via WP-CLI
   wp plugin install wp-graphql --activate
   ```

2. **Verify GraphQL Endpoint:**
   - Visit: `https://yoursite.com/graphql`
   - Should show GraphQL Playground or endpoint info

3. **Test GraphQL Access:**
   ```bash
   # Run the test script
   python test_graphql_wordpress.py
   ```

## Configuration

### WordPress Config File
```json
{
  "wordpress_url": "https://yoursite.com",
  "username": "your-wp-username",
  "application_password": "your-app-password",
  "graphql_endpoint": "https://yoursite.com/graphql",
  "api_version": "graphql",
  "plugins_required": [
    "WPGraphQL",
    "WPGraphQL Upload (optional)"
  ]
}
```

## GraphQL Operations

### 1. **Create Posts**
```graphql
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    post {
      id
      databaseId
      title
      content
      status
      date
      link
    }
    errors {
      field
      message
    }
  }
}
```

### 2. **Upload Media**
- Uses GraphQL when WPGraphQL Upload plugin is available
- Falls back to REST API (`/wp-json/wp/v2/media`) for compatibility

### 3. **Query Posts**
```graphql
query GetPosts($first: Int!) {
  posts(first: $first, where: {orderby: {field: DATE, order: DESC}}) {
    nodes {
      id
      title
      date
      status
      link
    }
  }
}
```

## Benefits of GraphQL

### 1. **Better Performance**
- Request only the data you need
- Single endpoint for all operations
- Reduced network overhead

### 2. **Type Safety**
- Strong typing system
- Better error handling
- Automatic validation

### 3. **Flexible Queries**
- Fetch related data in single request
- Avoid over-fetching
- Real-time subscriptions support

### 4. **Better Developer Experience**
- Self-documenting API
- GraphQL Playground for testing
- IntrospectionQuery support

## Implementation Details

### Authentication
- Uses same WordPress Application Passwords
- Basic Authentication header format
- Compatible with existing credentials

### Error Handling
- GraphQL-specific error responses
- Graceful fallbacks for media uploads
- Enhanced logging for debugging

### Media Uploads
- Primary: GraphQL mutations (when supported)
- Fallback: REST API endpoints
- Maintains compatibility with existing images

## Testing

### Run GraphQL Tests
```bash
# Install dependencies first
pip install -r requirements.txt

# Run GraphQL integration tests
python test_graphql_wordpress.py
```

### Test Results Should Show:
- ✅ GraphQL client creation
- ✅ Connection to WordPress
- ✅ Query operations (get posts)
- ✅ Mutation operations (create draft post)

## Troubleshooting

### Common Issues

1. **"Connection Failed" Error**
   - Check if WPGraphQL plugin is installed and activated
   - Verify WordPress site is accessible
   - Confirm application password is correct

2. **"Import gql could not be resolved" Error**
   ```bash
   pip install gql[requests] graphql-core
   ```

3. **GraphQL Endpoint Not Found (404)**
   - Install WPGraphQL plugin
   - Check plugin is activated
   - Verify endpoint at `/graphql`

4. **Permission Denied Errors**
   - Verify application password is correct
   - Check user has publishing permissions
   - Confirm Basic Auth header format

### Debug Mode

Enable detailed logging by setting log level:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration Notes

### Backward Compatibility
- All existing functionality preserved
- Same configuration file format (with additions)
- Same authentication method
- Same application behavior

### Performance Improvements
- Faster post creation with GraphQL
- Better error messages
- Reduced API calls
- Improved debugging

### Future Enhancements
- Real-time subscriptions for content updates
- Advanced media handling with WPGraphQL Upload
- Custom post types and fields support
- Multi-site publishing capabilities

## WordPress Plugin Installation Commands

### Via WordPress Admin Panel
1. Navigate to `Plugins → Add New`
2. Search for "WPGraphQL"
3. Click "Install Now" → "Activate"

### Via WP-CLI
```bash
# Install and activate WPGraphQL
wp plugin install wp-graphql --activate

# Install WPGraphQL Upload (optional)
wp plugin install wp-graphql-upload --activate

# Verify plugins are active
wp plugin list --status=active
```

### Via FTP/Manual Installation
1. Download WPGraphQL from WordPress.org
2. Upload to `/wp-content/plugins/`
3. Activate in WordPress admin

## Support

### Resources
- WPGraphQL Documentation: https://www.wpgraphql.com/docs/
- GraphQL Specification: https://graphql.org/
- GQL Python Client: https://gql.readthedocs.io/

### Getting Help
- Check the test script output for specific errors
- Review WordPress error logs
- Verify plugin compatibility
- Test GraphQL endpoint directly in browser