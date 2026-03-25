from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.graph.graph_service import GraphService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NodeService:
    def __init__(self, session: Session):
        self.graph_service = GraphService(session)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        return self.graph_service.get_node(node_id)

    def get_neighbors(self, node_id: str):
        return self.graph_service.get_neighbors(node_id)
