"""Run: python -m pytest inventory-service  (or: python inventory-service/test_app.py)"""
import os
import tempfile

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test.db")

from app import app  # noqa: E402


def test_crud_flow():
    c = app.test_client()
    assert c.post("/items", json={"name": "Laptop"}).status_code == 400
    assert c.post("/items", json={"name": "X", "sku": "A", "quantity": -1}).status_code == 400

    r = c.post("/items", json={"name": "Laptop Asus", "sku": "LPT-001", "quantity": 5, "location": "Gudang A"})
    assert r.status_code == 201
    item_id = r.get_json()["itemId"]
    assert c.post("/items", json={"name": "Dup", "sku": "LPT-001", "quantity": 1}).status_code == 409

    assert c.get("/items").get_json()["count"] == 1
    assert c.get(f"/items/{item_id}").get_json()["sku"] == "LPT-001"

    r = c.put(f"/items/{item_id}", json={"quantity": 3})
    assert r.status_code == 200 and r.get_json()["quantity"] == 3

    assert c.delete(f"/items/{item_id}").status_code == 200
    assert c.get(f"/items/{item_id}").status_code == 404


if __name__ == "__main__":
    test_crud_flow()
    print("OK")
