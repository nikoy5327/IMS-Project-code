from database.connection import SessionLocal
from database.models import Product, Category
from services.alert_service import AlertService
from datetime import datetime

class InventoryService:

    @staticmethod
    def get_all_products():
        session = SessionLocal()
        products = session.query(Product).all()
        data = []
        for p in products:
            data.append({
                "id": p.code,
                "name": p.name,
                "category": p.category.name if p.category else "",
                "price": p.price,
                "qty": p.current_quantity,
                "reorder_threshold": p.reorder_threshold
            })
        session.close()
        return data

    @staticmethod
    def get_all_categories():
        session = SessionLocal()
        categories = session.query(Category).order_by(Category.name).all()
        data = [{"id": c.category_id, "name": c.name} for c in categories]
        session.close()
        return data

    
    @staticmethod
    def add_product(data, user_id):
        session = SessionLocal()

        name = data.get("name")
        category_name = data.get("category")
        price = data.get("price")
        qty = data.get("quantity")
        input_code = data.get("ID")  # custom code from user

        # Validate required fields
        if not name or price is None or qty is None or not category_name:
            session.close()
            return {"error": "Missing required fields"}

        threshold = data.get("reorder_threshold")
        try:
            threshold = int(threshold)
        except (TypeError, ValueError):
            threshold = 0  

        # Handle dynamic category
        category = session.query(Category).filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name, code_prefix=category_name[:3].upper())
            session.add(category)
            session.commit()

        # Generate product code
        if input_code:
            code = input_code.upper()  # use custom ID entered by user
        else:
            prefix = category.code_prefix
            last_product = (
                session.query(Product)
                .filter(Product.category_id == category.category_id)
                .order_by(Product.product_id.desc())
                .first()
            )
            if last_product and last_product.code.startswith(prefix):
                try:
                    last_num = int(last_product.code.split("_")[-1])
                except:
                    last_num = 0
                next_num = last_num + 1
            else:
                next_num = 1
            code = f"{prefix}_{str(next_num).zfill(3)}"  # e.g., BEV_001

        # Create product
        product = Product(
            name=name,
            category_id=category.category_id,
            price=price,
            current_quantity=qty,
            reorder_threshold=threshold,
            code=code,
            updated_by_user_id=user_id
        )

        session.add(product)
        session.commit()
        AlertService.check_low_stock(product.product_id)  
        session.close()

        return {"message": "Product added", "product_code": code}


    @staticmethod
    def update_product(product_id, data, user_id):
        session = SessionLocal()
        product = session.query(Product).filter_by(product_id=product_id).first()
        if not product:
            return {"error": "Product not found"}

        # Handle dynamic category
        category_name = data.get("category")
        if category_name:
            category = session.query(Category).filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name, code_prefix=category_name[:3].upper())
                session.add(category)
                session.commit()
            product.category_id = category.category_id

        # Update other fields
        for key, value in data.items():
            if key == "reorder_threshold":
                try:
                    product.reorder_threshold = int(value)
                except (TypeError, ValueError):
                    pass  # keep current if invalid
            elif key != "category":
                setattr(product, key, value)

        product.updated_at = datetime.utcnow()
        product.updated_by_user_id = user_id

        session.commit()
        AlertService.check_low_stock(product.product_id)  
        session.close()

        return {"message": "Product updated"}

    @staticmethod
    def delete_product(product_id):
        session = SessionLocal()
        product = session.query(Product).filter_by(product_id=product_id).first()
        if not product:
            return {"error": "Product not found"}

        session.delete(product)
        session.commit()
        session.close()

        return {"message": "Product removed"}

