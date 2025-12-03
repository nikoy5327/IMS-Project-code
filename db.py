import os
from dotenv import load_dotenv
from inventory_crud_pg import InventoryCRUD

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "carols_ims")
DB_USER = os.getenv("DB_USER", "ims_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password123")

print(f"Database config: host={DB_HOST}, db={DB_NAME}, user={DB_USER}")
crud = InventoryCRUD(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

connect = crud.connect



add_product = crud.add_product
update_product = crud.update_product
delete_product = crud.delete_product
