from typing import List, Dict, Any, Optional
from app.utils.helpers import safe_str
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _safe_float(val: Any) -> Optional[float]:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _safe_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ("true", "1", "yes")
    return bool(val)


def transform_business_partners(records: List[Dict]) -> List[Dict]:
    out = []
    seen = set()
    for r in records:
        cid = safe_str(r.get("customer") or r.get("businessPartner"))
        if not cid or cid in seen:
            continue
        seen.add(cid)
        out.append({
            "customer": cid,
            "businessPartnerFullName": safe_str(r.get("businessPartnerFullName")),
            "businessPartnerCategory": safe_str(r.get("businessPartnerCategory")),
            "businessPartnerGrouping": safe_str(r.get("businessPartnerGrouping")),
            "creationDate": safe_str(r.get("creationDate")),
            "lastChangeDate": safe_str(r.get("lastChangeDate")),
            "businessPartnerIsBlocked": _safe_bool(r.get("businessPartnerIsBlocked")),
            "isMarkedForArchiving": _safe_bool(r.get("isMarkedForArchiving")),
            "createdByUser": safe_str(r.get("createdByUser")),
            "industry": safe_str(r.get("industry")),
        })
    return out


def transform_sales_order_headers(records: List[Dict]) -> List[Dict]:
    out = []
    seen = set()
    for r in records:
        so = safe_str(r.get("salesOrder"))
        if not so or so in seen:
            continue
        seen.add(so)
        out.append({
            "salesOrder": so,
            "salesOrderType": safe_str(r.get("salesOrderType")),
            "salesOrganization": safe_str(r.get("salesOrganization")),
            "distributionChannel": safe_str(r.get("distributionChannel")),
            "soldToParty": safe_str(r.get("soldToParty")),
            "creationDate": safe_str(r.get("creationDate")),
            "lastChangeDateTime": safe_str(r.get("lastChangeDateTime")),
            "totalNetAmount": _safe_float(r.get("totalNetAmount")),
            "overallDeliveryStatus": safe_str(r.get("overallDeliveryStatus")),
            "overallOrdReltdBillgStatus": safe_str(r.get("overallOrdReltdBillgStatus")),
            "transactionCurrency": safe_str(r.get("transactionCurrency")),
            "requestedDeliveryDate": safe_str(r.get("requestedDeliveryDate")),
            "headerBillingBlockReason": safe_str(r.get("headerBillingBlockReason")),
            "deliveryBlockReason": safe_str(r.get("deliveryBlockReason")),
            "customerPaymentTerms": safe_str(r.get("customerPaymentTerms")),
            "createdByUser": safe_str(r.get("createdByUser")),
            "incotermsClassification": safe_str(r.get("incotermsClassification")),
        })
    return out


def transform_sales_order_items(records: List[Dict]) -> List[Dict]:
    out = []
    for r in records:
        so = safe_str(r.get("salesOrder"))
        soi = safe_str(r.get("salesOrderItem"))
        if not so or not soi:
            continue
        out.append({
            "salesOrder": so,
            "salesOrderItem": soi,
            "salesOrderItemCategory": safe_str(r.get("salesOrderItemCategory")),
            "material": safe_str(r.get("material")),
            "requestedQuantity": _safe_float(r.get("requestedQuantity")),
            "requestedQuantityUnit": safe_str(r.get("requestedQuantityUnit")),
            "transactionCurrency": safe_str(r.get("transactionCurrency")),
            "netAmount": _safe_float(r.get("netAmount")),
            "materialGroup": safe_str(r.get("materialGroup")),
            "productionPlant": safe_str(r.get("productionPlant")),
            "storageLocation": safe_str(r.get("storageLocation")),
            "salesDocumentRjcnReason": safe_str(r.get("salesDocumentRjcnReason")),
            "itemBillingBlockReason": safe_str(r.get("itemBillingBlockReason")),
        })
    return out


def transform_outbound_delivery_headers(records: List[Dict]) -> List[Dict]:
    out = []
    seen = set()
    for r in records:
        dd = safe_str(r.get("deliveryDocument"))
        if not dd or dd in seen:
            continue
        seen.add(dd)

        creation_time = r.get("creationTime", {})
        if isinstance(creation_time, dict):
            ct_str = f"{creation_time.get('hours',0):02d}:{creation_time.get('minutes',0):02d}"
        else:
            ct_str = ""

        out.append({
            "deliveryDocument": dd,
            "creationDate": safe_str(r.get("creationDate")),
            "deliveryBlockReason": safe_str(r.get("deliveryBlockReason")),
            "hdrGeneralIncompletionStatus": safe_str(r.get("hdrGeneralIncompletionStatus")),
            "headerBillingBlockReason": safe_str(r.get("headerBillingBlockReason")),
            "lastChangeDate": safe_str(r.get("lastChangeDate")),
            "overallGoodsMovementStatus": safe_str(r.get("overallGoodsMovementStatus")),
            "overallPickingStatus": safe_str(r.get("overallPickingStatus")),
            "overallProofOfDeliveryStatus": safe_str(r.get("overallProofOfDeliveryStatus")),
            "shippingPoint": safe_str(r.get("shippingPoint")),
        })
    return out


def transform_billing_documents(records: List[Dict]) -> List[Dict]:
    out = []
    seen = set()
    for r in records:
        bd = safe_str(r.get("billingDocument"))
        if not bd or bd in seen:
            continue
        seen.add(bd)
        out.append({
            "billingDocument": bd,
            "billingDocumentType": safe_str(r.get("billingDocumentType")),
            "creationDate": safe_str(r.get("creationDate")),
            "billingDocumentDate": safe_str(r.get("billingDocumentDate")),
            "billingDocumentIsCancelled": _safe_bool(r.get("billingDocumentIsCancelled")),
            "cancelledBillingDocument": safe_str(r.get("cancelledBillingDocument")),
            "totalNetAmount": _safe_float(r.get("totalNetAmount")),
            "transactionCurrency": safe_str(r.get("transactionCurrency")),
            "companyCode": safe_str(r.get("companyCode")),
            "fiscalYear": safe_str(r.get("fiscalYear")),
            "accountingDocument": safe_str(r.get("accountingDocument")),
            "soldToParty": safe_str(r.get("soldToParty")),
            "lastChangeDateTime": safe_str(r.get("lastChangeDateTime")),
        })
    return out


def transform_journal_entries(records: List[Dict]) -> List[Dict]:
    out = []
    for r in records:
        ad = safe_str(r.get("accountingDocument"))
        if not ad:
            continue
        out.append({
            "companyCode": safe_str(r.get("companyCode")),
            "fiscalYear": safe_str(r.get("fiscalYear")),
            "accountingDocument": ad,
            "glAccount": safe_str(r.get("glAccount")),
            "referenceDocument": safe_str(r.get("referenceDocument")),
            "costCenter": safe_str(r.get("costCenter")),
            "profitCenter": safe_str(r.get("profitCenter")),
            "transactionCurrency": safe_str(r.get("transactionCurrency")),
            "amountInTransactionCurrency": _safe_float(r.get("amountInTransactionCurrency")),
            "companyCodeCurrency": safe_str(r.get("companyCodeCurrency")),
            "amountInCompanyCodeCurrency": _safe_float(r.get("amountInCompanyCodeCurrency")),
            "postingDate": safe_str(r.get("postingDate")),
            "documentDate": safe_str(r.get("documentDate")),
            "accountingDocumentType": safe_str(r.get("accountingDocumentType")),
            "accountingDocumentItem": safe_str(r.get("accountingDocumentItem")),
            "customer": safe_str(r.get("customer")),
            "financialAccountType": safe_str(r.get("financialAccountType")),
            "clearingDate": safe_str(r.get("clearingDate")),
            "clearingAccountingDocument": safe_str(r.get("clearingAccountingDocument")),
        })
    return out


def transform_payments(records: List[Dict]) -> List[Dict]:
    out = []
    for r in records:
        ad = safe_str(r.get("accountingDocument"))
        if not ad:
            continue
        out.append({
            "companyCode": safe_str(r.get("companyCode")),
            "fiscalYear": safe_str(r.get("fiscalYear")),
            "accountingDocument": ad,
            "accountingDocumentItem": safe_str(r.get("accountingDocumentItem")),
            "clearingDate": safe_str(r.get("clearingDate")),
            "clearingAccountingDocument": safe_str(r.get("clearingAccountingDocument")),
            "clearingDocFiscalYear": safe_str(r.get("clearingDocFiscalYear")),
            "amountInTransactionCurrency": _safe_float(r.get("amountInTransactionCurrency")),
            "transactionCurrency": safe_str(r.get("transactionCurrency")),
            "amountInCompanyCodeCurrency": _safe_float(r.get("amountInCompanyCodeCurrency")),
            "companyCodeCurrency": safe_str(r.get("companyCodeCurrency")),
            "customer": safe_str(r.get("customer")),
            "invoiceReference": safe_str(r.get("invoiceReference")),
            "salesDocument": safe_str(r.get("salesDocument")),
            "postingDate": safe_str(r.get("postingDate")),
            "documentDate": safe_str(r.get("documentDate")),
            "glAccount": safe_str(r.get("glAccount")),
            "profitCenter": safe_str(r.get("profitCenter")),
        })
    return out


def transform_products(records: List[Dict]) -> List[Dict]:
    out = []
    seen = set()
    for r in records:
        mat = safe_str(r.get("product") or r.get("material"))
        if not mat or mat in seen:
            continue
        seen.add(mat)
        out.append({
            "material": mat,
            "productDescription": safe_str(r.get("productDescription")),
            "materialGroup": safe_str(r.get("materialGroup")),
            "language": safe_str(r.get("language")),
        })
    return out
