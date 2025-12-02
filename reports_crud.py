import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date


class ReportsCRUD:
    def __init__(self, host, database, user, password):
        self.config = {
            "host": host,
            "database": database,
            "user": user,
            "password": password
        }

    def connect(self):
        return psycopg2.connect(**self.config)

    # ---------------------------------------------------------
    # 1) MONTHLY INVENTORY REPORT
    # ---------------------------------------------------------
    def monthly_inventory_report(self, year=None, month=None):
        """
        Generates a monthly inventory report summarizing:
        - Current stock
        - Low-stock items
        - Total stock value
        """
        if year is None or month is None:
            today = date.today()
            year, month = today.year, today.month

        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            # Fetch all inventory with low-stock flag
            cursor.execute("""
                SELECT 
                    p.id, p.product_code, p.name, p.current_quantity,
                    p.price, p.reorder_threshold,
                    (p.price * p.current_quantity) AS stock_value,
                    (p.current_quantity <= p.reorder_threshold) AS is_low_stock
                FROM products p
                WHERE p.archived = FALSE
                ORDER BY p.name;
            """)

            products = cursor.fetchall()

            # Totals
            total_stock_value = sum(item["stock_value"] for item in products)
            low_stock_items = [item for item in products if item["is_low_stock"]]

            return {
                "report_type": "monthly_inventory_report",
                "year": year,
                "month": month,
                "generated_at": datetime.now(),
                "total_stock_value": total_stock_value,
                "total_products": len(products),
                "low_stock_count": len(low_stock_items),
                "low_stock_items": low_stock_items,
                "products": products
            }

        finally:
            cursor.close()
            conn.close()

    # ---------------------------------------------------------
    # 2) SALES REPORT (DATE RANGE)
    # ---------------------------------------------------------
    def sales_report(self, start_date, end_date, category_id=None):
        """
        Generates a sales report for a date range.
        Optionally filters by product category.
        """
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            sql = """
                SELECT 
                    si.product_id,
                    p.name,
                    p.category_id,
                    SUM(si.quantity) AS total_quantity_sold,
                    SUM(si.price * si.quantity) AS total_sales
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                JOIN products p ON si.product_id = p.id
                WHERE s.created_at BETWEEN %s AND %s
            """

            params = [start_date, end_date]

            if category_id:
                sql += " AND p.category_id = %s"
                params.append(category_id)

            sql += """
                GROUP BY si.product_id, p.name, p.category_id
                ORDER BY total_sales DESC;
            """

            cursor.execute(sql, params)
            results = cursor.fetchall()

            return {
                "report_type": "sales_report",
                "start_date": start_date,
                "end_date": end_date,
                "generated_at": datetime.now(),
                "items": results,
                "total_revenue": sum(item["total_sales"] for item in results)
            }

        finally:
            cursor.close()
            conn.close()

    # ---------------------------------------------------------
    # 3) LOW-STOCK REPORT
    # ---------------------------------------------------------
    def low_stock_report(self):
        """
        Generates a list of all products at or below threshold.
        """
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute("""
                SELECT 
                    id, product_code, name, current_quantity, 
                    reorder_threshold, price
                FROM products
                WHERE archived = FALSE
                  AND current_quantity <= reorder_threshold
                ORDER BY current_quantity ASC;
            """)

            items = cursor.fetchall()

            return {
                "report_type": "low_stock_report",
                "generated_at": datetime.now(),
                "count": len(items),
                "items": items
            }

        finally:
            cursor.close()
            conn.close()

    # ---------------------------------------------------------
    # 4) FULL INVENTORY SNAPSHOT (ON-DEMAND)
    # ---------------------------------------------------------
    def inventory_snapshot(self):
        """
        Returns real-time inventory with categories and values.
        """
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            cursor.execute("""
                SELECT 
                    p.id, p.product_code, p.name,
                    p.current_quantity, p.price,
                    p.reorder_threshold, c.name AS category,
                    (p.price * p.current_quantity) AS stock_value
                FROM products p
                LEFT JOIN categories c ON c.id = p.category_id
                WHERE p.archived = FALSE
                ORDER BY c.name, p.name;
            """)

            records = cursor.fetchall()

            return {
                "report_type": "inventory_snapshot",
                "generated_at": datetime.now(),
                "total_products": len(records),
                "products": records,
                "total_stock_value": sum(r["stock_value"] for r in records)
            }

        finally:
            cursor.close()
            conn.close()
