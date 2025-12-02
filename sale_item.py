
class sale_item:
    """Database CRUD operations for sale_item table"""
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity
        self.price = product["price"] * quantity  # Total price for this item
