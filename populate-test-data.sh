#!/bin/bash

echo "🧪 Populating OpenSearch with test data..."

# Check if OpenSearch is running
if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:9200/_cluster/health | grep -q "200"; then
    echo "❌ OpenSearch is not running. Please start it first with ./start-opensearch.sh"
    exit 1
fi

# Create sample indices and populate with test data

echo "📝 Creating 'blog-posts' index..."
curl -X PUT "localhost:9200/blog-posts" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "standard"
      },
      "content": {
        "type": "text",
        "analyzer": "standard"
      },
      "author": {
        "type": "keyword"
      },
      "tags": {
        "type": "keyword"
      },
      "published_date": {
        "type": "date"
      },
      "category": {
        "type": "keyword"
      },
      "view_count": {
        "type": "integer"
      }
    }
  }
}'

echo ""
echo "📄 Adding blog post documents..."

# Blog post 1
curl -X POST "localhost:9200/blog-posts/_doc/1" -H 'Content-Type: application/json' -d'
{
  "title": "Getting Started with OpenSearch",
  "content": "OpenSearch is a powerful distributed search and analytics engine. In this post, we will explore how to set up and use OpenSearch for your applications.",
  "author": "alice_doe",
  "tags": ["opensearch", "elasticsearch", "search", "tutorial"],
  "published_date": "2024-01-15T10:00:00Z",
  "category": "tutorial",
  "view_count": 1250
}'

# Blog post 2
curl -X POST "localhost:9200/blog-posts/_doc/2" -H 'Content-Type: application/json' -d'
{
  "title": "Advanced Search Techniques",
  "content": "Learn advanced search techniques including aggregations, complex queries, and performance optimization for large datasets.",
  "author": "bob_smith",
  "tags": ["search", "aggregations", "performance", "advanced"],
  "published_date": "2024-02-20T14:30:00Z",
  "category": "advanced",
  "view_count": 890
}'

# Blog post 3
curl -X POST "localhost:9200/blog-posts/_doc/3" -H 'Content-Type: application/json' -d'
{
  "title": "Machine Learning with OpenSearch",
  "content": "Discover how to integrate machine learning capabilities with OpenSearch for anomaly detection and intelligent search features.",
  "author": "carol_johnson",
  "tags": ["machine-learning", "ai", "anomaly-detection", "opensearch"],
  "published_date": "2024-03-10T09:15:00Z",
  "category": "machine-learning",
  "view_count": 2100
}'

echo ""
echo "🏪 Creating 'products' index..."
curl -X PUT "localhost:9200/products" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "name": {
        "type": "text",
        "analyzer": "standard"
      },
      "description": {
        "type": "text"
      },
      "price": {
        "type": "float"
      },
      "category": {
        "type": "keyword"
      },
      "brand": {
        "type": "keyword"
      },
      "rating": {
        "type": "float"
      },
      "in_stock": {
        "type": "boolean"
      },
      "created_date": {
        "type": "date"
      }
    }
  }
}'

echo ""
echo "🛍️ Adding product documents..."

# Product 1
curl -X POST "localhost:9200/products/_doc/1" -H 'Content-Type: application/json' -d'
{
  "name": "Wireless Bluetooth Headphones",
  "description": "High-quality wireless headphones with noise cancellation and 30-hour battery life",
  "price": 199.99,
  "category": "electronics",
  "brand": "TechBrand",
  "rating": 4.5,
  "in_stock": true,
  "created_date": "2024-01-05T00:00:00Z"
}'

# Product 2
curl -X POST "localhost:9200/products/_doc/2" -H 'Content-Type: application/json' -d'
{
  "name": "Ergonomic Office Chair",
  "description": "Comfortable ergonomic chair with lumbar support and adjustable height",
  "price": 299.99,
  "category": "furniture",
  "brand": "OfficeComfort",
  "rating": 4.2,
  "in_stock": true,
  "created_date": "2024-01-10T00:00:00Z"
}'

# Product 3
curl -X POST "localhost:9200/products/_doc/3" -H 'Content-Type: application/json' -d'
{
  "name": "Stainless Steel Water Bottle",
  "description": "Insulated water bottle that keeps drinks cold for 24 hours or hot for 12 hours",
  "price": 29.99,
  "category": "accessories",
  "brand": "HydroLife",
  "rating": 4.8,
  "in_stock": false,
  "created_date": "2024-02-01T00:00:00Z"
}'

echo ""
echo "📊 Creating 'user-activity' index..."
curl -X PUT "localhost:9200/user-activity" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "user_id": {
        "type": "keyword"
      },
      "action": {
        "type": "keyword"
      },
      "timestamp": {
        "type": "date"
      },
      "page": {
        "type": "keyword"
      },
      "duration": {
        "type": "integer"
      },
      "device": {
        "type": "keyword"
      },
      "ip_address": {
        "type": "ip"
      }
    }
  }
}'

echo ""
echo "👤 Adding user activity documents..."

# Activity 1
curl -X POST "localhost:9200/user-activity/_doc/1" -H 'Content-Type: application/json' -d'
{
  "user_id": "user_123",
  "action": "page_view",
  "timestamp": "2024-03-15T10:30:00Z",
  "page": "/home",
  "duration": 45,
  "device": "desktop",
  "ip_address": "192.168.1.100"
}'

# Activity 2
curl -X POST "localhost:9200/user-activity/_doc/2" -H 'Content-Type: application/json' -d'
{
  "user_id": "user_456",
  "action": "search",
  "timestamp": "2024-03-15T11:15:00Z",
  "page": "/search",
  "duration": 120,
  "device": "mobile",
  "ip_address": "192.168.1.101"
}'

# Activity 3
curl -X POST "localhost:9200/user-activity/_doc/3" -H 'Content-Type: application/json' -d'
{
  "user_id": "user_789",
  "action": "purchase",
  "timestamp": "2024-03-15T14:20:00Z",
  "page": "/checkout",
  "duration": 300,
  "device": "tablet",
  "ip_address": "192.168.1.102"
}'

echo ""
echo "🔄 Refreshing indices to make data searchable..."
curl -X POST "localhost:9200/_refresh"

echo ""
echo "✅ Test data populated successfully!"
echo ""
echo "📈 Summary of created indices:"
curl -s "localhost:9200/_cat/indices?v"

echo ""
echo "🔍 Sample queries to test:"
echo "  Search blog posts: curl \"localhost:9200/blog-posts/_search?q=OpenSearch\""
echo "  Get all products: curl \"localhost:9200/products/_search?pretty\""
echo "  Find user activities: curl \"localhost:9200/user-activity/_search?q=action:search\""
echo ""
echo "🧪 You can now test your OpenSearch MCP server with this data!"