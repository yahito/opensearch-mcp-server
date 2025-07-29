#!/usr/bin/env python3
"""
Demo script showing various OpenSearch operations with the MCP server
"""
from opensearch_service import OpenSearchService
from config import opensearch_config

def main():
    service = OpenSearchService(opensearch_config)

    print('=== Testing Blog Posts Search ===')
    results = service.simple_search('blog-posts', 'machine learning', size=5)
    print(f'Found {results.total_hits} blog posts about machine learning:')
    for hit in results.hits:
        print(f'  - {hit.source.get("title", "No title")} (Score: {hit.score})')

    print('\n=== Testing Product Price Range ===')
    results = service.range_search('products', 'price', gte=100, lte=500)
    print(f'Found {results.total_hits} products in price range $100-$500:')
    for hit in results.hits:
        print(f'  - {hit.source.get("name", "No name")}: ${hit.source.get("price", "N/A")}')

    print('\n=== Testing User Activity ===')
    results = service.match_search('user-activity', 'action', 'search')
    print(f'Found {results.total_hits} search activities:')
    for hit in results.hits:
        print(f'  - User {hit.source.get("user_id", "unknown")} searched on {hit.source.get("device", "unknown")} device')

    print('\n=== Getting Specific Document ===')
    doc = service.get_document('blog-posts', '1')
    print(f'Blog post 1: {doc.get("title", "No title")}')
    print(f'Author: {doc.get("author", "Unknown")}')
    print(f'Tags: {doc.get("tags", [])}')

    print('\n=== Complex Query Example ===')
    complex_query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"category": "tutorial"}},
                    {"range": {"view_count": {"gte": 1000}}}
                ]
            }
        }
    }
    results = service.search('blog-posts', complex_query)
    print(f'Found {results.total_hits} tutorial posts with >1000 views:')
    for hit in results.hits:
        print(f'  - {hit.source.get("title", "No title")} ({hit.source.get("view_count", 0)} views)')

if __name__ == "__main__":
    main()