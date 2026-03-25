import networkx as nx
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Tuple, List
from app.graph.graph_schema import GraphNode, GraphEdge
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_graph_cache: nx.DiGraph = None


def build_graph(session: Session) -> nx.DiGraph:
    global _graph_cache
    G = nx.DiGraph()
    node_limit = settings.MAX_GRAPH_NODES

    # --- CUSTOMERS ---
    rows = session.execute(text(
        "SELECT customer, businessPartnerFullName FROM business_partners LIMIT :lim"
    ), {"lim": node_limit // 8}).fetchall()
    for row in rows:
        nid = f"CUST_{row[0]}"
        G.add_node(nid, entity_type="Customer", label=row[1] or row[0],
                   properties={"customer": row[0], "name": row[1]})

    # --- SALES ORDERS ---
    rows = session.execute(text(
        "SELECT salesOrder, soldToParty, totalNetAmount, overallDeliveryStatus, transactionCurrency "
        "FROM sales_order_headers LIMIT :lim"
    ), {"lim": node_limit // 6}).fetchall()
    for row in rows:
        nid = f"SO_{row[0]}"
        G.add_node(nid, entity_type="SalesOrder", label=f"SO {row[0]}",
                   properties={
                       "salesOrder": row[0], "soldToParty": row[1],
                       "totalNetAmount": row[2], "deliveryStatus": row[3],
                       "currency": row[4]
                   })
        # Edge: Customer -> SalesOrder
        cust_nid = f"CUST_{row[1]}"
        if G.has_node(cust_nid):
            eid = f"PLACED_{row[1]}_{row[0]}"
            G.add_edge(cust_nid, nid, relationship="PLACED", id=eid)

    # --- PRODUCTS ---
    rows = session.execute(text(
        "SELECT material, productDescription, materialGroup FROM products LIMIT :lim"
    ), {"lim": node_limit // 8}).fetchall()
    for row in rows:
        nid = f"PROD_{row[0]}"
        G.add_node(nid, entity_type="Product", label=row[1] or row[0],
                   properties={"material": row[0], "description": row[1], "group": row[2]})

    # --- SALES ORDER ITEMS → Product ---
    rows = session.execute(text(
        "SELECT salesOrder, salesOrderItem, material, netAmount "
        "FROM sales_order_items LIMIT :lim"
    ), {"lim": node_limit // 4}).fetchall()
    for row in rows:
        so_nid = f"SO_{row[0]}"
        prod_nid = f"PROD_{row[2]}"
        if G.has_node(so_nid) and G.has_node(prod_nid):
            eid = f"HAS_{row[0]}_{row[1]}"
            if not G.has_edge(so_nid, prod_nid):
                G.add_edge(so_nid, prod_nid, relationship="HAS_PRODUCT", id=eid)

    # --- DELIVERIES ---
    rows = session.execute(text(
        "SELECT deliveryDocument, overallGoodsMovementStatus, overallPickingStatus "
        "FROM outbound_delivery_headers LIMIT :lim"
    ), {"lim": node_limit // 8}).fetchall()
    for row in rows:
        nid = f"DEL_{row[0]}"
        G.add_node(nid, entity_type="Delivery", label=f"DEL {row[0]}",
                   properties={"deliveryDocument": row[0], "goodsMovement": row[1], "picking": row[2]})

    # --- BILLING DOCUMENTS ---
    rows = session.execute(text(
        "SELECT billingDocument, soldToParty, totalNetAmount, billingDocumentType, "
        "billingDocumentIsCancelled, accountingDocument "
        "FROM billing_documents LIMIT :lim"
    ), {"lim": node_limit // 6}).fetchall()
    for row in rows:
        nid = f"BD_{row[0]}"
        G.add_node(nid, entity_type="BillingDocument", label=f"BD {row[0]}",
                   properties={
                       "billingDocument": row[0], "soldToParty": row[1],
                       "totalNetAmount": row[2], "type": row[3],
                       "isCancelled": bool(row[4]), "accountingDocument": row[5]
                   })
        # Edge: Customer -> BillingDocument
        cust_nid = f"CUST_{row[1]}"
        if G.has_node(cust_nid):
            eid = f"BILLED_{row[1]}_{row[0]}"
            G.add_edge(cust_nid, nid, relationship="BILLED_TO", id=eid)

    # --- JOURNAL ENTRIES ---
    rows = session.execute(text(
        "SELECT accountingDocument, referenceDocument, customer, "
        "amountInTransactionCurrency, postingDate, accountingDocumentType "
        "FROM journal_entries LIMIT :lim"
    ), {"lim": node_limit // 6}).fetchall()
    for row in rows:
        nid = f"JE_{row[0]}_{row[1]}"
        G.add_node(nid, entity_type="JournalEntry", label=f"JE {row[0]}",
                   properties={
                       "accountingDocument": row[0], "referenceDocument": row[1],
                       "customer": row[2], "amount": row[3],
                       "postingDate": row[4], "docType": row[5]
                   })
        # Edge: BillingDocument -> JournalEntry via referenceDocument
        bd_nid = f"BD_{row[1]}"
        if G.has_node(bd_nid):
            eid = f"RECORDED_{row[1]}_{row[0]}"
            G.add_edge(bd_nid, nid, relationship="RECORDED_IN", id=eid)

    # --- PAYMENTS ---
    rows = session.execute(text(
        "SELECT accountingDocument, customer, amountInTransactionCurrency, "
        "clearingAccountingDocument, postingDate "
        "FROM payments LIMIT :lim"
    ), {"lim": node_limit // 6}).fetchall()
    for row in rows:
        nid = f"PAY_{row[0]}"
        G.add_node(nid, entity_type="Payment", label=f"PAY {row[0]}",
                   properties={
                       "accountingDocument": row[0], "customer": row[1],
                       "amount": row[2], "clearingDoc": row[3], "postingDate": row[4]
                   })
        # Edge: JournalEntry -> Payment via clearingAccountingDocument
        for je_node in list(G.nodes):
            if G.nodes[je_node].get("entity_type") == "JournalEntry":
                props = G.nodes[je_node].get("properties", {})
                if props.get("accountingDocument") == row[3]:
                    eid = f"SETTLED_{row[3]}_{row[0]}"
                    G.add_edge(je_node, nid, relationship="SETTLED_BY", id=eid)
                    break

    _graph_cache = G
    logger.info(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def get_cached_graph() -> nx.DiGraph:
    return _graph_cache


def graph_to_cytoscape(G: nx.DiGraph) -> dict:
    from app.core.constants import NODE_COLORS
    nodes = []
    for nid, data in G.nodes(data=True):
        color = NODE_COLORS.get(data.get("entity_type", ""), "#94A3B8")
        degree = G.degree(nid)
        nodes.append({
            "data": {
                "id": nid,
                "label": data.get("label", nid),
                "entity_type": data.get("entity_type", "Unknown"),
                "properties": data.get("properties", {}),
                "color": color,
                "degree": degree,
            }
        })

    edges = []
    for src, tgt, data in G.edges(data=True):
        eid = data.get("id", f"{src}_{tgt}")
        edges.append({
            "data": {
                "id": eid,
                "source": src,
                "target": tgt,
                "label": data.get("relationship", ""),
            }
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
    }
