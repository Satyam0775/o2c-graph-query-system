ENTITY_TYPES = [
    "Customer",
    "SalesOrder",
    "SalesOrderItem",
    "Delivery",
    "BillingDocument",
    "JournalEntry",
    "Payment",
    "Product",
]

RELATIONSHIP_TYPES = {
    "PLACED": ("Customer", "SalesOrder"),
    "CONTAINS": ("SalesOrder", "SalesOrderItem"),
    "HAS_PRODUCT": ("SalesOrderItem", "Product"),
    "FULFILLED_BY": ("SalesOrder", "Delivery"),
    "BILLED_TO": ("Customer", "BillingDocument"),
    "RECORDED_IN": ("BillingDocument", "JournalEntry"),
    "SETTLED_BY": ("JournalEntry", "Payment"),
}

NODE_COLORS = {
    "Customer": "#3B82F6",
    "SalesOrder": "#10B981",
    "SalesOrderItem": "#6366F1",
    "Delivery": "#F59E0B",
    "BillingDocument": "#EF4444",
    "JournalEntry": "#8B5CF6",
    "Payment": "#14B8A6",
    "Product": "#F97316",
}

TABLE_SCHEMA = {
    "business_partners": {
        "description": "Customer/business partner master data",
        "key_columns": ["customer", "businessPartnerFullName", "businessPartnerCategory"],
    },
    "sales_order_headers": {
        "description": "Sales order header records",
        "key_columns": ["salesOrder", "soldToParty", "totalNetAmount", "overallDeliveryStatus", "creationDate"],
    },
    "sales_order_items": {
        "description": "Line items within sales orders",
        "key_columns": ["salesOrder", "salesOrderItem", "material", "requestedQuantity", "netAmount"],
    },
    "outbound_delivery_headers": {
        "description": "Outbound delivery/shipment headers",
        "key_columns": ["deliveryDocument", "overallGoodsMovementStatus", "overallPickingStatus", "creationDate"],
    },
    "billing_documents": {
        "description": "Billing document headers (invoices)",
        "key_columns": ["billingDocument", "soldToParty", "totalNetAmount", "billingDocumentType", "billingDocumentDate", "accountingDocument"],
    },
    "journal_entries": {
        "description": "Journal entry items for accounts receivable",
        "key_columns": ["accountingDocument", "referenceDocument", "customer", "amountInTransactionCurrency", "postingDate", "accountingDocumentType"],
    },
    "payments": {
        "description": "Payment records for accounts receivable",
        "key_columns": ["accountingDocument", "customer", "amountInTransactionCurrency", "clearingAccountingDocument", "postingDate"],
    },
    "products": {
        "description": "Product/material master data",
        "key_columns": ["material", "productDescription", "materialGroup"],
    },
}

GUARDRAIL_KEYWORDS = [
    "salesorder", "sales order", "billing", "invoice", "payment", "delivery",
    "customer", "product", "material", "journal", "accounting", "order",
    "amount", "currency", "date", "status", "document", "quantity",
    "revenue", "transaction", "shipment", "partner", "business"
]

OUT_OF_SCOPE_RESPONSE = (
    "This system is designed to answer questions related to the SAP Order-to-Cash dataset only. "
    "I can help with questions about sales orders, deliveries, billing documents, journal entries, "
    "payments, customers, and products. Please ask a question related to these topics."
)
