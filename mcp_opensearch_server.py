#!/usr/bin/env python3
import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)

from config import opensearch_config
from opensearch_service import OpenSearchService


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("opensearch-mcp-server")

# Initialize OpenSearch service
opensearch_service = OpenSearchService(opensearch_config)

# Create MCP server
server = Server("opensearch-mcp-server")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available OpenSearch tools."""
    return [
        Tool(
            name="search",
            description="Execute a custom search query against an OpenSearch index",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "The index name to search in"
                    },
                    "query": {
                        "type": "object",
                        "description": "OpenSearch query DSL object"
                    },
                    "size": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["index", "query"]
            }
        ),
        Tool(
            name="simple_search",
            description="Execute a simple string search query against an OpenSearch index",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "The index name to search in"
                    },
                    "query_string": {
                        "type": "string",
                        "description": "Simple search query string"
                    },
                    "size": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["index", "query_string"]
            }
        ),
        Tool(
            name="match_search",
            description="Execute a match query for a specific field in an OpenSearch index",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "The index name to search in"
                    },
                    "field": {
                        "type": "string",
                        "description": "The field name to match against"
                    },
                    "value": {
                        "type": "string",
                        "description": "The value to match"
                    },
                    "size": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["index", "field", "value"]
            }
        ),
        Tool(
            name="range_search",
            description="Execute a range query for a specific field in an OpenSearch index",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "The index name to search in"
                    },
                    "field": {
                        "type": "string",
                        "description": "The field name to perform range query on"
                    },
                    "gte": {
                        "description": "Greater than or equal to value"
                    },
                    "lte": {
                        "description": "Less than or equal to value"
                    },
                    "gt": {
                        "description": "Greater than value"
                    },
                    "lt": {
                        "description": "Less than value"
                    },
                    "size": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["index", "field"]
            }
        ),
        Tool(
            name="get_document",
            description="Get a specific document by ID from an OpenSearch index",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "The index name"
                    },
                    "doc_id": {
                        "type": "string",
                        "description": "The document ID"
                    }
                },
                "required": ["index", "doc_id"]
            }
        ),
        Tool(
            name="get_indices",
            description="Get information about all available OpenSearch indices",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_cluster_health",
            description="Get OpenSearch cluster health information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_index_mapping",
            description="Get the mapping (schema) for a specific OpenSearch index",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "The index name"
                    }
                },
                "required": ["index"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "search":
            index = arguments.get("index")
            query = arguments.get("query")
            size = arguments.get("size", 10)
            
            if not index:
                raise ValueError("index is required")
            if not query:
                raise ValueError("query is required")
            
            response = opensearch_service.search(index, query, size)
            result = {
                "total_hits": response.total_hits,
                "max_score": response.max_score,
                "took": response.took,
                "timed_out": response.timed_out,
                "hits": [
                    {
                        "id": hit.id,
                        "score": hit.score,
                        "source": hit.source,
                        "highlight": hit.highlight
                    }
                    for hit in response.hits
                ]
            }
            
        elif name == "simple_search":
            index = arguments.get("index")
            query_string = arguments.get("query_string")
            size = arguments.get("size", 10)
            
            response = opensearch_service.simple_search(index, query_string, size)
            result = {
                "total_hits": response.total_hits,
                "max_score": response.max_score,
                "took": response.took,
                "hits": [
                    {
                        "id": hit.id,
                        "score": hit.score,
                        "source": hit.source
                    }
                    for hit in response.hits
                ]
            }
            
        elif name == "match_search":
            index = arguments.get("index")
            field = arguments.get("field")
            value = arguments.get("value")
            size = arguments.get("size", 10)
            
            response = opensearch_service.match_search(index, field, value, size)
            result = {
                "total_hits": response.total_hits,
                "max_score": response.max_score,
                "took": response.took,
                "hits": [
                    {
                        "id": hit.id,
                        "score": hit.score,
                        "source": hit.source
                    }
                    for hit in response.hits
                ]
            }
            
        elif name == "range_search":
            index = arguments.get("index")
            field = arguments.get("field")
            gte = arguments.get("gte")
            lte = arguments.get("lte")
            gt = arguments.get("gt")
            lt = arguments.get("lt")
            size = arguments.get("size", 10)
            
            response = opensearch_service.range_search(index, field, gte, lte, gt, lt, size)
            result = {
                "total_hits": response.total_hits,
                "max_score": response.max_score,
                "took": response.took,
                "hits": [
                    {
                        "id": hit.id,
                        "score": hit.score,
                        "source": hit.source
                    }
                    for hit in response.hits
                ]
            }
            
        elif name == "get_document":
            index = arguments.get("index")
            doc_id = arguments.get("doc_id")
            
            result = opensearch_service.get_document(index, doc_id)
            
        elif name == "get_indices":
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
            
        elif name == "get_cluster_health":
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
                "delayed_unassigned_shards": health.delayed_unassigned_shards,
                "number_of_pending_tasks": health.number_of_pending_tasks,
                "number_of_in_flight_fetch": health.number_of_in_flight_fetch,
                "task_max_waiting_in_queue_millis": health.task_max_waiting_in_queue_millis,
                "active_shards_percent": health.active_shards_percent_as_number
            }
            
        elif name == "get_index_mapping":
            index = arguments.get("index")
            
            result = opensearch_service.get_index_mapping(index)
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        logger.error(f"Error in {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting OpenSearch MCP Server")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="opensearch-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())