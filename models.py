from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .connection import Base

class Role(Base):
    __tablename__ = "roles"
    role_id = Column(Integer, primary_key=True)
    role_name = Column(String, nullable=False)
    allowed_actions = Column(String)  

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id"))

    role = relationship("Role", back_populates="users")


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    code_prefix = Column(String(10), nullable=True)



class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    category = relationship("Category")
    price = Column(Float, nullable=False)
    current_quantity = Column(Integer, default=0)
    reorder_threshold = Column(Integer, default=0)
    code = Column(String(50))
    updated_by_user_id = Column(Integer)
    updated_at = Column(String)

    


class SaleTransaction(Base):
    __tablename__ = "sales_transactions"

    transaction_id = Column(Integer, primary_key=True)
    cashier_id = Column(Integer, ForeignKey("users.user_id"))
    date = Column(DateTime, default=datetime.utcnow)
    subtotal = Column(Float)
    tax = Column(Float)
    total = Column(Float)

    items = relationship("SaleItem", back_populates="transaction")


class SaleItem(Base):
    __tablename__ = "sale_items"

    sale_item_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    transaction_id = Column(Integer, ForeignKey("sales_transactions.transaction_id"))
    quantity = Column(Integer, nullable=False)
    price_at_sale = Column(Float, nullable=False)

    transaction = relationship("SaleTransaction", back_populates="items")


class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    product = relationship("Product")
    alert_type = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")
