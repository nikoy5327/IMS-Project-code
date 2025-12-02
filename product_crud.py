import psycopg2
from psycopg2.extras import RealDictCursor  # Returns rows as dictionaries

class product_crud:
    """Database CRUD operations for sales processing"""

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


    # ---------------------- UPDATE PRODUCT ----------------------
    def search_product_sales(self, name=None):
        """Searches for product"""

      
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            # Verify product exists and is not archived
            cursor.execute("SELECT * FROM products WHERE archived = FALSE AND name ILIKE %s", (f"%{name}%",))
            #raise ValueError("This is a custom error message")
            #cursor.execute("SELECT * FROM products WHERE archived = FALSE AND name ILIKE %s", ("%eggs%",)) 
            product = cursor.fetchone()

            if not product or product["archived"] is True:
                return None 
            return product 
  
        finally:
            cursor.close()
            conn.close()
