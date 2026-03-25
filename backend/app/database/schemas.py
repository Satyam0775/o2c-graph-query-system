from pydantic import BaseModel
from typing import Optional, List, Any, Dict


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    sql: str
    results: List[Dict[str, Any]]
    answer: str
    row_count: int
    highlighted_nodes: List[str] = []


class NodeResponse(BaseModel):
    id: str
    entity_type: str
    label: str
    properties: Dict[str, Any]
    connections: int


class GraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    total_nodes: int
    total_edges: int


class LoadDataResponse(BaseModel):
    status: str
    tables_loaded: List[str]
    row_counts: Dict[str, int]


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    data_loaded: bool
