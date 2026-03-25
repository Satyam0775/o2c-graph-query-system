from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.db import get_db
from app.database.schemas import HealthResponse
from app.core.config import settings

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT COUNT(*) FROM sales_order_headers")).fetchone()
        data_loaded = result[0] > 0
        db_status = "connected"
    except Exception:
        data_loaded = False
        db_status = "error"

    return HealthResponse(
        status="ok",
        version=settings.VERSION,
        database=db_status,
        data_loaded=data_loaded,
    )