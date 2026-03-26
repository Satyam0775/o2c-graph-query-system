from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.router import api_router
from app.database.db import engine, Base
from app.database import models  # required
from app.utils.logger import get_logger

logger = get_logger(__name__)


# =========================
# 🚀 STARTUP LOGIC
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting O2C Graph Query System...")

    # Create DB tables
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created.")

    try:
        from sqlalchemy.orm import Session
        from app.database.db import SessionLocal
        from sqlalchemy import text

        db: Session = SessionLocal()

        try:
            count = db.execute(
                text("SELECT COUNT(*) FROM sales_order_headers")
            ).fetchone()[0]

            if count == 0:
                logger.info("📦 No data found, auto-loading dataset...")

                from app.ingestion.loader import DataLoader
                from app.ingestion.mapper import load_all_data
                from app.graph.graph_builder import build_graph

                loader = DataLoader()
                raw = loader.load_all()

                load_all_data(db, raw)
                build_graph(db)

                logger.info("✅ Dataset auto-loaded successfully.")

            else:
                logger.info(f"📊 Dataset already exists ({count}), rebuilding graph...")

                from app.graph.graph_builder import build_graph
                build_graph(db)

        finally:
            db.close()

    except Exception as e:
        logger.error(f"❌ Startup error: {e}", exc_info=True)

    yield
    logger.info("🛑 Shutting down...")


# =========================
# 🚀 FASTAPI APP
# =========================
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# =========================
# 🌐 CORS (IMPORTANT FOR VERCEL)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all (safe for assignment)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 🔗 ROUTES (/api PREFIX)
# =========================
app.include_router(api_router, prefix=settings.API_PREFIX)


# =========================
# 🏠 ROOT CHECK
# =========================
@app.get("/")
def root():
    return {
        "message": "O2C Graph Query System",
        "version": settings.VERSION,
        "docs": "/docs",
    }
