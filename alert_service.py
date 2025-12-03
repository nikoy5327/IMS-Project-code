from database.connection import SessionLocal
from database.models import Alert, Product

class AlertService:

    @staticmethod
    def check_low_stock(product_id):
        session = SessionLocal()
        product = session.query(Product).filter_by(product_id=product_id).first()

        if not product:
            session.close()
            return

        # Only create alert if quantity <= threshold and no existing unresolved alert
        existing_alert = session.query(Alert).filter_by(
            product_id=product_id,
            alert_type="LOW_STOCK",
            status="UNRESOLVED"
        ).first()

        if product.current_quantity <= product.reorder_threshold and not existing_alert:
            alert = Alert(
                product_id=product_id,
                alert_type="LOW_STOCK",
                message=f"{product.name} is low on stock!",
                status="UNRESOLVED"
            )
            session.add(alert)
            session.commit()

        session.close()

    @staticmethod
    def check_all_products():
        session = SessionLocal()
        products = session.query(Product).all()
        session.close()

        for p in products:
            AlertService.check_low_stock(p.product_id)




