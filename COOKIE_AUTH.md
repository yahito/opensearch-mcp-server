# Cookie Authentication Guide

The OpenSearch MCP Server supports cookie-based authentication for scenarios where OpenSearch is behind a proxy, load balancer, or authentication layer that uses session cookies.

## When to Use Cookie Authentication

- OpenSearch is behind a reverse proxy with authentication
- Using SAML, OAuth, or other SSO authentication
- Corporate environments with session-based authentication
- When username/password authentication is not available/desired

## Configuration Options

### Environment Variables

Add these to your `.env` file:

```bash
# Enable cookie authentication
OPENSEARCH_USE_COOKIES=true

# Option 1: Provide cookies as string
OPENSEARCH_COOKIES="sessionid=abc123; csrftoken=xyz789; security_authentication=eyJhbGc..."

# Option 2: Load cookies from file
OPENSEARCH_COOKIE_FILE="/path/to/cookies.txt"

# Optional: Additional authentication headers
OPENSEARCH_AUTH_HEADERS="X-Forwarded-User: username, Authorization: Bearer token"
```

### Complete Example Configuration

```bash
# OpenSearch connection
OPENSEARCH_HOST=opensearch.company.com
OPENSEARCH_PORT=443
OPENSEARCH_USE_SSL=true
OPENSEARCH_VERIFY_CERTS=true

# Cookie authentication
OPENSEARCH_USE_COOKIES=true
OPENSEARCH_COOKIES="security_authentication=eyJhbGc...; oid=user123; session=abc456"
OPENSEARCH_AUTH_HEADERS="X-Forwarded-User: john.doe, X-Department: engineering"
```

## How to Extract Cookies

### Method 1: Browser Developer Tools

1. Open OpenSearch Dashboards in your browser
2. Login normally with your credentials
3. Open Developer Tools (F12)
4. Go to Network tab
5. Make any request to OpenSearch (search, etc.)
6. Right-click on the request → Copy → Copy as cURL
7. Extract the `Cookie:` header from the cURL command

**Example cURL output:**
```bash
curl 'https://opensearch.company.com/_search' \
  -H 'Cookie: security_authentication=eyJhbGc...; oid=user123; session=abc456'
```

**Extract the cookie part:**
```
security_authentication=eyJhbGc...; oid=user123; session=abc456
```

### Method 2: Browser Cookie Export

1. **Chrome:** Use extensions like "Get cookies.txt" or "Export cookies"
2. **Firefox:** Use "Export Cookies" extension
3. **Manual:** Copy cookies from Developer Tools → Application → Cookies

**Cookie file format:**
```
# Simple format (key=value per line)
sessionid=abc123
csrftoken=xyz789
security_authentication=eyJhbGc...

# OR Netscape format (tab-separated)
.company.com	TRUE	/	TRUE	1640995200	sessionid	abc123
.company.com	TRUE	/	TRUE	1640995200	csrftoken	xyz789
```

### Method 3: Programmatic Extraction

Use browser automation tools:

```python
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://opensearch.company.com")
# Login manually or programmatically
cookies = driver.get_cookies()
cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
print(cookie_string)
```

## Authentication Flow

When cookie authentication is enabled, the MCP server:

1. **Session Setup**: Uses `requests.Session()` instead of `opensearch-py` client
2. **Cookie Loading**: Loads cookies from environment variable or file
3. **Header Setup**: Adds authentication headers if specified
4. **Request Execution**: Makes HTTP requests with cookies attached
5. **Automatic Retry**: Cookies are automatically sent with each request

## Supported Authentication Patterns

### 1. Session-Based Authentication
```bash
OPENSEARCH_COOKIES="JSESSIONID=ABC123; XSRF-TOKEN=xyz789"
```

### 2. JWT/Bearer Token in Cookies
```bash
OPENSEARCH_COOKIES="security_authentication=eyJhbGc..."
```

### 3. Proxy Authentication Headers
```bash
OPENSEARCH_AUTH_HEADERS="X-Forwarded-User: john.doe, X-Auth-Group: admins"
```

### 4. Combined Cookie + Header Authentication
```bash
OPENSEARCH_USE_COOKIES=true
OPENSEARCH_COOKIES="session=abc123"
OPENSEARCH_AUTH_HEADERS="Authorization: Bearer token123"
```

## Testing Cookie Authentication

Use the provided test script:

```bash
python test_cookie_auth.py
```

Or test manually:

```python
from config import OpenSearchConfig
from opensearch_service import OpenSearchService

# Set up config with cookies
config = OpenSearchConfig()
config.use_cookies = True
config.cookies = "your_cookie_string_here"

# Test connection
service = OpenSearchService(config)
health = service.get_cluster_health()
print(f"Connected to: {health.cluster_name}")
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Cookies may be expired or invalid
   - Re-extract cookies from fresh browser session
   - Check cookie expiration times

2. **403 Forbidden**: Missing required headers or permissions
   - Add required authentication headers
   - Verify user has proper permissions

3. **SSL/Certificate Errors**: 
   - Set `OPENSEARCH_VERIFY_CERTS=false` for testing
   - Use proper certificates in production

4. **Cookie Format Issues**:
   - Ensure no extra spaces in cookie strings
   - Use semicolon (;) to separate multiple cookies
   - Verify cookie names match exactly

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show:
- HTTP requests being made
- Cookie values being sent
- Response status codes
- Error details

## Security Considerations

1. **Cookie Storage**: Store cookies securely, don't commit to version control
2. **Expiration**: Cookies may expire, implement refresh logic if needed
3. **Network Security**: Always use HTTPS in production
4. **Access Control**: Ensure cookies have appropriate scope and permissions
5. **Rotation**: Regularly rotate authentication tokens/cookies

## Production Deployment

For production use:

1. **Environment Variables**: Use secure environment variable management
2. **Cookie Refresh**: Implement automatic cookie refresh if supported
3. **Monitoring**: Monitor authentication failures and cookie expiration
4. **Backup Auth**: Have fallback authentication methods available
5. **Audit Logging**: Log authentication events for security auditing

## Examples

See `test_cookie_auth.py` for complete working examples of:
- String-based cookie configuration
- File-based cookie loading
- Authentication header setup
- Error handling and debugging