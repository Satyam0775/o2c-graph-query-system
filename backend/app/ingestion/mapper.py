from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
from app.database.models import (
    BusinessPartner, SalesOrderHeader, SalesOrderItem,
    OutboundDeliveryHeader, BillingDocument, JournalEntry, Payment, Product
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


def bulk_insert(session: Session, model, records: List[Dict], batch_size: int = 500):
    if not records:
        return 0
    total = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        session.bulk_insert_mappings(model, batch)
        session.flush()
        total += len(batch)
    session.commit()
    logger.info(f"Inserted {total} records into {model.__tablename__}")
    return total


def load_all_data(session: Session, data: Dict[str, List[Dict]]) -> Dict[str, int]:
    from app.ingestion.transformer import (
        transform_business_partners, transform_sales_order_headers,
        transform_sales_order_items, transform_outbound_delivery_headers,
        transform_billing_documents, transform_journal_entries,
        transform_payments, transform_products
    )

    counts = {}

    # Clear existing
    for model in [BusinessPartner, SalesOrderHeader, SalesOrderItem,
                  OutboundDeliveryHeader, BillingDocument, JournalEntry, Payment, Product]:
        session.execute(text(f"DELETE FROM {model.__tablename__}"))
    session.commit()

    counts["business_partners"] = bulk_insert(
        session, BusinessPartner,
        transform_business_partners(data.get("business_partners", []))
    )
    counts["sales_order_headers"] = bulk_insert(
        session, SalesOrderHeader,
        transform_sales_order_headers(data.get("sales_order_headers", []))
    )
    counts["sales_order_items"] = bulk_insert(
        session, SalesOrderItem,
        transform_sales_order_items(data.get("sales_order_items", []))
    )
    counts["outbound_delivery_headers"] = bulk_insert(
        session, OutboundDeliveryHeader,
        transform_outbound_delivery_headers(data.get("outbound_delivery_headers", []))
    )
    counts["billing_documents"] = bulk_insert(
        session, BillingDocument,
        transform_billing_documents(data.get("billing_documents", []))
    )
    counts["journal_entries"] = bulk_insert(
        session, JournalEntry,
        transform_journal_entries(data.get("journal_entries", []))
    )
    counts["payments"] = bulk_insert(
        session, Payment,
        transform_payments(data.get("payments", []))
    )

    # Products from descriptions
    prod_records = data.get("product_descriptions", [])
    # Also gather from sales_order_items materials
    from app.ingestion.transformer import transform_products
    all_prod = transform_products(prod_records)
    # Supplement with materials from sales order items
    existing_mats = {p["material"] for p in all_prod}
    for item in data.get("sales_order_items", []):
        mat = str(item.get("material", "")).strip()
        if mat and mat not in existing_mats:
            all_prod.append({
                "material": mat,
                "productDescription": "",
                "materialGroup": str(item.get("materialGroup", "")),
                "language": "",
            })
            existing_mats.add(mat)

    counts["products"] = bulk_insert(session, Product, all_prod)

    return counts
