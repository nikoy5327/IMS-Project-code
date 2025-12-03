from database.connection import SessionLocal
from database.models import SaleTransaction, SaleItem, Product
from utils.pdf_generator import generate_receipt
from services.alert_service import AlertService

class SalesService:

    @staticmethod
    def create_sale(cashier_id, items):
        session = SessionLocal()

        transaction = SaleTransaction(cashier_id=cashier_id)
        session.add(transaction)
        session.commit()

        subtotal = 0

        result_items = []

        for item in items:
            product = session.query(Product).filter_by(product_id=item["product_id"]).first()

            line_total = product.price * item["qty"]
            subtotal += line_total

            sale_item = SaleItem(
                product_id=product.product_id,
                transaction_id=transaction.transaction_id,
                quantity=item["qty"],
                price_at_sale=product.price
            )
            session.add(sale_item)

            product.current_quantity -= item["qty"]

            AlertService.check_low_stock(product.product_id)

            result_items.append({
                "name": product.name,
                "qty": item["qty"],
                "price": product.price
            })

        tax = subtotal * 0.15
        total = subtotal + tax

        transaction.subtotal = subtotal
        transaction.tax = tax
        transaction.total = total

        session.commit()

        file = generate_receipt(transaction, result_items)

        return {"message": "Sale complete", "receipt": file}
