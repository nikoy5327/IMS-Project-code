import sale_item as si
import psycopg2
from psycopg2.extras import RealDictCursor  # Returns rows as dictionaries

class sale_transaction_crud:
    """Database CRUD operations for sale_transaction table"""

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
    
            #sale_transaction fields:
            # transaction_id integer,
            # date date,
            # cashier_id integer,
            # subtotal numeric(10, 2),
            # tax numeric(10, 2),
            # discount numeric(10, 2),
            # total numeric(10, 2)

    def add_transaction(self, date, cashier_id, transaction_data, sale_items):
        """Add a sale transaction to the database"""
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            sql = """
                INSERT INTO sale_transaction
                (date, cashier_id, subtotal, tax, discount, total)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING transaction_id;
            """

            cursor.execute(sql, (
                date, cashier_id,
                transaction_data["subtotal"],
                transaction_data["tax"],
                transaction_data["discount"],
                transaction_data["total"]
            ))

            new_id = cursor.fetchone()["transaction_id"]
            conn.commit()  # Save changes to database

            # Add each sale item to the sale_item table
            for item in sale_items:
                self.add_sale_item(item, new_id)

            return new_id
        finally:
            cursor.close()
            conn.close()

    def add_sale_item(self, sale_item, transaction_id: int):
        """Add an item to the current sale transaction"""
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            # sale_item fields:
                # sale_item_id integer,
                # transaction_id integer,
                # product_id integer,
                # "quantity " integer,
                # price_at_sale numeric(10, 2)
            sql = """
                INSERT INTO sale_item
                (transaction_id, product_id, quantity, price_at_sale)
                VALUES (%s, %s, %s, %s)
                RETURNING sale_item_id;
            """

            cursor.execute(sql, (
                transaction_id, sale_item.product["id"], sale_item.quantity, sale_item.price
            ))

            new_id = cursor.fetchone()["sale_item_id"]
            conn.commit()  # Save changes to database
            return new_id
        finally:
            cursor.close()
            conn.close()

        