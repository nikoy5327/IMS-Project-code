# app.py
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from db import crud
import os

app = Flask(__name__)
CORS(app)

@app.route("/api/products", methods=["GET"])
def list_products():
    """
    Optional query params:
      - q : partial name search
      - limit : integer
    """
    q = request.args.get("q", "").strip()
    limit = int(request.args.get("limit", 100))

    try:
        if q:
            # Simple search implemented here using raw SQL via CRUD helper.
            # inventory_crud_pg doesn't have a search function, so implement a quick one:
            conn = crud.connect()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, product_code, name, current_quantity, price, archived
                FROM products
                WHERE archived = FALSE AND name ILIKE %s
                ORDER BY name
                LIMIT %s
            """, (f"%{q}%", limit))
            rows = [dict(zip([c[0] for c in cur.description], r)) for r in cur.fetchall()]
            cur.close()
            conn.close()
            return jsonify(rows), 200

        # if no search, return first N active products
        conn = crud.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, product_code, name, current_quantity, price, archived
            FROM products
            WHERE archived = FALSE
            ORDER BY name
            LIMIT %s
        """, (limit,))
        rows = [dict(zip([c[0] for c in cur.description], r)) for r in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(rows), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    try:
        conn = crud.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return jsonify({"error": "Product not found"}), 404
        # map columns to values
        cols = [c[0] for c in conn.cursor().description] if False else None
        # simpler: use the CRUD helper
        # Reuse inventory_crud_pg's fetch by adapting (we'll just return limited fields here)
        conn = crud.connect()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, product_code, name, category_id, price, current_quantity,
                   reorder_threshold, archived, created_by, last_updated_by, created_at, updated_at
            FROM products WHERE id = %s
        """, (product_id,))
        r = cur.fetchone()
        if not r:
            cur.close(); conn.close()
            return jsonify({"error": "Product not found"}), 404
        cols = [c[0] for c in cur.description]
        obj = dict(zip(cols, r))
        cur.close(); conn.close()
        return jsonify(obj), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products", methods=["POST"])
def create_product():
    """
    Expects JSON body with:
      - name (required)
      - quantity (required, int)
      - price (required, numeric)
      - category_id (optional)
      - product_code (optional)
      - reorder_threshold (optional)
      - user_id (optional)
    """
    data = request.get_json(force=True)
    required = ["name", "quantity", "price"]
    for k in required:
        if k not in data:
            return jsonify({"error": f"Missing field: {k}"}), 400

    try:
        new_id = crud.add_product(
            name=data["name"],
            quantity=int(data["quantity"]),
            price=float(data["price"]),
            category_id=data.get("category_id"),
            product_code=data.get("product_code"),
            reorder_threshold=data.get("reorder_threshold"),
            user_id=data.get("user_id")
        )
        return jsonify({"id": new_id}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products/<int:product_id>", methods=["PUT", "PATCH"])
def update_product(product_id):
    """
    Accepts partial updates. JSON body may contain any of name, quantity, price, category_id, reorder_threshold, user_id
    """
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        success = crud.update_product(
            product_id=product_id,
            name=data.get("name"),
            quantity=(int(data["quantity"]) if "quantity" in data else None),
            price=(float(data["price"]) if "price" in data else None),
            category_id=data.get("category_id"),
            reorder_threshold=data.get("reorder_threshold"),
            user_id=data.get("user_id")
        )
        if not success:
            return jsonify({"message": "No fields updated"}), 200
        return jsonify({"message": "Updated"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """
    Query param: permanent=true to hard-delete
    JSON body may include user_id
    """
    permanent = request.args.get("permanent", "false").lower() in ("1", "true", "yes")
    user_id = None
    if request.is_json:
        user_id = request.get_json().get("user_id")
    try:
        crud.delete_product(product_id=product_id, user_id=user_id, permanent=permanent)
        return jsonify({"message": "Deleted" if permanent else "Archived"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
