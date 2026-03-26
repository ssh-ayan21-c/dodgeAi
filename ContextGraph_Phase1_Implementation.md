# Context Graph System - Phase 1 Implementation Plan

## 1. Graph Data Model & Architectural Decisions

To ensure optimal performance and high compatibility with Text-to-Cypher Large Language Models, the schema uses plain English nouns for Nodes and clear, action-oriented verbs for Relationships. 

### Core Schema Mapping

**Nodes (Entities):**
*   **`Customer`**: `id`, `name`, `industry`
*   **`Address`**: `id`, `street`, `city`, `state`, `country`, `postal_code`
*   **`Order`** (Sales Order): `id`, `order_date`, `total_amount`, `status`
*   **`Delivery`**: `id`, `delivery_date`, `status`, `tracking_number`
*   **`Invoice`** (Billing Document): `id`, `invoice_date`, `amount`, `due_date`
*   **`Payment`**: `id`, `payment_date`, `amount`, `method`
*   **`PurchaseOrder`**: `id`, `po_date`, `amount`
*   **`JournalEntry`**: `id`, `entry_date`, `account`, `amount`, `type`
*   **`Product`**: `id`, `name`, `category`, `price`
*   **`Material`**: `id`, `name`, `type`
*   **`Plant`**: `id`, `name`, `location`

**Relationships (Edges):**
*   `(Customer)-[:LOCATED_AT]->(Address)`
*   `(Plant)-[:LOCATED_AT]->(Address)`
*   `(Customer)-[:SUBMITTED]->(PurchaseOrder)`
*   `(PurchaseOrder)-[:INITIATES]->(Order)`
*   `(Customer)-[:PLACED]->(Order)`
*   `(Order)-[:CONTAINS]->(Product)`
*   `(Product)-[:COMPOSED_OF]->(Material)`
*   `(Plant)-[:MANUFACTURES]->(Product)`
*   `(Order)-[:FULFILLED_BY]->(Delivery)` – Maps chronological fulfillment.
*   `(Delivery)-[:TRIGGERS]->(Invoice)` – Maps the billing workflow.
*   `(Invoice)-[:PAID_BY]->(Payment)` – Represents the settlement.
*   `(Invoice)-[:RECORDED_AS]->(JournalEntry)` – Maps operational data to financial ledgers.
*   `(Payment)-[:RECORDED_AS]->(JournalEntry)`

### Architectural Tradeoffs & Decisions

1.  **Addresses as Independent Nodes (vs. Properties)**
    *   *Tradeoff:* Increases schema complexity slightly, but greatly enhances querying.
    *   *Reasoning:* Multiple entities (Customers, Plants) can share the same regional hierarchies. Extracting `Address` allows geospatial aggregations (e.g., "Show me all deliveries to this ZIP code") and prevents data duplication (e.g., Billing vs. Shipping addresses).
2.  **Handling Broken or Incomplete Workflows**
    *   *Tradeoff:* By separating the standard entity transitions (`Order` -> `Delivery` -> `Invoice`) into discrete nodes rather than updating a single `Order` node's status, we use more nodes/edges.
    *   *Reasoning:* This inherently models broken flows visually and computationally. An LLM can easily find delivered but unbilled orders via: `MATCH (o:Order)-[:FULFILLED_BY]->(d:Delivery) WHERE NOT (d)-[:TRIGGERS]->(:Invoice) RETURN o`. Missing connections *are* the anomalies.
3.  **Semantic Naming Conventions**
    *   LLMs struggle with ERP-specific jargon (e.g., `VBAK`, `VBRP`). Using highly semantic, human-readable English verbs like `PLACED`, `FULFILLED_BY`, and `TRIGGERS` bridges the gap between natural language prompts and Cypher generation.

---

## 2. Database Constraints & Indexes

To prevent data duplication and ensure O(1) node lookups during high-volume ingestion, we must establish uniqueness constraints on the primary identifiers.

```cypher
// Uniqueness Constraints
CREATE CONSTRAINT customer_id IF NOT EXISTS FOR (c:Customer) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT address_id IF NOT EXISTS FOR (a:Address) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT material_id IF NOT EXISTS FOR (m:Material) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT plant_id IF NOT EXISTS FOR (pl:Plant) REQUIRE pl.id IS UNIQUE;
CREATE CONSTRAINT order_id IF NOT EXISTS FOR (o:Order) REQUIRE o.id IS UNIQUE;
CREATE CONSTRAINT delivery_id IF NOT EXISTS FOR (d:Delivery) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT invoice_id IF NOT EXISTS FOR (i:Invoice) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT payment_id IF NOT EXISTS FOR (pay:Payment) REQUIRE pay.id IS UNIQUE;
CREATE CONSTRAINT po_id IF NOT EXISTS FOR (po:PurchaseOrder) REQUIRE po.id IS UNIQUE;
CREATE CONSTRAINT je_id IF NOT EXISTS FOR (je:JournalEntry) REQUIRE je.id IS UNIQUE;

// Indexes for fast querying/filtering
CREATE INDEX order_date IF NOT EXISTS FOR (o:Order) ON (o.order_date);
CREATE INDEX customer_name IF NOT EXISTS FOR (c:Customer) ON (c.name);
CREATE INDEX product_category IF NOT EXISTS FOR (p:Product) ON (p.category);
```

---

## 3. LLM Readiness Checklist

This specific graph schema prevents hallucinations and optimally supports inference in the following ways:

*   [x] **Action-Oriented Verbs:** Edge names map directly to verbs users naturally type ("Which orders were *fulfilled by* yesterday's deliveries?").
*   [x] **Explicit Tracing:** Tracing complex flows like Order-to-Cash is possible without inferring internal app logic or complex JOINs. A Text-to-Cypher agent can safely emit linear path matches: `(o:Order)-[:FULFILLED_BY]->(:Delivery)-[:TRIGGERS]->(:Invoice)-[:RECORDED_AS]->(:JournalEntry)`.
*   [x] **Entity-Attribute Separation:** Abstract concepts are Nodes, while quantitative/descriptive data are Properties. This reduces schema bloat (e.g., avoiding an edge for `amount`, instead keeping it as an attribute to support SUM and AVG in Cypher).
*   [x] **Self-Describing Metadata:** The database graph can be introspected dynamically (`CALL db.schema.visualization()`). The output will be incredibly clean due to our semantic naming convention, ensuring the LLM understands the exact topology before writing queries.
