from app.utils.logger import get_logger

logger = get_logger(__name__)

# ❌ blocked dangerous keywords only
DANGEROUS_SQL = ["drop", "delete", "truncate", "update", "insert"]

# ❌ blocked unrelated topics
BLOCKED_PATTERNS = [
    "weather", "recipe", "movie", "music", "celebrity",
    "bitcoin", "sports", "politics", "how to code"
]


def is_relevant(question: str) -> bool:
    q = question.lower()

    # block unrelated queries
    for pattern in BLOCKED_PATTERNS:
        if pattern in q:
            return False

    return True


def is_sql_safe(sql: str) -> bool:
    sql_lower = sql.lower()

    # ❌ block only dangerous operations
    for keyword in DANGEROUS_SQL:
        if keyword in sql_lower:
            return False

    # ✅ allow SELECT, JOIN, WITH, etc.
    return True


def validate_query(question: str):
    """
    Returns (is_valid, error_message)
    """

    if not question or not question.strip():
        return False, "Please enter a question."

    if len(question.strip()) < 3:
        return False, "Question too short."

    if len(question) > 1000:
        return False, "Question too long."

    if not is_relevant(question):
        return False, "This question is outside the dataset scope."

    return True, ""