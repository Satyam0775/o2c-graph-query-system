from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class GraphNode:
    id: str
    entity_type: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_cytoscape(self) -> Dict:
        from app.core.constants import NODE_COLORS
        color = NODE_COLORS.get(self.entity_type, "#94A3B8")
        return {
            "data": {
                "id": self.id,
                "label": self.label,
                "entity_type": self.entity_type,
                "properties": self.properties,
                "color": color,
            }
        }


@dataclass
class GraphEdge:
    id: str
    source: str
    target: str
    relationship: str

    def to_cytoscape(self) -> Dict:
        return {
            "data": {
                "id": self.id,
                "source": self.source,
                "target": self.target,
                "label": self.relationship,
            }
        }
