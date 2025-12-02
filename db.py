# backend/db.py
import os
from inventory_crud_pg import InventoryCRUD

# Get database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "inventory_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Initialize the CRUD instance
crud = InventoryCRUD(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

# Re-export the connect method
connect = crud.connect

# Re-export CRUD methods
get_product = crud.get_product
list_products = crud.list_products
add_product = crud.add_product
update_product = crud.update_product
delete_product = crud.delete_product
