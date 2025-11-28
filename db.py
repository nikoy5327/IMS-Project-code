# db.py
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env from project root if present

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "carols_ims"),
    "user": os.getenv("DB_USER", "ims_user"),
    "password": os.getenv("DB_PASS", "password123"),
}

# Import the postgres CRUD class you already created
from inventory_crud_pg import InventoryCRUD

# Create a single module-level instance
crud = InventoryCRUD(
    host=DB_CONFIG["host"],
    database=DB_CONFIG["database"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"]
)
