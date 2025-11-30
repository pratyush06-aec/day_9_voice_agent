from datetime import datetime
import json
from pathlib import Path

ORDERS_PATH = Path("shared-data/day9_orders.json")
CATALOG_PATH = Path("shared-data/day9_catalog.json")

def load_catalog():
    with CATALOG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_order(order):
    if not ORDERS_PATH.exists():
        with ORDERS_PATH.open("w") as f:
            json.dump([], f)

    with ORDERS_PATH.open("r", encoding="utf-8") as f:
        orders = json.load(f)

    orders.append(order)

    with ORDERS_PATH.open("w", encoding="utf-8") as f:
        json.dump(orders, f, indent=2)

def list_products(filters=None):
    products = load_catalog()
    if not filters:
        return products

    # simple filtering logic
    result = []
    for p in products:
        ok = True
        if "category" in filters and p.get("category") != filters["category"]:
            ok = False
        if "max_price" in filters and p.get("price") > filters["max_price"]:
            ok = False
        if "color" in filters and p.get("color") != filters["color"]:
            ok = False
        if ok:
            result.append(p)

    return result

def create_order(line_items):
    products = load_catalog()
    lookup = {p["id"]: p for p in products}

    items = []
    total = 0

    for li in line_items:
        pid = li["product_id"]
        qty = li.get("quantity", 1)

        if pid not in lookup:
            continue

        prod = lookup[pid]
        subtotal = prod["price"] * qty

        items.append({
            "id": pid,
            "name": prod["name"],
            "price": prod["price"],
            "quantity": qty
        })
        total += subtotal

    order = {
        "id": f"order-{int(datetime.now().timestamp())}",
        "items": items,
        "total": total,
        "currency": "INR",
        "created_at": datetime.now().isoformat()
    }

    save_order(order)
    return order
