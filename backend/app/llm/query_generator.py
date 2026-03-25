from app.llm.prompt_templates import (
    SQL_GENERATION_PROMPT,
    ANSWER_GENERATION_PROMPT,
    GUARDRAIL_PROMPT,
)
from app.utils.helpers import clean_sql
from app.utils.logger import get_logger
from app.core.config import settings
import json

logger = get_logger(__name__)


# 🔥 FINAL: ONLY COHERE (FREE & STABLE)
def _call_llm(prompt: str, temperature: float = 0.0, max_tokens: int = 512) -> str:
    if settings.COHERE_API_KEY:
        try:
            from app.llm.cohere_client import CohereClient

            logger.info("Using COHERE")
            return CohereClient().complete(prompt)

        except Exception as e:
            logger.error(f"Cohere failed: {e}")

    raise RuntimeError("Cohere not working. Check API key.")


# 🔹 GUARDRAIL
def check_relevance(question: str) -> bool:
    try:
        prompt = GUARDRAIL_PROMPT.format(question=question)
        result = _call_llm(prompt, temperature=0.0, max_tokens=10)

        return "RELEVANT" in result.upper()

    except Exception as e:
        logger.warning(f"Guardrail check failed: {e}")
        return None


# 🔹 SQL GENERATION
def generate_sql(question: str) -> str:
    prompt = SQL_GENERATION_PROMPT.format(question=question)

    raw = _call_llm(prompt, temperature=0.0, max_tokens=512)

    sql = clean_sql(raw)
    logger.info(f"Generated SQL: {sql[:200]}...")

    return sql


# 🔹 FINAL ANSWER GENERATION
def generate_answer(question: str, sql: str, results: list, row_count: int) -> str:
    results_str = json.dumps(results[:20], indent=2) if results else "No results found"

    prompt = ANSWER_GENERATION_PROMPT.format(
        question=question,
        sql=sql,
        row_count=row_count,
        results=results_str,
    )

    return _call_llm(prompt, temperature=0.1, max_tokens=512)