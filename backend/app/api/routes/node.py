from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.node_service import NodeService

router = APIRouter()


@router.get("/node/{node_id:path}")
def get_node(node_id: str, db: Session = Depends(get_db)):
    service = NodeService(db)
    node = service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    return node


@router.get("/node/{node_id:path}/neighbors")
def get_neighbors(node_id: str, db: Session = Depends(get_db)):
    service = NodeService(db)
    return {"neighbors": service.get_neighbors(node_id)}
