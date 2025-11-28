# app.py
from flask import Flask, request, jsonify, abort, send_from_directory
from flask_cors import CORS
from db import crud
import os

app = Flask(__name__)
CORS(app)

# Serve the main frontend page
@app.route("/")
def serve_frontend():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Inventory Management System</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; color: #333; line-height: 1.6; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem 0; text-align: center; margin-bottom: 2rem; border-radius: 10px; }
            h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
            .controls { background: white; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; display: flex; gap: 15px; flex-wrap: wrap; }
            .form-group { flex: 1; min-width: 200px; }
            label { display: block; margin-bottom: 5px; font-weight: 600; }
            input, select, button { width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 5px; font-size: 1rem; }
            button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; cursor: pointer; }
            .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
            .product-card { background: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .loading { text-align: center; padding: 2rem; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Inventory Management System</h1>
                <div class="subtitle">Manage your products efficiently</div>
            </header>
            <div class="controls">
                <div class="search-box" style="display: flex; gap: 10px; flex: 1;">
                    <div class="form-group" style="flex: 1;">
                        <label for="search">Search Products</label>
                        <input type="text" id="search" placeholder="Enter product name...">
                    </div>
                    <button onclick="searchProducts()" style="width: auto; align-self: end;">Search</button>
                    <button onclick="clearSearch()" style="width: auto; align-self: end; background: #f5576c;">Clear</button>
                </div>
                <div class="form-group">
                    <button onclick="showAddProductModal()">Add New Product</button>
                </div>
            </div>
            <div id="products-container" class="products-grid">
                <div class="loading">Loading products...</div>
            </div>
        </div>

        <script>
            const API_BASE = '/api';

            async function loadProducts() {
                try {
                    showLoading();
                    const response = await fetch(API_BASE + '/products');
                    if (!response.ok) throw new Error('Failed to fetch products');
                    const products = await response.json();
                    displayProducts(products);
                } catch (error) {
                    document.getElementById('products-container').innerHTML = 
                        '<div class="loading">Error loading products. Make sure the Flask server is running.</div>';
                }
            }

            async function searchProducts() {
                const query = document.getElementById('search').value.trim();
                try {
                    showLoading();
                    const url = query ? `${API_BASE}/products?q=${encodeURIComponent(query)}` : `${API_BASE}/products`;
                    const response = await fetch(url);
                    const products = await response.json();
                    displayProducts(products);
                } catch (error) {
                    alert('Search error: ' + error.message);
                }
            }

            function clearSearch() {
                document.getElementById('search').value = '';
                loadProducts();
            }

            function displayProducts(products) {
                const container = document.getElementById('products-container');
                if (products.length === 0) {
                    container.innerHTML = '<div class="loading">No products found</div>';
                    return;
                }

                container.innerHTML = products.map(product => `
                    <div class="product-card">
                        <div style="font-size: 1.3rem; font-weight: 600; margin-bottom: 0.5rem;">${product.name}</div>
                        <div style="color: #666; margin-bottom: 1rem;">${product.product_code || 'No code'}</div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 1rem 0;">
                            <div style="text-align: center; padding: 0.5rem; background: #f8f9fa; border-radius: 5px;">
                                <div style="font-size: 0.8rem; color: #666;">Quantity</div>
                                <div style="font-weight: 600; font-size: 1.1rem;">${product.current_quantity}</div>
                            </div>
                            <div style="text-align: center; padding: 0.5rem; background: #f8f9fa; border-radius: 5px;">
                                <div style="font-size: 0.8rem; color: #666;">Price</div>
                                <div style="font-weight: 600; font-size: 1.1rem;">$${parseFloat(product.price || 0).toFixed(2)}</div>
                            </div>
                        </div>
                        <div style="display: flex; gap: 10px; margin-top: 1rem;">
                            <button onclick="editProduct(${product.id})" style="flex: 1;">Edit</button>
                            <button onclick="archiveProduct(${product.id})" style="flex: 1; background: #f5576c;">Archive</button>
                        </div>
                    </div>
                `).join('');
            }

            function showLoading() {
                document.getElementById('products-container').innerHTML = '<div class="loading">Loading products...</div>';
            }

            function showAddProductModal() {
                alert('Add product feature would open a modal. Check the console for the full implementation.');
                // In the full version, this would open a modal form
            }

            function editProduct(productId) {
                alert('Edit product ' + productId + ' - This would open an edit form.');
                // In the full version, this would open a modal with the product data
            }

            function archiveProduct(productId) {
                if (confirm('Are you sure you want to archive this product?')) {
                    fetch(`${API_BASE}/products/${productId}`, { method: 'DELETE' })
                        .then(response => {
                            if (response.ok) {
                                loadProducts(); // Reload the list
                                alert('Product archived successfully!');
                            } else {
                                alert('Failed to archive product');
                            }
                        })
                        .catch(error => alert('Error: ' + error.message));
                }
            }

            // Load products when page loads
            document.addEventListener('DOMContentLoaded', loadProducts);
        </script>
    </body>
    </html>
    """

# Your existing API routes
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