import logging
from typing import List, Optional, Dict, Any
import requests
from opensearchpy import OpenSearch
from opensearchpy.exceptions import ConnectionError, RequestError

from config import opensearch_config, OpenSearchConfig
from opensearch_models import SearchHit, SearchResponse, IndexInfo, ClusterHealth


logger = logging.getLogger(__name__)


class OpenSearchService:
    def __init__(self, config: OpenSearchConfig):
        self.config = config
        self.use_requests = config.use_cookies or config.auth_headers
        
        if self.use_requests:
            # Use requests session for cookie/header support
            self.session = requests.Session()
            
            # Set up authentication
            if config.username and config.password and not config.use_cookies:
                self.session.auth = (config.username, config.password)
            
            # Set up cookies
            if config.use_cookies:
                # Load from cookie file if specified
                file_cookies = config.load_cookies_from_file()
                if file_cookies:
                    self.session.cookies.update(file_cookies)
                
                # Load from environment variable
                env_cookies = config.parsed_cookies
                if env_cookies:
                    self.session.cookies.update(env_cookies)
            
            # Set up additional headers
            auth_headers = config.parsed_auth_headers
            if auth_headers:
                self.session.headers.update(auth_headers)
            
            # Set default headers
            self.session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            
            # SSL configuration
            self.session.verify = config.verify_certs if config.use_ssl else False
            
            logger.info(f"Using requests session with cookies: {bool(config.use_cookies)}, headers: {bool(auth_headers)}")
        else:
            # Use standard OpenSearch client
            auth = None
            if config.username and config.password:
                auth = (config.username, config.password)
            
            self.client = OpenSearch(
                hosts=[{'host': config.host, 'port': config.port}],
                http_auth=auth,
                use_ssl=config.use_ssl,
                verify_certs=config.verify_certs,
                ssl_assert_hostname=False,
                ssl_show_warn=False,
                timeout=config.timeout_seconds
            )
            logger.info("Using standard OpenSearch client")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request using requests session (for cookie support)"""
        url = f"{self.config.url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.config.timeout_seconds,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            raise RequestError(f"Request failed: {e}")
    
    def search(self, index: str, query: Dict[str, Any], size: Optional[int] = None) -> SearchResponse:
        """Execute a search query against an OpenSearch index"""
        logger.info(f"Searching index '{index}' with query: {query}")
        
        if not index or not index.strip():
            raise ValueError("index is required")
        
        if not query:
            raise ValueError("query is required")
        
        try:
            if self.use_requests:
                # Use requests session for cookie support
                params = {}
                if size:
                    params['size'] = size or 10
                
                response = self._make_request(
                    'POST',
                    f'/{index}/_search',
                    json=query,
                    params=params
                )
            else:
                # Use standard OpenSearch client
                response = self.client.search(
                    index=index,
                    body=query,
                    size=size or 10
                )
            
            return self._parse_search_response(response)
            
        except RequestError as e:
            logger.error(f"Search request error: {e}")
            raise
        except ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            raise
    
    def simple_search(self, index: str, query_string: str, size: Optional[int] = None) -> SearchResponse:
        """Execute a simple string query against an OpenSearch index"""
        logger.info(f"Simple search in index '{index}' for: {query_string}")
        
        if not query_string or not query_string.strip():
            raise ValueError("query_string is required")
        
        query = {
            "query": {
                "query_string": {
                    "query": query_string
                }
            }
        }
        
        return self.search(index, query, size)
    
    def match_search(self, index: str, field: str, value: str, size: Optional[int] = None) -> SearchResponse:
        """Execute a match query for a specific field"""
        logger.info(f"Match search in index '{index}' for field '{field}' with value: {value}")
        
        if not field or not field.strip():
            raise ValueError("field is required")
        if not value or not value.strip():
            raise ValueError("value is required")
        
        query = {
            "query": {
                "match": {
                    field: value
                }
            }
        }
        
        return self.search(index, query, size)
    
    def range_search(self, index: str, field: str, gte: Any = None, lte: Any = None, 
                    gt: Any = None, lt: Any = None, size: Optional[int] = None) -> SearchResponse:
        """Execute a range query for a specific field"""
        logger.info(f"Range search in index '{index}' for field '{field}'")
        
        if not field or not field.strip():
            raise ValueError("field is required")
        
        range_params = {}
        if gte is not None:
            range_params["gte"] = gte
        if lte is not None:
            range_params["lte"] = lte
        if gt is not None:
            range_params["gt"] = gt
        if lt is not None:
            range_params["lt"] = lt
        
        if not range_params:
            raise ValueError("At least one range parameter (gte, lte, gt, lt) is required")
        
        query = {
            "query": {
                "range": {
                    field: range_params
                }
            }
        }
        
        return self.search(index, query, size)
    
    def get_document(self, index: str, doc_id: str) -> Dict[str, Any]:
        """Get a specific document by ID"""
        logger.info(f"Getting document '{doc_id}' from index '{index}'")
        
        if not index or not index.strip():
            raise ValueError("index is required")
        if not doc_id or not doc_id.strip():
            raise ValueError("doc_id is required")
        
        try:
            if self.use_requests:
                response = self._make_request('GET', f'/{index}/_doc/{doc_id}')
                return response["_source"]
            else:
                response = self.client.get(index=index, id=doc_id)
                return response["_source"]
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            raise
    
    def get_indices(self) -> List[IndexInfo]:
        """Get information about all indices"""
        logger.info("Getting all indices information")
        
        try:
            if self.use_requests:
                response = self._make_request('GET', '/_cat/indices', params={'format': 'json', 'v': 'true'})
            else:
                response = self.client.cat.indices(format="json", v=True)
            
            indices = []
            
            for index_data in response:
                indices.append(IndexInfo(
                    name=index_data.get("index", ""),
                    health=index_data.get("health", ""),
                    status=index_data.get("status", ""),
                    uuid=index_data.get("uuid", ""),
                    pri=int(index_data.get("pri", 0)),
                    rep=int(index_data.get("rep", 0)),
                    docs_count=int(index_data.get("docs.count", 0)),
                    docs_deleted=int(index_data.get("docs.deleted", 0)),
                    store_size=index_data.get("store.size", ""),
                    pri_store_size=index_data.get("pri.store.size", "")
                ))
            
            logger.info(f"Found {len(indices)} indices")
            return indices
            
        except Exception as e:
            logger.error(f"Error getting indices: {e}")
            raise
    
    def get_cluster_health(self) -> ClusterHealth:
        """Get cluster health information"""
        logger.info("Getting cluster health")
        
        try:
            if self.use_requests:
                response = self._make_request('GET', '/_cluster/health')
            else:
                response = self.client.cluster.health()
            
            return ClusterHealth(
                cluster_name=response.get("cluster_name", ""),
                status=response.get("status", ""),
                timed_out=response.get("timed_out", False),
                number_of_nodes=response.get("number_of_nodes", 0),
                number_of_data_nodes=response.get("number_of_data_nodes", 0),
                active_primary_shards=response.get("active_primary_shards", 0),
                active_shards=response.get("active_shards", 0),
                relocating_shards=response.get("relocating_shards", 0),
                initializing_shards=response.get("initializing_shards", 0),
                unassigned_shards=response.get("unassigned_shards", 0),
                delayed_unassigned_shards=response.get("delayed_unassigned_shards", 0),
                number_of_pending_tasks=response.get("number_of_pending_tasks", 0),
                number_of_in_flight_fetch=response.get("number_of_in_flight_fetch", 0),
                task_max_waiting_in_queue_millis=response.get("task_max_waiting_in_queue_millis", 0),
                active_shards_percent_as_number=response.get("active_shards_percent_as_number", 0.0)
            )
            
        except Exception as e:
            logger.error(f"Error getting cluster health: {e}")
            raise
    
    def get_index_mapping(self, index: str) -> Dict[str, Any]:
        """Get the mapping for a specific index"""
        logger.info(f"Getting mapping for index '{index}'")
        
        if not index or not index.strip():
            raise ValueError("index is required")
        
        try:
            if self.use_requests:
                response = self._make_request('GET', f'/{index}/_mapping')
            else:
                response = self.client.indices.get_mapping(index=index)
            return response
        except Exception as e:
            logger.error(f"Error getting index mapping: {e}")
            raise
    
    def _parse_search_response(self, response: Dict[str, Any]) -> SearchResponse:
        """Parse OpenSearch response into SearchResponse object"""
        hits_data = response.get("hits", {})
        hits = []
        
        for hit in hits_data.get("hits", []):
            search_hit = SearchHit(
                index=hit.get("_index", ""),
                id=hit.get("_id", ""),
                score=hit.get("_score", 0.0),
                source=hit.get("_source", {}),
                highlight=hit.get("highlight")
            )
            hits.append(search_hit)
        
        return SearchResponse(
            total_hits=hits_data.get("total", {}).get("value", 0),
            max_score=hits_data.get("max_score", 0.0),
            hits=hits,
            took=response.get("took", 0),
            timed_out=response.get("timed_out", False),
            aggregations=response.get("aggregations")
        )