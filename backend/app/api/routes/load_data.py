from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.schemas import LoadDataResponse
from app.ingestion.loader import DataLoader
from app.ingestion.mapper import load_all_data
from app.graph.graph_builder import build_graph
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/load-data", response_model=LoadDataResponse)
def load_data(db: Session = Depends(get_db)):
    try:
        logger.info("Starting data ingestion...")
        loader = DataLoader()
        raw_data = loader.load_all()

        counts = load_all_data(db, raw_data)

        # Rebuild graph after loading
        logger.info("Rebuilding graph...")
        build_graph(db)

        return LoadDataResponse(
            status="success",
            tables_loaded=list(counts.keys()),
            row_counts=counts,
        )
    except Exception as e:
        logger.error(f"Data loading failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
