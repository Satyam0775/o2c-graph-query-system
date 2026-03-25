import json
import os
from pathlib import Path
from typing import List, Dict, Any
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def read_jsonl_folder(folder_path: str) -> List[Dict[str, Any]]:
    records = []
    folder = Path(folder_path)
    if not folder.exists():
        logger.warning(f"Folder not found: {folder_path}")
        return records
    for file in sorted(folder.glob("*.jsonl")):
        try:
            with open(file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Error reading {file}: {e}")
    logger.info(f"Loaded {len(records)} records from {folder_path}")
    return records


class DataLoader:
    def __init__(self):
        self.data_dir = Path(settings.DATA_DIR)

    def load_business_partners(self) -> List[Dict]:
        return read_jsonl_folder(self.data_dir / "business_partners")

    def load_sales_order_headers(self) -> List[Dict]:
        return read_jsonl_folder(self.data_dir / "sales_order_headers")

    def load_sales_order_items(self) -> List[Dict]:
        return read_jsonl_folder(self.data_dir / "sales_order_items")

    def load_outbound_delivery_headers(self) -> List[Dict]:
        return read_jsonl_folder(self.data_dir / "outbound_delivery_headers")

    def load_billing_documents(self) -> List[Dict]:
        return read_jsonl_folder(self.data_dir / "billing_document_cancellations")

    def load_journal_entries(self) -> List[Dict]:
        return read_jsonl_folder(self.data_dir / "journal_entry_items_accounts_receivable")

    def load_payments(self) -> List[Dict]:
        return read_jsonl_folder(self.data_dir / "payments_accounts_receivable")

    def load_product_descriptions(self) -> List[Dict]:
        return read_jsonl_folder(self.data_dir / "product_descriptions")

    def load_all(self) -> Dict[str, List[Dict]]:
        return {
            "business_partners": self.load_business_partners(),
            "sales_order_headers": self.load_sales_order_headers(),
            "sales_order_items": self.load_sales_order_items(),
            "outbound_delivery_headers": self.load_outbound_delivery_headers(),
            "billing_documents": self.load_billing_documents(),
            "journal_entries": self.load_journal_entries(),
            "payments": self.load_payments(),
            "product_descriptions": self.load_product_descriptions(),
        }
