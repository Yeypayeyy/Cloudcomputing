#!/usr/bin/env bash
# CRUD smoke test for inventory-service. Usage: ./scripts/crud-test.sh [base_url]
set -u
BASE="${1:-http://localhost:8080}"
J="Content-Type: application/json"

echo "=== 0. HEALTH (GET /health) ==="
curl -s "$BASE/health"; echo; echo

echo "=== 1. CREATE (POST /items) ==="
RES=$(curl -s -X POST "$BASE/items" -H "$J" \
  -d '{"name":"Laptop Asus Vivobook 14","sku":"LPT-ASUS-014","category":"Elektronik","quantity":10,"location":"Gudang A - Rak 2"}')
echo "$RES"; echo
ID=$(echo "$RES" | sed -n 's/.*"itemId":"\([^"]*\)".*/\1/p')

echo "=== 1b. CREATE invalid (expect 400) ==="
curl -s -w "\nHTTP %{http_code}\n" -X POST "$BASE/items" -H "$J" -d '{"name":"Tanpa SKU"}'; echo

echo "=== 2. READ ALL (GET /items) ==="
curl -s "$BASE/items"; echo; echo

echo "=== 3. READ ONE (GET /items/{itemId}) ==="
curl -s "$BASE/items/$ID"; echo; echo

echo "=== 4. UPDATE (PUT /items/{itemId}) ==="
curl -s -X PUT "$BASE/items/$ID" -H "$J" -d '{"quantity":7,"location":"Gudang B - Rak 1"}'; echo; echo

echo "=== 5. DELETE (DELETE /items/{itemId}) ==="
curl -s -X DELETE "$BASE/items/$ID"; echo; echo

echo "=== 6. READ deleted item (expect 404) ==="
curl -s -w "\nHTTP %{http_code}\n" "$BASE/items/$ID"
