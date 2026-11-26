import os
import sqlite3
import uuid
from datetime import datetime, timezone

from flask import Flask, g, jsonify, request

DB_PATH = os.environ.get("DB_PATH", "/data/inventory.db")
FIELDS = ("name", "sku", "category", "quantity", "location")
REQUIRED = ("name", "sku", "quantity")

app = Flask(__name__)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn:
        conn.close()


def init_db():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS items (
                itemId TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                sku TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL DEFAULT '',
                quantity INTEGER NOT NULL CHECK (quantity >= 0),
                location TEXT NOT NULL DEFAULT '',
                createdAt TEXT NOT NULL,
                updatedAt TEXT NOT NULL)"""
        )


def validate(body, partial=False):
    if not isinstance(body, dict):
        return "Body must be a JSON object"
    if not partial:
        missing = [f for f in REQUIRED if body.get(f) in (None, "")]
        if missing:
            return f"Missing required field(s): {', '.join(missing)}"
    if "quantity" in body:
        q = body["quantity"]
        if not isinstance(q, int) or isinstance(q, bool) or q < 0:
            return "quantity must be an integer >= 0"
    for f in ("name", "sku", "category", "location"):
        if f in body and not isinstance(body[f], str):
            return f"{f} must be a string"
    return None


def get_item(item_id):
    row = db().execute("SELECT * FROM items WHERE itemId = ?", (item_id,)).fetchone()
    return dict(row) if row else None


def not_found(item_id):
    return jsonify(message=f"Item {item_id} not found"), 404


@app.get("/health")
def health():
    return jsonify(status="ok", service="inventory-service")


@app.post("/items")
def create_item():
    body = request.get_json(silent=True)
    err = validate(body)
    if err:
        return jsonify(message=err), 400
    ts = now()
    item = {
        "itemId": str(uuid.uuid4()),
        "name": body["name"],
        "sku": body["sku"],
        "category": body.get("category", ""),
        "quantity": body["quantity"],
        "location": body.get("location", ""),
        "createdAt": ts,
        "updatedAt": ts,
    }
    try:
        db().execute(
            "INSERT INTO items VALUES (:itemId,:name,:sku,:category,:quantity,:location,:createdAt,:updatedAt)",
            item,
        )
        db().commit()
    except sqlite3.IntegrityError:
        return jsonify(message=f"SKU {body['sku']} already exists"), 409
    return jsonify(item), 201


@app.get("/items")
def list_items():
    rows = db().execute("SELECT * FROM items ORDER BY createdAt").fetchall()
    items = [dict(r) for r in rows]
    return jsonify(count=len(items), items=items)


@app.get("/items/<item_id>")
def read_item(item_id):
    item = get_item(item_id)
    return jsonify(item) if item else not_found(item_id)


@app.put("/items/<item_id>")
def update_item(item_id):
    item = get_item(item_id)
    if not item:
        return not_found(item_id)
    body = request.get_json(silent=True)
    err = validate(body, partial=True)
    if err:
        return jsonify(message=err), 400
    item.update({k: body[k] for k in FIELDS if k in body})
    item["updatedAt"] = now()
    try:
        db().execute(
            "UPDATE items SET name=:name, sku=:sku, category=:category, quantity=:quantity, "
            "location=:location, updatedAt=:updatedAt WHERE itemId=:itemId",
            item,
        )
        db().commit()
    except sqlite3.IntegrityError:
        return jsonify(message=f"SKU {body['sku']} already exists"), 409
    return jsonify(item)


@app.delete("/items/<item_id>")
def delete_item(item_id):
    if not get_item(item_id):
        return not_found(item_id)
    db().execute("DELETE FROM items WHERE itemId = ?", (item_id,))
    db().commit()
    return jsonify(message=f"Item {item_id} deleted")


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
