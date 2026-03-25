import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


class Settings:
    PROJECT_NAME: str = "O2C Graph Query System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # ✅ ONLY COHERE
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")

    # DATABASE
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR}/o2c_graph.db"
    )

    DATA_DIR: str = os.getenv(
        "DATA_DIR",
        str(BASE_DIR / "data")
    )

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    MAX_GRAPH_NODES: int = int(os.getenv("MAX_GRAPH_NODES", 500))
    MAX_SQL_RESULTS: int = int(os.getenv("MAX_SQL_RESULTS", 100))


settings = Settings()


# ✅ DEBUG (SAFE)
print("COHERE:", settings.COHERE_API_KEY[:10] if settings.COHERE_API_KEY else "NOT SET")