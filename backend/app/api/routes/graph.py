from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.graph.graph_service import GraphService
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/graph")
def get_graph(db: Session = Depends(get_db)):
    try:
        service = GraphService(db)
        return service.get_graph_data()
    except Exception as e:
        logger.error(f"Graph fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/graph/rebuild")
def rebuild_graph(db: Session = Depends(get_db)):
    try:
        service = GraphService(db)
        return service.rebuild_graph()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
