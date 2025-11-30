Day 9 — E-commerce Agent (Agentic Commerce Protocol — Lite)

A voice-driven shopping assistant inspired by a slimmed-down Agentic Commerce Protocol (ACP).
The agent interprets spoken shopping intent, calls a small merchant layer (Python functions) to browse a catalog and create orders, and persists orders to JSON. Built on the same realtime stack (LiveKit, STT, LLM, TTS) used in prior days.

TL;DR — What this repo does

Loads a small product catalog (JSON).

Lets users explore products by voice (filters: category, max_price, color, etc.).

Lets users place orders by voice; the agent calls create_order() which persists orders to JSON.

Keeps per-session order state in ctx.userdata.

Provides LLM-callable tools (list_products_tool, create_order_tool, get_last_order_tool) so the LLM drives the flow by calling functions (not embedding commerce logic in prompts).

Stores orders in shared-data/day9_orders.json (or per-order files, whichever you prefer).

Why ACP-inspired?

ACP is an architecture pattern for separating conversation (LLM/voice) from commerce logic (catalog/order APIs). This project borrows that separation: the LLM asks the agent to call merchant functions; the merchant layer (Python) is authoritative for product lookup and order creation.

Files & important paths
backend/
  src/
    agent.py            # voice agent (LLM + tools)
    merchant.py         # merchant API: load_catalog, list_products, create_order, save_order
shared-data/
  day9_catalog.json     # your product catalog (you create/edit)
  day9_orders.json      # orders appended here by merchant.save_order()
frontend/
  ...                   # UI (optional) to join LiveKit room and speak
  Example day9_catalog.json

Create shared-data/day9_catalog.json with at least 10 items (small but diverse).

[
  {
    "id": "mug-001",
    "name": "Stoneware Coffee Mug",
    "description": "Handmade 12oz stoneware mug",
    "price": 499,
    "currency": "INR",
    "category": "mugs",
    "color": "white"
  },
  {
    "id": "hoodie-black-m",
    "name": "Cozy Hoodie (Black, M)",
    "description": "Medium, cotton-blend hoodie",
    "price": 1199,
    "currency": "INR",
    "category": "clothing",
    "color": "black",
    "size": "M"
  }
  // add 8–20 items total
]

Merchant layer (example: backend/src/merchant.py)

The merchant layer is a tiny Python API that the agent calls.

Key functions:

load_catalog() → returns list[dict]

list_products(filters: dict|None) → returns filtered list (category, max_price, color)

create_order(line_items: list[dict]) → builds an order object, persists it, returns order

Example shape of order returned by create_order:

{
  "id": "order-1700000000",
  "items": [
    {"id":"mug-001","name":"Stoneware Coffee Mug","price":499,"quantity":1}
  ],
  "total": 499,
  "currency": "INR",
  "created_at": "2025-11-30T12:00:00Z"
}
Agent changes (what backend/src/agent.py should do)

Import merchant functions:

from merchant import load_catalog, list_products, create_order


At entrypoint() load the catalog and place it in session userdata:

catalog = load_catalog()
session = AgentSession(..., userdata={"catalog": catalog, "last_order": None, "last_products": []})


Add LLM-callable tools inside the Assistant class (use @function_tool()):

list_products_tool(ctx, filters: dict | None = None) — calls list_products(filters), stores ctx.userdata["last_products"], returns the products

create_order_tool(ctx, product_id: str, quantity: int = 1) — calls create_order(...), stores ctx.userdata["last_order"], returns order

get_last_order_tool(ctx) — returns ctx.userdata.get("last_order")

Instruction prompt (GM for commerce): make agent ask clarifying questions ("Which size?", "Confirm order?") and call the tools (LLM should call them; your function tools make that possible).

Why function tools: keeping catalog/order logic in merchant.py and exposing only well-typed functions prevents the LLM from inventing product details and keeps data authoritative.
Conversation flow examples
Browse

User: “Show me coffee mugs under 600.”
Agent (LLM) calls list_products_tool({"category":"mugs", "max_price":600}) → tool returns list → agent speaks summary: “I found 2 mugs: Stoneware Coffee Mug — ₹499; Classic Ceramic Mug — ₹549. Want either?”

Buy

User: “I’ll take the stoneware mug.”
Agent resolves product ID (using last_products or by name matching), then calls create_order_tool(product_id="mug-001", quantity=1) → receives order → confirms: “Order placed: 1 × Stoneware Coffee Mug. Total ₹499. Order ID order-170... Would you like a receipt?”

What did I buy?

User: “What did I just buy?”
Agent calls get_last_order_tool() → reads back items and total.

How to run (local dev)

Prereqs: Python 3.10+ (project venv), Node (if frontend), set .env.local keys for LiveKit, Murf, STT/LLM providers if needed.

Backend

Create & activate venv, install Python deps:

python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

pip install -r backend/requirements.txt


Ensure shared-data/day9_catalog.json exists.

Run the agent worker:

uv run python src/agent.py dev


This starts a worker that will register with LiveKit and handle room joins.

Frontend (optional)

If the repo has a frontend (LiveKit web UI):

cd frontend
npm install
npm run dev
# open http://localhost:3000 (or the port printed)


Then join the LiveKit room (UI should be wired to the repo's front end) and speak to the agent.

Development & testing tips

If the LLM returns ambiguous product references (“the second one”), keep ctx.userdata["last_products"] populated so the agent can resolve “the second” reliably.

Add defensive checks in create_order: if product_id not found return a friendly error; LLM can then ask user to clarify.

Log all calls in merchant.py (use logging.info) so you can trace which products were requested and which orders were created.

For offline testing without LiveKit, you can write a small python test harness that calls list_products() and create_order() directly.
Minimal unit tests suggestions

Test merchant.load_catalog() reads JSON and returns list.

Test list_products filters correctly (category, max_price, color).

Test create_order returns order with correct total and persists to day9_orders.json.

Use pytest in backend/tests/.
MVP Checklist

 day9_catalog.json exists and contains 10+ items

 merchant.py contains load_catalog, list_products, create_order, save_order

 agent.py loads catalog into session userdata

 Tools implemented: list_products_tool, create_order_tool, get_last_order_tool

 Orders persisted to shared-data/day9_orders.json

 Agent can summarize products and confirm orders

 Agent can read back the last order


 #VoiceAI #AgenticCommerce #ACP #LiveKit #MurfAI #Gemini #STT #TTS #Ecommerce #BuildInPublic #Day9 #10DaysofAIVoiceAgents
