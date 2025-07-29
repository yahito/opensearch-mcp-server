from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class SearchHit:
    """Represents a single search result hit from OpenSearch"""
    index: str
    id: str
    score: float
    source: Dict[str, Any]
    highlight: Optional[Dict[str, List[str]]] = None


@dataclass
class SearchResponse:
    """Represents an OpenSearch search response"""
    total_hits: int
    max_score: float
    hits: List[SearchHit]
    took: int
    timed_out: bool
    aggregations: Optional[Dict[str, Any]] = None


@dataclass
class IndexInfo:
    """Represents information about an OpenSearch index"""
    name: str
    health: str
    status: str
    uuid: str
    pri: int
    rep: int
    docs_count: int
    docs_deleted: int
    store_size: str
    pri_store_size: str


@dataclass
class ClusterHealth:
    """Represents OpenSearch cluster health information"""
    cluster_name: str
    status: str
    timed_out: bool
    number_of_nodes: int
    number_of_data_nodes: int
    active_primary_shards: int
    active_shards: int
    relocating_shards: int
    initializing_shards: int
    unassigned_shards: int
    delayed_unassigned_shards: int
    number_of_pending_tasks: int
    number_of_in_flight_fetch: int
    task_max_waiting_in_queue_millis: int
    active_shards_percent_as_number: float