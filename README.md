# OpenSearch MCP Python Server

A Model Context Protocol (MCP) server for interacting with OpenSearch clusters. This server provides tools to search, query, and retrieve data from OpenSearch indices.

## Features

- **Search Operations**: Execute various types of search queries (simple string, match, range queries)
- **Index Management**: List and inspect OpenSearch indices
- **Document Retrieval**: Get specific documents by ID
- **Cluster Health**: Monitor cluster status and health
- **Index Mapping**: Retrieve index mappings and schema information

## Installation

1. Clone or create the project directory
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment configuration:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` with your OpenSearch connection details:
   ```
   OPENSEARCH_HOST=your-opensearch-host
   OPENSEARCH_PORT=9200
   OPENSEARCH_USERNAME=your-username
   OPENSEARCH_PASSWORD=your-password
   OPENSEARCH_USE_SSL=true
   OPENSEARCH_VERIFY_CERTS=true
   ```

## Configuration

The server uses environment variables for configuration:

- `OPENSEARCH_HOST`: OpenSearch host (default: localhost)
- `OPENSEARCH_PORT`: OpenSearch port (default: 9200)
- `OPENSEARCH_USERNAME`: Username for authentication
- `OPENSEARCH_PASSWORD`: Password for authentication
- `OPENSEARCH_USE_SSL`: Use SSL connection (default: false)
- `OPENSEARCH_VERIFY_CERTS`: Verify SSL certificates (default: false)

## Usage

### Running the Server

```bash
python opensearch_mcp_server.py
```

### Available Operations

The OpenSearch service provides the following methods:

#### Search Operations
- `search(index, query, size)`: Execute custom query
- `simple_search(index, query_string, size)`: Simple string-based search
- `match_search(index, field, value, size)`: Match query for specific field
- `range_search(index, field, gte, lte, gt, lt, size)`: Range-based queries

#### Data Retrieval
- `get_document(index, doc_id)`: Retrieve specific document
- `get_indices()`: List all available indices
- `get_index_mapping(index)`: Get index mapping/schema

#### Cluster Information
- `get_cluster_health()`: Get cluster health status

## Example Queries

### Simple Text Search
```python
results = opensearch_service.simple_search("my-index", "search terms", size=10)
```

### Match Query
```python
results = opensearch_service.match_search("my-index", "title", "search value", size=5)
```

### Range Query
```python
results = opensearch_service.range_search("my-index", "timestamp", gte="2024-01-01", lte="2024-12-31")
```

### Custom Query
```python
custom_query = {
    "query": {
        "bool": {
            "must": [
                {"match": {"title": "important"}},
                {"range": {"date": {"gte": "2024-01-01"}}}
            ]
        }
    }
}
results = opensearch_service.search("my-index", custom_query, size=20)
```

## Data Models

The server uses structured data models:

- `SearchResponse`: Contains search results with hits, total count, and metadata
- `SearchHit`: Individual search result with document data and score
- `IndexInfo`: Index metadata including health, document count, and size
- `ClusterHealth`: Cluster status and node information

## Error Handling

The service handles common OpenSearch errors:
- Connection errors
- Authentication failures
- Invalid queries
- Missing indices
- Network timeouts

## Security

- Supports SSL/TLS connections
- Username/password authentication
- Certificate verification options
- Environment-based credential management

## Development

To extend the server:

1. Add new methods to `OpenSearchService` class
2. Create corresponding data models in `opensearch_models.py`
3. Update configuration in `config.py` if needed
4. Test with your OpenSearch cluster

## Dependencies

- `opensearch-py`: Official OpenSearch Python client
- `python-dotenv`: Environment variable management
- `requests`: HTTP client library
- `mcp`: Model Context Protocol framework
- `fastapi`: Web framework for HTTP endpoints
- `uvicorn`: ASGI server