import sale_item as ti
import sale_transaction_crud as stc


class sale_transaction:
    """Database CRUD operations for sale_transaction table"""

    def __init__(self, tax_rate, discount_rate, inventory_db, product_db, sale_tx_crud: stc.sale_transaction_crud):
        self.tax_rate = tax_rate
        self.discount_rate = discount_rate
        self.inventory_db = inventory_db
        self.product_db = product_db
        self.sale_tx_crud = sale_tx_crud
        self.sale_items = []  # List to hold items in the current transaction
    
    def add_sale_item(self, product, quantity):
        """Add an item to the current sale transaction"""
        # Here we would typically check inventory, calculate totals, etc.
        self.sale_items.append(ti.sale_item(product, quantity))
    
    def calculate_subtotal(self):
        """Calculate the total amount for the current transaction"""
        total = 0
        for item in self.sale_items:
            total += item.price
        return total
    
    def calculate_tax(self, subtotal):
        """Calculate tax based on the subtotal"""
        return subtotal * self.tax_rate
    
    def calculate_discount(self, subtotal):
        """Calculate discount based on the subtotal"""
        return subtotal * self.discount_rate
    
    def calculate_transaction_data(self):
        """Calculate subtotal, tax, discount, and total for the transaction"""
        subtotal = self.calculate_subtotal()
        tax = self.calculate_tax(subtotal)
        discount = self.calculate_discount(subtotal)
        total = subtotal + tax - discount
        return {
            "subtotal": subtotal,
            "tax": tax,
            "discount": discount,
            "total": total
        }
    
    def finalize_transaction(self, cashier_id):
        """Finalize the transaction and save to database"""
        transaction_data = self.calculate_transaction_data()

        #update inventory
        for item in self.sale_items:
            product = self.product_db.search_product_sales(item.product["name"])
            #convert realdict to normal dict
            product = dict(product)
            quantity_available = product["current_quantity"]
            updated_quantity = quantity_available - item.quantity
            
            self.inventory_db.update_product(
                product_id=item.product["id"],
                quantity=updated_quantity
            )

        # Here we would insert the transaction and its items into the database
        date = 'NOW()'  # In real code, use the current date/time
        self.sale_tx_crud.add_transaction(date, cashier_id, transaction_data, self.sale_items)
        return transaction_data
    



    # Further methods for sale_transaction would go here