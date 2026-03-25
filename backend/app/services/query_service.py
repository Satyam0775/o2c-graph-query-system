import re
from typing import Dict, Any, List, Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.llm.query_generator import generate_sql, generate_answer
from app.guardrails.validator import validate_query
from app.utils.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

ALLOWED_TABLES = {
    "business_partners", "sales_order_headers", "sales_order_items",
    "outbound_delivery_headers", "billing_documents", "journal_entries",
    "payments", "products"
}


def _is_safe_sql(sql: str) -> bool:
    sql_upper = sql.upper().strip()
    # Only allow SELECT statements
    if not sql_upper.startswith("SELECT"):
        return False
    # Block dangerous keywords
    dangerous = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE",
                 "EXEC", "EXECUTE", "TRUNCATE", "PRAGMA", "--", ";--"]
    for d in dangerous:
        if d in sql_upper:
            return False
    return True


def _execute_sql(session: Session, sql: str) -> Tuple[List[Dict], int]:
    if not _is_safe_sql(sql):
        raise ValueError("Unsafe SQL detected")

    # Ensure LIMIT is present
    if "LIMIT" not in sql.upper():
        sql = sql.rstrip(";") + f" LIMIT {settings.MAX_SQL_RESULTS};"

    result = session.execute(text(sql))
    columns = list(result.keys())
    rows = result.fetchall()
    data = [dict(zip(columns, row)) for row in rows]
    return data, len(data)


def _extract_node_ids(results: List[Dict]) -> List[str]:
    """Extract graph node IDs from query results."""
    node_ids = []
    id_field_map = {
        "customer": "CUST_",
        "soldToParty": "CUST_",
        "salesOrder": "SO_",
        "deliveryDocument": "DEL_",
        "billingDocument": "BD_",
        "accountingDocument": "JE_",
        "material": "PROD_",
    }
    for row in results[:50]:
        for field, prefix in id_field_map.items():
            val = row.get(field)
            if val:
                node_ids.append(f"{prefix}{val}")
    return list(set(node_ids))


class QueryService:
    def __init__(self, session: Session):
        self.session = session

    def process_query(self, question: str) -> Dict[str, Any]:
        # Validate
        valid, rejection = validate_query(question)
        if not valid:
            return {
                "question": question,
                "sql": "",
                "results": [],
                "answer": rejection,
                "row_count": 0,
                "highlighted_nodes": [],
            }

        # Generate SQL
        try:
            sql = generate_sql(question)
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return {
                "question": question,
                "sql": "",
                "results": [],
                "answer": f"Failed to generate query: {str(e)}",
                "row_count": 0,
                "highlighted_nodes": [],
            }

        # Execute SQL
        try:
            results, row_count = _execute_sql(self.session, sql)
        except Exception as e:
            logger.error(f"SQL execution failed: {e}\nSQL: {sql}")
            # Try to fix and retry once
            try:
                fixed_sql = self._attempt_sql_fix(sql, str(e))
                if fixed_sql and fixed_sql != sql:
                    results, row_count = _execute_sql(self.session, fixed_sql)
                    sql = fixed_sql
                else:
                    raise
            except Exception as e2:
                return {
                    "question": question,
                    "sql": sql,
                    "results": [],
                    "answer": f"Query execution failed: {str(e2)}",
                    "row_count": 0,
                    "highlighted_nodes": [],
                }

        # Generate natural language answer
        try:
            answer = generate_answer(question, sql, results, row_count)
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            answer = f"Query returned {row_count} results."

        # Extract highlighted nodes
        highlighted_nodes = _extract_node_ids(results)

        return {
            "question": question,
            "sql": sql,
            "results": results,
            "answer": answer,
            "row_count": row_count,
            "highlighted_nodes": highlighted_nodes,
        }

    def _attempt_sql_fix(self, sql: str, error: str) -> str:
        """Attempt basic SQL fixes for common errors."""
        # Fix common column name issues
        fixes = {
            "billingDocumentHeaders": "billing_documents",
            "salesOrderHeaders": "sales_order_headers",
        }
        fixed = sql
        for wrong, right in fixes.items():
            fixed = fixed.replace(wrong, right)
        return fixed
