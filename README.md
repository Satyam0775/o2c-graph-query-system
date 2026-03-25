# O2C Graph Query System

A graph-based data modeling and natural language query system for SAP Order-to-Cash (O2C) process data. Structured business records — orders, deliveries, invoices, and payments — are loaded into a relational database, mapped to a graph, and made queryable through a conversational interface powered by an LLM.

---

## Features

- **Graph Visualization** — Interactive Cytoscape.js graph with node filtering, zoom, and metadata inspection
- **Natural Language Queries** — Plain English questions are converted to SQL by an LLM and executed against live data
- **Data-Backed Responses** — The LLM generates answers only from actual query results; no hallucination
- **Guardrails** — Out-of-scope queries are detected and rejected before reaching the LLM
- **Node Highlighting** — Query results are reflected on the graph by highlighting matched nodes
- **LLM Fallback** — Automatic fallback to a secondary LLM provider if the primary request fails

---

## Tech Stack

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Backend    | Python 3.10, FastAPI, SQLAlchemy, SQLite        |
| Data       | Pandas (ingestion), NetworkX (graph model)      |
| LLM        | Cohere API (primary), secondary fallback        |
| Frontend   | React 18, Vite, Cytoscape.js (fcose layout)     |
| HTTP       | Axios                                           |

---

## Project Structure

```
graph-query-system/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # FastAPI route handlers
│   │   ├── core/             # Config, constants
│   │   ├── database/         # SQLAlchemy models, schema definitions, DB setup
│   │   ├── graph/            # NetworkX graph builder and service layer
│   │   ├── guardrails/       # Query relevance validator
│   │   ├── ingestion/        # Data loader, transformer, mapper (JSONL → SQLite)
│   │   ├── llm/              # LLM client, prompt templates
│   │   ├── services/         # Business logic (query execution, node lookup)
│   │   └── utils/            # Logger, helpers
│   ├── data/                 # SAP O2C JSONL source files
│   ├── main.py               # FastAPI application entry point
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/       # GraphView, ChatPanel, NodeDetails
│   │   ├── pages/            # Home page layout
│   │   └── services/api.js   # Axios API calls
│   ├── package.json
│   └── vite.config.js
└── docs/
    └── architecture.md
```

---

## How It Works

### End-to-End Query Flow

```
User types a question
        │
        ▼
Guardrail check
  ├── Rejected → "Out of scope" message returned
  └── Accepted
        │
        ▼
LLM (SQL Generation)
  Prompt includes: schema, column types, FK relationships, domain context
        │
        ▼
SQL executed on SQLite (SELECT only)
        │
        ▼
LLM (Answer Generation)
  Prompt includes: original question + raw query results (up to 20 rows)
        │
        ▼
Response returned to UI
  ├── Natural language answer
  └── Node IDs highlighted on the graph
```

### Data Ingestion

Source data is in JSONL format across 13 domain folders. On startup, the backend:

1. Loads JSONL files via `DataLoader`
2. Normalises and deduplicates records via transformer functions
3. Writes to 8 SQLite tables via `Mapper`
4. Builds a NetworkX directed graph cached in memory via `GraphBuilder`

---

## Database Choice

SQLite was chosen for its simplicity and zero-configuration setup. The dataset is read-heavy (no concurrent writes), fits comfortably in a single file, and does not require a running database process. SQLAlchemy provides a clean ORM layer if a migration to PostgreSQL is needed later.

---

## LLM Prompting Strategy

**SQL Generation prompt** includes:
- All 8 table schemas with column names, types, and nullability
- Foreign key relationships between tables
- Domain-specific context (e.g. what constitutes an "incomplete order" in SAP terminology)
- Explicit instruction to return only a valid `SELECT` statement

**Answer Generation prompt** includes:
- The user's original question
- The raw result rows from the SQL query (capped at 20 rows)
- Instruction to answer only from the provided data, not from general knowledge

This two-step approach ensures the LLM never constructs an answer without grounding it in real data.

---

## Guardrails

Queries pass through two validation layers before any LLM call is made:

**Layer 1 — Keyword filter (no API call)**
- Blocklist: topics unrelated to O2C (e.g. weather, recipes, general coding)
- Allowlist: known O2C domain terms (billing, order, payment, delivery, customer, etc.)

**Layer 2 — LLM classifier (for ambiguous cases)**
- A lightweight classification prompt returns `RELEVANT` or `IRRELEVANT`
- Only invoked when Layer 1 is inconclusive

**SQL safety:**
- Only `SELECT` statements are permitted
- A keyword blocklist (`DROP`, `DELETE`, `INSERT`, `UPDATE`, `TRUNCATE`, etc.) is enforced before any query reaches the database

---

## Graph Model

Nodes represent business entities. Edges represent process relationships.

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

| Entity          | Color   | Shape        |
|-----------------|---------|--------------|
| Customer        | #3B82F6 | Circle       |
| SalesOrder      | #10B981 | Rounded Rect |
| Product         | #F97316 | Star         |
| SalesOrderItem  | #6366F1 | Rounded Rect |
| Delivery        | #F59E0B | Tag          |
| BillingDocument | #EF4444 | Diamond      |
| JournalEntry    | #8B5CF6 | Pentagon     |
| Payment         | #14B8A6 | Hexagon      |

---

## API Reference

| Method | Endpoint          | Description                            |
|--------|-------------------|----------------------------------------|
| GET    | `/api/health`     | Server and data load status check      |
| POST   | `/api/load-data`  | Load or reload JSONL dataset to SQLite |
| GET    | `/api/graph`      | Full graph (nodes + edges) for the UI  |
| GET    | `/api/node/{id}`  | Single node details and neighbour list |
| POST   | `/api/query`      | Natural language → SQL → answer        |

---

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Cohere API key

### 1. Backend

```bash
cd graph-query-system/backend

python3.10 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Open .env and add your COHERE_API_KEY

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The dataset is loaded automatically on first startup. Progress is logged to the terminal.  
API docs available at: http://localhost:8000/docs

### 2. Frontend

```bash
cd graph-query-system/frontend

npm install
npm run dev
```

Open http://localhost:3000 in your browser.

### 3. First Use

1. Wait for the backend terminal to confirm data load completion.
2. If needed, click **▶ Load Data** in the UI to trigger loading manually.
3. The graph renders automatically once data is available.
4. Click any node to view its properties and connections.
5. Use the chat panel to ask natural language questions.

---

## Environment Variables

| Variable         | Required | Description                                    |
|------------------|----------|------------------------------------------------|
| `COHERE_API_KEY` | Yes      | Cohere API key (primary LLM)                   |
| `DATABASE_URL`   | No       | SQLite file path (default: `./o2c_graph.db`)   |
| `DATA_DIR`       | No       | Path to JSONL data folder                      |
| `LOG_LEVEL`      | No       | `INFO` / `DEBUG` / `WARNING` (default: `INFO`) |

---

## Example Queries

```
Which products are associated with the highest number of billing documents?
Trace the full flow for billing document 90504274.
Find sales orders where delivery or billing is blocked.
Which customers have made the highest total payments?
Show all journal entries linked to customer 320000083.
List the top 10 customers by total order value.
How many sales orders have an incomplete delivery status?
```
