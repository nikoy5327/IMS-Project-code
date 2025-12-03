from flask import Blueprint, request, jsonify
from services.inventory_service import InventoryService

inventory_bp = Blueprint("inventory", __name__)

@inventory_bp.get("/")
def get_inventory():
    return jsonify(InventoryService.get_all_products())

@inventory_bp.post("/product")
def add_product():
    data = request.json
    return jsonify(InventoryService.add_product(data, user_id=1))

@inventory_bp.put("/product/<int:id>")
def update_product(id):
    data = request.json
    return jsonify(InventoryService.update_product(id, data, user_id=1))

@inventory_bp.delete("/product/<int:id>")
def delete_product(id):
    return jsonify(InventoryService.delete_product(id))

@inventory_bp.get("/categories")
def get_categories():
    return jsonify(InventoryService.get_all_categories())
@inventory_bp.post("/category")
def add_category():
    data = request.json
    return jsonify(InventoryService.add_category(data))
