import psycopg2
from psycopg2.extras import RealDictCursor

class InventoryCRUD:
    def __init__(self, host, database, user, password):
        # Store database connection parameters
        self.config = {
            "host": host,           # Use parameters, not hardcoded values
            "database": database,
            "user": user,
            "password": password
        }

    def connect(self):
        """Create and return a new database connection"""
        return psycopg2.connect(**self.config)

    # ---------------------- READ OPERATIONS ----------------------
    def get_product(self, product_id):
        """Get a single product by ID"""
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def list_products(self, search_query=None, limit=100):
        """List products, optionally filtered by search"""
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            if search_query:
                cursor.execute("""
                    SELECT id, product_code, name, current_quantity, price, archived
                    FROM products
                    WHERE archived = FALSE AND name ILIKE %s
                    ORDER BY name
                    LIMIT %s
                """, (f"%{search_query}%", limit))
            else:
                cursor.execute("""
                    SELECT id, product_code, name, current_quantity, price, archived
                    FROM products
                    WHERE archived = FALSE
                    ORDER BY name
                    LIMIT %s
                """, (limit,))
            
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

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
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            # Check if product with same name already exists
            cursor.execute(
                "SELECT id FROM products WHERE name = %s AND archived = FALSE",
                (name,)
            )
            if cursor.fetchone():
                raise ValueError("A product with this name already exists.")

            # SQL insert with RETURNING clause
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
            conn.commit()
            return new_id

        finally:
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

            # Dynamic SQL building
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
            return cursor.rowcount > 0

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
                cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            else:
                cursor.execute(
                    """
                    UPDATE products
                    SET archived = TRUE,
                        last_updated_by = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (user_id, product_id)
                )

            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()