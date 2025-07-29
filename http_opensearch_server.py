#!/usr/bin/env python3
import json
import logging
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import uvicorn

from config import opensearch_config
from opensearch_service import OpenSearchService


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("opensearch-http-server")

# Initialize OpenSearch service
opensearch_service = OpenSearchService(opensearch_config)

# Create FastAPI app
app = FastAPI(
    title="OpenSearch MCP HTTP Server",
    description="HTTP wrapper for OpenSearch MCP tools",
    version="1.0.0"
)


def format_search_result(hit):
    """Format search hit for responses"""
    return {
        "id": hit.id,
        "score": hit.score,
        "source": hit.source,
        "highlight": hit.highlight
    }


def format_search_response(response):
    """Format search response"""
    return {
        "total_hits": response.total_hits,
        "max_score": response.max_score,
        "took": response.took,
        "timed_out": response.timed_out,
        "hits": [format_search_result(hit) for hit in response.hits]
    }


@app.get("/api/opensearch/cluster/health")
async def get_cluster_health():
    """Get OpenSearch cluster health"""
    try:
        logger.info("Getting cluster health")
        health = opensearch_service.get_cluster_health()
        result = {
            "cluster_name": health.cluster_name,
            "status": health.status,
            "timed_out": health.timed_out,
            "number_of_nodes": health.number_of_nodes,
            "number_of_data_nodes": health.number_of_data_nodes,
            "active_primary_shards": health.active_primary_shards,
            "active_shards": health.active_shards,
            "relocating_shards": health.relocating_shards,
            "initializing_shards": health.initializing_shards,
            "unassigned_shards": health.unassigned_shards,
            "active_shards_percent": health.active_shards_percent_as_number
        }
        return result
    except Exception as e:
        logger.error(f"Error getting cluster health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/opensearch/indices")
async def get_indices():
    """Get all OpenSearch indices"""
    try:
        logger.info("Getting all indices")
        indices = opensearch_service.get_indices()
        result = [
            {
                "name": idx.name,
                "health": idx.health,
                "status": idx.status,
                "uuid": idx.uuid,
                "primary_shards": idx.pri,
                "replica_shards": idx.rep,
                "docs_count": idx.docs_count,
                "docs_deleted": idx.docs_deleted,
                "store_size": idx.store_size,
                "primary_store_size": idx.pri_store_size
            }
            for idx in indices
        ]
        return result
    except Exception as e:
        logger.error(f"Error getting indices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/opensearch/indices/{index}/mapping")
async def get_index_mapping(index: str):
    """Get mapping for a specific index"""
    try:
        logger.info(f"Getting mapping for index: {index}")
        mapping = opensearch_service.get_index_mapping(index)
        return mapping
    except Exception as e:
        logger.error(f"Error getting mapping for {index}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/opensearch/indices/{index}/documents/{doc_id}")
async def get_document(index: str, doc_id: str):
    """Get a specific document by ID"""
    try:
        logger.info(f"Getting document {doc_id} from index {index}")
        document = opensearch_service.get_document(index, doc_id)
        return document
    except Exception as e:
        logger.error(f"Error getting document {doc_id} from {index}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/opensearch/indices/{index}/search")
async def simple_search(index: str, q: str = Query(), size: int = Query(default=10)):
    """Simple string search in an index"""
    try:
        logger.info(f"Simple search in {index} for: {q}")
        response = opensearch_service.simple_search(index, q, size)
        return format_search_response(response)
    except Exception as e:
        logger.error(f"Error in simple search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/opensearch/indices/{index}/search")
async def custom_search(index: str, query: Dict[str, Any], size: int = 10):
    """Custom search with query DSL"""
    try:
        logger.info(f"Custom search in {index} with query: {query}")
        response = opensearch_service.search(index, query, size)
        return format_search_response(response)
    except Exception as e:
        logger.error(f"Error in custom search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/opensearch/indices/{index}/search/match")
async def match_search(
    index: str, 
    field: str = Query(), 
    value: str = Query(), 
    size: int = Query(default=10)
):
    """Match search for a specific field"""
    try:
        logger.info(f"Match search in {index} for {field}:{value}")
        response = opensearch_service.match_search(index, field, value, size)
        return format_search_response(response)
    except Exception as e:
        logger.error(f"Error in match search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/opensearch/indices/{index}/search/range")
async def range_search(
    index: str,
    field: str = Query(),
    gte: Optional[str] = Query(default=None),
    lte: Optional[str] = Query(default=None),
    gt: Optional[str] = Query(default=None),
    lt: Optional[str] = Query(default=None),
    size: int = Query(default=10)
):
    """Range search for a specific field"""
    try:
        logger.info(f"Range search in {index} for field {field}")
        response = opensearch_service.range_search(index, field, gte, lte, gt, lt, size)
        return format_search_response(response)
    except Exception as e:
        logger.error(f"Error in range search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# MCP Protocol endpoints
@app.post("/")
async def mcp_rpc_endpoint(request: dict):
    """Main MCP JSON-RPC endpoint"""
    try:
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "logging": {}
                    },
                    "serverInfo": {
                        "name": "opensearch-http-server",
                        "version": "1.0.0"
                    }
                }
            }
            
        elif method == "tools/list":
            tools = [
                {
                    "name": "search",
                    "description": "Execute a custom search query against an OpenSearch index",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "index": {"type": "string", "description": "The index name to search in"},
                            "query": {"type": "object", "description": "OpenSearch query DSL object"},
                            "size": {"type": "integer", "description": "Maximum number of results", "default": 10}
                        },
                        "required": ["index", "query"]
                    }
                },
                {
                    "name": "simple_search",
                    "description": "Execute a simple string search query against an OpenSearch index",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "index": {"type": "string", "description": "The index name to search in"},
                            "query_string": {"type": "string", "description": "Simple search query string"},
                            "size": {"type": "integer", "description": "Maximum number of results", "default": 10}
                        },
                        "required": ["index", "query_string"]
                    }
                },
                {
                    "name": "match_search",
                    "description": "Execute a match query for a specific field in an OpenSearch index",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "index": {"type": "string", "description": "The index name to search in"},
                            "field": {"type": "string", "description": "The field name to match against"},
                            "value": {"type": "string", "description": "The value to match"},
                            "size": {"type": "integer", "description": "Maximum number of results", "default": 10}
                        },
                        "required": ["index", "field", "value"]
                    }
                },
                {
                    "name": "range_search",
                    "description": "Execute a range query for a specific field in an OpenSearch index",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "index": {"type": "string", "description": "The index name to search in"},
                            "field": {"type": "string", "description": "The field name to perform range query on"},
                            "gte": {"description": "Greater than or equal to value"},
                            "lte": {"description": "Less than or equal to value"},
                            "gt": {"description": "Greater than value"},
                            "lt": {"description": "Less than value"},
                            "size": {"type": "integer", "description": "Maximum number of results", "default": 10}
                        },
                        "required": ["index", "field"]
                    }
                },
                {
                    "name": "get_document",
                    "description": "Get a specific document by ID from an OpenSearch index",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "index": {"type": "string", "description": "The index name"},
                            "doc_id": {"type": "string", "description": "The document ID"}
                        },
                        "required": ["index", "doc_id"]
                    }
                },
                {
                    "name": "get_indices",
                    "description": "Get information about all available OpenSearch indices",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_cluster_health",
                    "description": "Get OpenSearch cluster health information",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "get_index_mapping",
                    "description": "Get the mapping (schema) for a specific OpenSearch index",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "index": {"type": "string", "description": "The index name"}
                        },
                        "required": ["index"]
                    }
                }
            ]
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": tools
                }
            }
            
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "search":
                response = opensearch_service.search(
                    arguments.get("index"),
                    arguments.get("query"),
                    arguments.get("size", 10)
                )
                result = format_search_response(response)
                
            elif tool_name == "simple_search":
                response = opensearch_service.simple_search(
                    arguments.get("index"),
                    arguments.get("query_string"),
                    arguments.get("size", 10)
                )
                result = format_search_response(response)
                
            elif tool_name == "match_search":
                response = opensearch_service.match_search(
                    arguments.get("index"),
                    arguments.get("field"),
                    arguments.get("value"),
                    arguments.get("size", 10)
                )
                result = format_search_response(response)
                
            elif tool_name == "range_search":
                response = opensearch_service.range_search(
                    arguments.get("index"),
                    arguments.get("field"),
                    arguments.get("gte"),
                    arguments.get("lte"),
                    arguments.get("gt"),
                    arguments.get("lt"),
                    arguments.get("size", 10)
                )
                result = format_search_response(response)
                
            elif tool_name == "get_document":
                result = opensearch_service.get_document(
                    arguments.get("index"),
                    arguments.get("doc_id")
                )
                
            elif tool_name == "get_indices":
                indices = opensearch_service.get_indices()
                result = [
                    {
                        "name": idx.name,
                        "health": idx.health,
                        "status": idx.status,
                        "uuid": idx.uuid,
                        "primary_shards": idx.pri,
                        "replica_shards": idx.rep,
                        "docs_count": idx.docs_count,
                        "docs_deleted": idx.docs_deleted,
                        "store_size": idx.store_size,
                        "primary_store_size": idx.pri_store_size
                    }
                    for idx in indices
                ]
                
            elif tool_name == "get_cluster_health":
                health = opensearch_service.get_cluster_health()
                result = {
                    "cluster_name": health.cluster_name,
                    "status": health.status,
                    "timed_out": health.timed_out,
                    "number_of_nodes": health.number_of_nodes,
                    "number_of_data_nodes": health.number_of_data_nodes,
                    "active_primary_shards": health.active_primary_shards,
                    "active_shards": health.active_shards,
                    "relocating_shards": health.relocating_shards,
                    "initializing_shards": health.initializing_shards,
                    "unassigned_shards": health.unassigned_shards,
                    "active_shards_percent": health.active_shards_percent_as_number
                }
                
            elif tool_name == "get_index_mapping":
                result = opensearch_service.get_index_mapping(arguments.get("index"))
                
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
                
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
            
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            
    except Exception as e:
        logger.error(f"Error in MCP RPC: {e}")
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "opensearch-http-server"}


if __name__ == "__main__":
    logger.info("Starting OpenSearch HTTP Server on port 8091")
    uvicorn.run(app, host="0.0.0.0", port=8091)