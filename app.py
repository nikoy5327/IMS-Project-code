from flask import Flask, request, jsonify
from flask_cors import CORS
from db import crud
import os

app = Flask(__name__)
CORS(app)

@app.route("/api/products", methods=["GET"])
def list_products():
    q = request.args.get("q", "").strip()
    limit = int(request.args.get("limit", 100))
    
    try:
        print(f"DEBUG: list_products called - q='{q}', limit={limit}")
        
        # Use the crud.list_products method instead of raw SQL
        products = crud.list_products(search_term=q, limit=limit)
        return jsonify(products), 200
            
    except Exception as e:
        print(f"DEBUG: ERROR in list_products: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    try:
        print(f"DEBUG: get_product called - id={product_id}")
        product = crud.get_product(product_id)
        
        if not product:
            return jsonify({"error": "Product not found"}), 404
            
        return jsonify(product), 200
    except Exception as e:
        print(f"DEBUG: ERROR in get_product: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.get_json(force=True)
    required = ["name", "price"]  
    
    for key in required:
        if key not in data:
            return jsonify({"error": f"Missing field: {key}"}), 400
    
    try:
        print(f"DEBUG: create_product called - name={data['name']}")
        
        new_id = crud.add_product(
            name=data["name"],
            current_quantity=int(data.get("quantity", 0)),  
            price=float(data["price"]),
            category_id=data.get("category_id"),
            product_code=data.get("product_code"),
            reorder_threshold=data.get("reorder_threshold", 0),  
            created_by=data.get("user_id")
        )
        return jsonify({"id": new_id}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"DEBUG: ERROR in create_product: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/products/<int:product_id>", methods=["PUT", "PATCH"])
def update_product(product_id):
    data = request.get_json(force=True)
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        print(f"DEBUG: update_product called - id={product_id}")
        
        success = crud.update_product(
            product_id=product_id,
            name=data.get("name"),
            current_quantity=(int(data["quantity"]) if "quantity" in data else None),
            price=(float(data["price"]) if "price" in data else None),
            category_id=data.get("category_id"),
            reorder_threshold=data.get("reorder_threshold"),
            last_updated_by=data.get("user_id")
        )
        
        if not success:
            return jsonify({"message": "No fields updated"}), 200
        return jsonify({"message": "Updated"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"DEBUG: ERROR in update_product: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    permanent = request.args.get("permanent", "false").lower() in ("1", "true", "yes")
    user_id = None
    
    if request.is_json:
        user_id = request.get_json().get("user_id")
    
    try:
        print(f"DEBUG: delete_product called - id={product_id}, permanent={permanent}")
        
        crud.delete_product(
            product_id=product_id, 
            last_updated_by=user_id,  
            permanent=permanent
        )
        return jsonify({"message": "Deleted" if permanent else "Archived"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"DEBUG: ERROR in delete_product: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "inventory-api"}), 200

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    
    # Print all registered routes
    print("\n" + "="*50)
    print("🚀 Flask Application Routes:")
    print("="*50)
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods.difference(['HEAD', 'OPTIONS'])))
        print(f"  {rule.rule} [{methods}] -> {rule.endpoint}")
    print("="*50)
    print(f"📡 Server starting on: http://localhost:{port}")
    print(f"🔧 Debug mode: {debug}")
    print("="*50 + "\n")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
