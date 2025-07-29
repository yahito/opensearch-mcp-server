#!/usr/bin/env python3
import logging
from config import opensearch_config
from opensearch_service import OpenSearchService


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting OpenSearch MCP Server")
    
    # Initialize configuration and service
    opensearch_service = OpenSearchService(opensearch_config)
    
    # Example usage
    try:
        # Get cluster health
        health = opensearch_service.get_cluster_health()
        logger.info(f"Cluster health: {health.status} - {health.cluster_name}")
        
        # Get all indices
        indices = opensearch_service.get_indices()
        logger.info(f"Found {len(indices)} indices")
        
        for index in indices[:5]:  # Show first 5 indices
            logger.info(f"Index: {index.name} - Health: {index.health}, Docs: {index.docs_count}")
        
        # Example search (if there are indices)
        if indices:
            first_index = indices[0].name
            try:
                # Simple match-all query
                results = opensearch_service.search(first_index, {"query": {"match_all": {}}}, size=3)
                logger.info(f"Sample search in '{first_index}': found {results.total_hits} total documents")
                
                for hit in results.hits:
                    logger.info(f"Document {hit.id}: score={hit.score}")
                    
            except Exception as search_error:
                logger.warning(f"Could not perform sample search: {search_error}")
        
    except Exception as e:
        logger.error(f"Error accessing OpenSearch: {e}")


if __name__ == "__main__":
    main()