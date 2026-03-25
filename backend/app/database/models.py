from sqlalchemy import Column, String, Float, Boolean, Integer, Text
from app.database.db import Base


class BusinessPartner(Base):
    __tablename__ = "business_partners"
    customer = Column(String, primary_key=True)
    businessPartnerFullName = Column(String)
    businessPartnerCategory = Column(String)
    businessPartnerGrouping = Column(String)
    creationDate = Column(String)
    lastChangeDate = Column(String)
    businessPartnerIsBlocked = Column(Boolean, default=False)
    isMarkedForArchiving = Column(Boolean, default=False)
    createdByUser = Column(String)
    industry = Column(String)


class SalesOrderHeader(Base):
    __tablename__ = "sales_order_headers"
    salesOrder = Column(String, primary_key=True)
    salesOrderType = Column(String)
    salesOrganization = Column(String)
    distributionChannel = Column(String)
    soldToParty = Column(String)
    creationDate = Column(String)
    lastChangeDateTime = Column(String)
    totalNetAmount = Column(Float)
    overallDeliveryStatus = Column(String)
    overallOrdReltdBillgStatus = Column(String)
    transactionCurrency = Column(String)
    requestedDeliveryDate = Column(String)
    headerBillingBlockReason = Column(String)
    deliveryBlockReason = Column(String)
    customerPaymentTerms = Column(String)
    createdByUser = Column(String)
    incotermsClassification = Column(String)


class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    salesOrder = Column(String)
    salesOrderItem = Column(String)
    salesOrderItemCategory = Column(String)
    material = Column(String)
    requestedQuantity = Column(Float)
    requestedQuantityUnit = Column(String)
    transactionCurrency = Column(String)
    netAmount = Column(Float)
    materialGroup = Column(String)
    productionPlant = Column(String)
    storageLocation = Column(String)
    salesDocumentRjcnReason = Column(String)
    itemBillingBlockReason = Column(String)


class OutboundDeliveryHeader(Base):
    __tablename__ = "outbound_delivery_headers"
    deliveryDocument = Column(String, primary_key=True)
    creationDate = Column(String)
    deliveryBlockReason = Column(String)
    hdrGeneralIncompletionStatus = Column(String)
    headerBillingBlockReason = Column(String)
    lastChangeDate = Column(String)
    overallGoodsMovementStatus = Column(String)
    overallPickingStatus = Column(String)
    overallProofOfDeliveryStatus = Column(String)
    shippingPoint = Column(String)


class BillingDocument(Base):
    __tablename__ = "billing_documents"
    billingDocument = Column(String, primary_key=True)
    billingDocumentType = Column(String)
    creationDate = Column(String)
    billingDocumentDate = Column(String)
    billingDocumentIsCancelled = Column(Boolean, default=False)
    cancelledBillingDocument = Column(String)
    totalNetAmount = Column(Float)
    transactionCurrency = Column(String)
    companyCode = Column(String)
    fiscalYear = Column(String)
    accountingDocument = Column(String)
    soldToParty = Column(String)
    lastChangeDateTime = Column(String)


class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    companyCode = Column(String)
    fiscalYear = Column(String)
    accountingDocument = Column(String)
    glAccount = Column(String)
    referenceDocument = Column(String)
    costCenter = Column(String)
    profitCenter = Column(String)
    transactionCurrency = Column(String)
    amountInTransactionCurrency = Column(Float)
    companyCodeCurrency = Column(String)
    amountInCompanyCodeCurrency = Column(Float)
    postingDate = Column(String)
    documentDate = Column(String)
    accountingDocumentType = Column(String)
    accountingDocumentItem = Column(String)
    customer = Column(String)
    financialAccountType = Column(String)
    clearingDate = Column(String)
    clearingAccountingDocument = Column(String)


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    companyCode = Column(String)
    fiscalYear = Column(String)
    accountingDocument = Column(String)
    accountingDocumentItem = Column(String)
    clearingDate = Column(String)
    clearingAccountingDocument = Column(String)
    clearingDocFiscalYear = Column(String)
    amountInTransactionCurrency = Column(Float)
    transactionCurrency = Column(String)
    amountInCompanyCodeCurrency = Column(Float)
    companyCodeCurrency = Column(String)
    customer = Column(String)
    invoiceReference = Column(String)
    salesDocument = Column(String)
    postingDate = Column(String)
    documentDate = Column(String)
    glAccount = Column(String)
    profitCenter = Column(String)


class Product(Base):
    __tablename__ = "products"
    material = Column(String, primary_key=True)
    productDescription = Column(String)
    materialGroup = Column(String)
    language = Column(String)
