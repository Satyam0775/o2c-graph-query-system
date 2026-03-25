import networkx as nx
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, List, Optional
from app.graph.graph_builder import build_graph, get_cached_graph, graph_to_cytoscape
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GraphService:
    def __init__(self, session: Session):
        self.session = session

    def get_or_build_graph(self) -> nx.DiGraph:
        G = get_cached_graph()
        if G is None:
            G = build_graph(self.session)
        return G

    def get_graph_data(self) -> Dict:
        G = self.get_or_build_graph()
        return graph_to_cytoscape(G)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        G = self.get_or_build_graph()
        if not G.has_node(node_id):
            return None
        data = G.nodes[node_id]
        neighbors = list(G.predecessors(node_id)) + list(G.successors(node_id))
        return {
            "id": node_id,
            "entity_type": data.get("entity_type", "Unknown"),
            "label": data.get("label", node_id),
            "properties": data.get("properties", {}),
            "connections": len(neighbors),
            "neighbors": neighbors,
        }

    def get_neighbors(self, node_id: str) -> List[Dict]:
        G = self.get_or_build_graph()
        if not G.has_node(node_id):
            return []
        from app.core.constants import NODE_COLORS
        result = []
        for n in list(G.predecessors(node_id)) + list(G.successors(node_id)):
            ndata = G.nodes[n]
            color = NODE_COLORS.get(ndata.get("entity_type", ""), "#94A3B8")
            result.append({
                "data": {
                    "id": n,
                    "label": ndata.get("label", n),
                    "entity_type": ndata.get("entity_type", "Unknown"),
                    "color": color,
                    "properties": ndata.get("properties", {}),
                }
            })
        return result

    def highlight_nodes(self, node_ids: List[str]) -> List[str]:
        G = self.get_or_build_graph()
        return [nid for nid in node_ids if G.has_node(nid)]

    def rebuild_graph(self) -> Dict:
        G = build_graph(self.session)
        return graph_to_cytoscape(G)
