#!/usr/bin/env python3
"""
Test script to verify OpenSearch connection and test the MCP server functionality
"""
import sys
import logging
from config import opensearch_config
from opensearch_service import OpenSearchService

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def test_connection():
    """Test basic OpenSearch connection"""
    print("🔍 Testing OpenSearch Connection...")
    print(f"   Host: {opensearch_config.host}:{opensearch_config.port}")
    print(f"   SSL: {opensearch_config.use_ssl}")
    
    try:
        service = OpenSearchService(opensearch_config)
        health = service.get_cluster_health()
        print(f"✅ Connection successful!")
        print(f"   Cluster: {health.cluster_name}")
        print(f"   Status: {health.status}")
        print(f"   Nodes: {health.number_of_nodes}")
        return service
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def test_indices(service):
    """Test index listing"""
    print("\n📋 Testing Index Listing...")
    try:
        indices = service.get_indices()
        print(f"✅ Found {len(indices)} indices:")
        for idx in indices:
            print(f"   - {idx.name}: {idx.docs_count} docs, {idx.health} health")
        return indices
    except Exception as e:
        print(f"❌ Failed to list indices: {e}")
        return []

def test_search(service, indices):
    """Test search functionality"""
    if not indices:
        print("\n⚠️  No indices found to test search")
        return
    
    print("\n🔍 Testing Search Functions...")
    
    # Test with blog-posts index if available
    blog_index = next((idx for idx in indices if idx.name == 'blog-posts'), None)
    if blog_index:
        print(f"   Testing with 'blog-posts' index...")
        
        try:
            # Simple search
            results = service.simple_search("blog-posts", "OpenSearch", size=3)
            print(f"   ✅ Simple search: {results.total_hits} hits")
            
            # Match search
            results = service.match_search("blog-posts", "title", "OpenSearch", size=2)
            print(f"   ✅ Match search: {results.total_hits} hits")
            
            # Get a document
            if results.hits:
                doc_id = results.hits[0].id
                doc = service.get_document("blog-posts", doc_id)
                print(f"   ✅ Document retrieval: got doc {doc_id}")
                
        except Exception as e:
            print(f"   ❌ Search test failed: {e}")
    
    # Test with products index if available
    products_index = next((idx for idx in indices if idx.name == 'products'), None)
    if products_index:
        print(f"   Testing with 'products' index...")
        
        try:
            # Range search
            results = service.range_search("products", "price", gte=50, lte=300, size=5)
            print(f"   ✅ Range search: {results.total_hits} hits")
            
        except Exception as e:
            print(f"   ❌ Range search test failed: {e}")

def test_mappings(service, indices):
    """Test index mapping retrieval"""
    if not indices:
        return
        
    print("\n🗺️  Testing Index Mappings...")
    
    test_index = indices[0].name
    try:
        mapping = service.get_index_mapping(test_index)
        print(f"   ✅ Retrieved mapping for '{test_index}'")
        # Print first few fields
        if test_index in mapping and 'mappings' in mapping[test_index]:
            fields = list(mapping[test_index]['mappings'].get('properties', {}).keys())[:3]
            print(f"   Sample fields: {', '.join(fields)}")
    except Exception as e:
        print(f"   ❌ Mapping test failed: {e}")

def main():
    setup_logging()
    
    print("🧪 OpenSearch MCP Server Test Suite")
    print("=" * 50)
    
    # Test connection
    service = test_connection()
    if not service:
        print("\n❌ Cannot proceed without connection. Please ensure:")
        print("   1. OpenSearch is running (./start-opensearch.sh)")
        print("   2. Environment variables are set correctly")
        sys.exit(1)
    
    # Test indices
    indices = test_indices(service)
    
    # If no indices, suggest populating test data
    if not indices:
        print("\n💡 No indices found. Run './populate-test-data.sh' to create test data")
    else:
        # Test search functionality
        test_search(service, indices)
        
        # Test mappings
        test_mappings(service, indices)
    
    print("\n🎉 Test suite completed!")
    print("\n📝 Next steps:")
    print("   - Run './populate-test-data.sh' to add test data (if not done)")
    print("   - Use 'python opensearch_mcp_server.py' to run the MCP server")
    print("   - Access OpenSearch Dashboards at http://localhost:5601")

if __name__ == "__main__":
    main()