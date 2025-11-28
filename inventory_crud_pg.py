import psycopg2
from psycopg2.extras import RealDictCursor  # Returns rows as dictionaries

class InventoryCRUD:
    """Database CRUD operations for inventory management"""

    def __init__(self, host, database, user, password):
        # Store database connection parameters
        self.config = {
            "host": host,
            "database": database,
            "user": user,
            "password": password
        }

    def connect(self):
        """Create and return a new database connection"""
        return psycopg2.connect(**self.config)

    # ---------------------- ADD PRODUCT ----------------------
    def add_product(self, name, quantity, price,
                    category_id=None, product_code=None,
                    reorder_threshold=None, user_id=None):
        """Create a new product in the database"""

        # Input validation
        if not name or name.strip() == "":
            raise ValueError("Product name is required.")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        conn = self.connect()
        # Use RealDictCursor to get rows as dictionaries
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            # Check if product with same name already exists (and is active)
            cursor.execute(
                "SELECT id FROM products WHERE name = %s AND archived = FALSE",
                (name,)
            )
            if cursor.fetchone():
                raise ValueError("A product with this name already exists.")

            # SQL insert with RETURNING clause to get the new ID
            sql = """
                INSERT INTO products
                (product_code, name, category_id, price, current_quantity,
                 reorder_threshold, created_by, last_updated_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """

            cursor.execute(sql, (
                product_code, name, category_id, price, quantity,
                reorder_threshold, user_id, user_id
            ))

            new_id = cursor.fetchone()["id"]
            conn.commit()  # Save changes to database

            return new_id

        finally:
            # Always close connections in finally block
            cursor.close()
            conn.close()

    # ---------------------- UPDATE PRODUCT ----------------------
    def update_product(self, product_id,
                       name=None, quantity=None, price=None,
                       category_id=None, reorder_threshold=None,
                       user_id=None):
        """Update existing product - only provided fields are updated"""

        if not product_id:
            raise ValueError("Product ID is required.")

        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            # Verify product exists and is not archived
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()

            if not product or product["archived"] is True:
                raise ValueError("Product does not exist or is archived.")

            # Dynamic SQL building - only include fields that are provided
            updates = []
            params = []

            if name is not None:
                updates.append("name = %s")
                params.append(name)

            if quantity is not None:
                updates.append("current_quantity = %s")
                params.append(quantity)

            if price is not None:
                updates.append("price = %s")
                params.append(price)

            if category_id is not None:
                updates.append("category_id = %s")
                params.append(category_id)

            if reorder_threshold is not None:
                updates.append("reorder_threshold = %s")
                params.append(reorder_threshold)

            # If no fields to update, return early
            if not updates:
                return False

            # Add audit fields
            updates.append("last_updated_by = %s")
            params.append(user_id)

            params.append(product_id)  # WHERE clause parameter

            # Build dynamic UPDATE query
            sql = f"""
                UPDATE products
                SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """

            cursor.execute(sql, params)
            conn.commit()

            return True

        finally:
            cursor.close()
            conn.close()

    # ---------------------- DELETE PRODUCT ----------------------
    def delete_product(self, product_id, user_id=None, permanent=False):
        """Delete a product - soft delete (archive) by default"""

        if not product_id:
            raise ValueError("Product ID is required.")

        conn = self.connect()
        cursor = conn.cursor()

        try:
            if permanent:
                # Hard delete - completely remove from database
                cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            else:
                # Soft delete - mark as archived (preferred approach)
                cursor.execute(
                    """
                    UPDATE products
                    SET archived = TRUE,  # Use TRUE for PostgreSQL boolean
                        last_updated_by = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (user_id, product_id)
                )

            conn.commit()
            return True

        finally:
            cursor.close()
            conn.close()