from flask import Blueprint, request
from services.sales_service import SalesService

sales_bp = Blueprint("sales", __name__)

@sales_bp.post("/")
def make_sale():
    data = request.json
    return SalesService.create_sale(
        cashier_id=data["cashier_id"],
        items=data["items"]
    )
