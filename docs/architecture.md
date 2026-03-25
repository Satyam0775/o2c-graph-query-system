# Architecture — O2C Graph Query System

## 1. System Overview

The O2C Graph Query System converts structured SAP Order-to-Cash data into a queryable graph. Users can explore the data visually through a graph interface and ask natural language questions through a chat panel. Questions are translated to SQL by an LLM, executed against a SQLite database, and the results are interpreted into a plain-English response.

The system is split into two independently running services:

- **Backend** — FastAPI server handling data ingestion, query processing, and graph construction
- **Frontend** — React application rendering the graph (Cytoscape.js) and chat interface

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Frontend (React)                           │
│                                                                     │
│   ┌─────────────────────────┐     ┌───────────────────────────┐    │
│   │     Graph View          │     │       Chat Panel          │    │
│   │   (Cytoscape.js)        │     │  (Natural Language Input) │    │
│   └──────────┬──────────────┘     └─────────────┬─────────────┘    │
│              │ GET /api/graph                    │ POST /api/query  │
│              │ GET /api/node/{id}                │                  │
└──────────────┼───────────────────────────────────┼──────────────────┘
               │                                   │
               ▼                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Backend (FastAPI)                           │
│                                                                     │
│   ┌─────────────┐   ┌───────────────────────────────────────────┐  │
│   │ Graph Route │   │              Query Route                  │  │
│   │             │   │                                           │  │
│   │ GraphService│   │  ┌──────────────┐   ┌──────────────────┐ │  │
│   │ (NetworkX)  │   │  │  Guardrails  │   │  Query Service   │ │  │
│   └─────────────┘   │  │  (2 layers)  │──▶│                  │ │  │
│                     │  └──────────────┘   │  ┌────────────┐  │ │  │
│                     │                     │  │  LLM       │  │ │  │
│                     │                     │  │  (Cohere)  │  │ │  │
│                     │                     │  └─────┬──────┘  │ │  │
│                     │                     │        │ SQL      │ │  │
│                     │                     │  ┌─────▼──────┐  │ │  │
│                     │                     │  │  SQLite    │  │ │  │
│                     │                     │  │ (SQLAlch.) │  │ │  │
│                     │                     │  └─────┬──────┘  │ │  │
│                     │                     │        │ rows     │ │  │
│                     │                     │  ┌─────▼──────┐  │ │  │
│                     │                     │  │  LLM       │  │ │  │
│                     │                     │  │  (Answer)  │  │ │  │
│                     │                     │  └────────────┘  │ │  │
│                     │                     └──────────────────┘ │  │
│                     └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────┐
│     SQLite Database         │
│  (8 tables, loaded on boot) │
└─────────────────────────────┘
```

---

## 3. Backend Components

### API Routes (`app/api/routes/`)

| Route                | Method | Purpose                                         |
|----------------------|--------|-------------------------------------------------|
| `/api/health`        | GET    | Returns server status and data load state       |
| `/api/load-data`     | POST   | Triggers JSONL ingestion into SQLite            |
| `/api/graph`         | GET    | Returns all nodes and edges for the UI          |
| `/api/node/{id}`     | GET    | Returns a single node's properties and neighbours |
| `/api/query`         | POST   | Handles end-to-end NL → SQL → answer flow       |

### Query Service (`app/services/`)

Orchestrates the full query pipeline:

1. Receives the natural language question from the route handler
2. Passes it through the guardrail validator
3. Sends the validated question to the LLM for SQL generation
4. Executes the generated SQL against SQLite via SQLAlchemy
5. Sends the question and result rows to the LLM for answer generation
6. Returns the response and any matched node IDs to the frontend

### LLM Module (`app/llm/`)

Contains:
- **Client wrapper** — handles Cohere API calls and fallback logic
- **Prompt templates** — separate templates for SQL generation and answer generation
- **Response parser** — extracts the SQL statement or answer text from LLM output

### Graph Module (`app/graph/`)

- `GraphBuilder` constructs a NetworkX `DiGraph` from the SQLite tables on first load
- The graph is cached in memory and served via `GraphService`
- Nodes carry entity type, label, and property metadata; edges carry relationship type

### Ingestion Module (`app/ingestion/`)

- `DataLoader` reads JSONL files from the `data/` directory
- Transformer functions normalise field names, cast types, and deduplicate records
- `Mapper` writes normalised records to the appropriate SQLite table

---

## 4. Query Flow — Step by Step

```
User submits question: "Which customers have unpaid invoices?"
        │
        ▼
┌─────────────────────────────────────────────────┐
│  Layer 1 Guardrail — Keyword Filter             │
│  Checks against O2C allowlist and blocklist     │
│  Fast, no API call                              │
│  Result: RELEVANT / IRRELEVANT / AMBIGUOUS      │
└─────────────┬───────────────────────────────────┘
              │ If AMBIGUOUS
              ▼
┌─────────────────────────────────────────────────┐
│  Layer 2 Guardrail — LLM Classifier             │
│  Sends question to LLM with classification      │
│  prompt. Returns RELEVANT or IRRELEVANT.        │
└─────────────┬───────────────────────────────────┘
              │ If IRRELEVANT → return rejection message
              │ If RELEVANT ↓
              ▼
┌─────────────────────────────────────────────────┐
│  LLM: SQL Generation                           │
│  Prompt: schema + FK map + domain context      │
│  + question                                    │
│  Output: SELECT statement                      │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│  SQL Safety Check                              │
│  Rejects any non-SELECT or dangerous keyword   │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│  SQLite Execution (via SQLAlchemy)             │
│  Returns result rows (max 20 for LLM context)  │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│  LLM: Answer Generation                        │
│  Prompt: original question + result rows       │
│  Output: plain English answer                  │
└─────────────┬───────────────────────────────────┘
              │
              ▼
     Response returned to UI:
       - answer (string)
       - highlighted_node_ids (list)
```

---

## 5. Data Ingestion Pipeline

```
JSONL files (13 domain folders in data/)
        │
        ▼
DataLoader.load_all()
  Reads files, parses line-by-line
        │
        ▼
Transformer functions
  - Normalise field names to snake_case
  - Cast data types (dates, decimals, booleans)
  - Deduplicate on primary key
        │
        ▼
Mapper.load_all_data()
  Writes records to 8 SQLite tables:
  customers, sales_orders, sales_order_items,
  products, deliveries, billing_documents,
  journal_entries, payments
        │
        ▼
GraphBuilder.build_graph()
  Reads all 8 tables
  Constructs NetworkX DiGraph
  Nodes = entity records
  Edges = FK-driven relationships
  Cached in memory for the lifetime of the process
```

---

## 6. LLM Integration

### SQL Generation

The prompt sent to the LLM for SQL generation includes:

- All 8 table schemas (table name, column names, types, nullability)
- Foreign key relationships (e.g. `sales_orders.customer_id → customers.id`)
- Domain-specific business context (e.g. SAP delivery status codes, blocking flags)
- Instruction to return only a valid, single `SELECT` statement with no explanation

### Answer Generation

After SQL execution, a second prompt is sent containing:

- The user's original question (verbatim)
- The query result rows (formatted, capped at 20 rows)
- Instruction to answer using only the provided data and to acknowledge if the data is insufficient

This two-step design ensures the LLM cannot fabricate data — it can only interpret what the database returned.

### Fallback

If the primary LLM call fails (timeout, rate limit, or error), the system automatically retries using a configured secondary provider before returning an error to the user.

---

## 7. Guardrails Design

Two layers protect the system from off-topic or unsafe queries.

### Layer 1 — Keyword Filter

A fast, synchronous check with no external API call:

- **Blocklist** — terms from unrelated domains (weather, sports, recipes, general coding, etc.)
- **Allowlist** — known O2C terms (invoice, payment, delivery, customer, order, billing, journal, etc.)

If the question contains only blocklist terms → `IRRELEVANT`  
If the question contains allowlist terms → `RELEVANT`  
If neither → `AMBIGUOUS` → escalated to Layer 2

### Layer 2 — LLM Classifier

A minimal classification prompt asks the LLM:

```
Is the following question related to an SAP Order-to-Cash dataset?
Question: <user question>
Reply with one word: RELEVANT or IRRELEVANT.
```

Result determines whether the query proceeds or a rejection message is returned.

### SQL Safety

Before any generated SQL is executed:

- The statement must begin with `SELECT`
- A keyword blocklist is checked: `DROP`, `DELETE`, `INSERT`, `UPDATE`, `TRUNCATE`, `ALTER`, `CREATE`, `EXEC`, `--`
- Any match → query is rejected and an error is returned to the UI

---

## 8. Graph Model

Nodes represent individual business entity records. Edges represent directed process relationships derived from foreign keys and domain logic.

```
Customer ──PLACED──→ SalesOrder ──HAS_PRODUCT──→ Product
                          │
                    FULFILLED_BY
                          ▼
                      Delivery
                          │
                      BILLED_TO
                          ▼
                   BillingDocument ──RECORDED_IN──→ JournalEntry ──SETTLED_BY──→ Payment
```

### Node Types

| Entity          | Source Table        | Key Relationships                        |
|-----------------|---------------------|------------------------------------------|
| Customer        | `customers`         | Places SalesOrders                       |
| SalesOrder      | `sales_orders`      | Has Items, fulfilled by Delivery         |
| SalesOrderItem  | `sales_order_items` | Links SalesOrder to Product              |
| Product         | `products`          | Referenced by SalesOrderItems            |
| Delivery        | `deliveries`        | Fulfils SalesOrder, triggers Billing     |
| BillingDocument | `billing_documents` | Billed from Delivery, recorded in Journal|
| JournalEntry    | `journal_entries`   | Settled by Payment                       |
| Payment         | `payments`          | Settles JournalEntry                     |

---

## 9. Frontend Interaction

The frontend communicates with the backend over HTTP via Axios. There is no WebSocket or persistent connection.

### Graph View (`GraphView.jsx`)

- Loads the full graph on mount via `GET /api/graph`
- Renders nodes and edges using Cytoscape.js with the `fcose` layout
- Supports per-entity-type filtering, zoom, and fit controls
- On node click, fetches details via `GET /api/node/{id}` and displays a side panel
- Accepts a `highlightedNodes` prop from the chat panel to visually mark query results

### Chat Panel (`ChatPanel.jsx`)

- Sends questions to `POST /api/query`
- Displays the natural language answer returned by the backend
- Passes returned `highlighted_node_ids` up to the parent, which forwards them to `GraphView`

### Node Details Panel (`NodeDetails.jsx`)

- Displays entity type, label, and all stored properties for the selected node
- Lists direct neighbours with clickable links that trigger selection in the graph
