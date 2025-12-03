import psycopg2
from psycopg2.extras import RealDictCursor

class InventoryCRUD:
    def __init__(self, host, database, user, password):
        self.config = {
            "host": host,
            "database": database,
            "user": user,
            "password": password
        }

    def connect(self):
        """Create and return a new database connection"""
        return psycopg2.connect(**self.config)

    def list_products(self, search_term="", limit=100):
        """Get list of products with optional search"""
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            if search_term:
                sql = """
                    SELECT 
                        id, product_code, name, category_id, 
                        price, current_quantity as quantity, 
                        reorder_threshold, archived,
                        created_by, last_updated_by,
                        created_at, updated_at
                    FROM products 
                    WHERE name ILIKE %s 
                    AND archived = FALSE 
                    ORDER BY id 
                    LIMIT %s
                """
                cursor.execute(sql, (f"%{search_term}%", limit))
            else:
                sql = """
                    SELECT 
                        id, product_code, name, category_id, 
                        price, current_quantity as quantity, 
                        reorder_threshold, archived,
                        created_by, last_updated_by,
                        created_at, updated_at
                    FROM products 
                    WHERE archived = FALSE 
                    ORDER BY id 
                    LIMIT %s
                """
                cursor.execute(sql, (limit,))
            
            rows = cursor.fetchall()
            return rows
            
        finally:
            cursor.close()
            conn.close()

    def get_product(self, product_id):
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            sql = """
                SELECT 
                    id, product_code, name, category_id, 
                    price, current_quantity as quantity, 
                    reorder_threshold, archived,
                    created_by, last_updated_by,
                    created_at, updated_at
                FROM products 
                WHERE id = %s 
                AND archived = FALSE
            """
            cursor.execute(sql, (product_id,))
            product = cursor.fetchone()
            return product
            
        finally:
            cursor.close()
            conn.close()

    def add_product(self, name, current_quantity, price,
                    category_id=None, product_code=None,
                    reorder_threshold=None, created_by=None):
        """Create a new product in the database"""
        
        # Input validation
        if not name or name.strip() == "":
            raise ValueError("Product name is required.")
        if current_quantity < 0:
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
                product_code, name, category_id, price, current_quantity,
                reorder_threshold, created_by, created_by
            ))

            new_id = cursor.fetchone()["id"]
            conn.commit()
            return new_id

        finally:
            cursor.close()
            conn.close()

    def update_product(self, product_id,
                       name=None, current_quantity=None, price=None,
                       category_id=None, reorder_threshold=None,
                       last_updated_by=None):
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

            if current_quantity is not None:
                updates.append("current_quantity = %s")
                params.append(current_quantity)

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

            # Add audit field
            updates.append("last_updated_by = %s")
            params.append(last_updated_by)

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

    def delete_product(self, product_id, last_updated_by=None, permanent=False):
        """Delete a product - soft delete (archive) by default"""
        
        if not product_id:
            raise ValueError("Product ID is required.")

        conn = self.connect()
        cursor = conn.cursor()

        try:
            if permanent:
                # Hard delete
                cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            else:
                # Soft delete (archive)
                sql = """
                    UPDATE products
                    SET archived = TRUE,
                        last_updated_by = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                cursor.execute(sql, (last_updated_by, product_id))

            conn.commit()
            return True

        finally:
            cursor.close()
            conn.close()
