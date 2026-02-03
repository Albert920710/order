from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Float,
)
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False)
    order_prefix = Column(String(4), nullable=True)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    last_login_at = Column(DateTime, nullable=True)
    last_login_location = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="sales")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    short_description = Column(Text, nullable=True)
    brand = Column(String(80), nullable=True)
    material = Column(String(80), nullable=True)
    base_price = Column(Float, default=0)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    remark_enabled = Column(Boolean, default=True)
    distributor_enabled = Column(Boolean, default=True)
    custom_order_code_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    attributes = relationship(
        "ProductAttribute", back_populates="product", cascade="all, delete-orphan"
    )


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    image_url = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False)

    product = relationship("Product", back_populates="images")


class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    name = Column(String(100), nullable=False)
    sort_order = Column(Integer, default=0)

    product = relationship("Product", back_populates="attributes")
    options = relationship(
        "ProductAttributeOption", back_populates="attribute", cascade="all, delete-orphan"
    )


class ProductAttributeOption(Base):
    __tablename__ = "product_attribute_options"

    id = Column(Integer, primary_key=True)
    attribute_id = Column(Integer, ForeignKey("product_attributes.id"), nullable=False)
    label = Column(String(120), nullable=False)
    price_delta = Column(Float, default=0)
    image_url = Column(String(255), nullable=True)
    is_default = Column(Boolean, default=False)

    attribute = relationship("ProductAttribute", back_populates="options")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_code = Column(String(80), unique=True, nullable=False)
    sales_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    status = Column(String(40), default="created")
    qty = Column(Integer, default=1)
    total_price = Column(Float, default=0)
    distributor = Column(String(120), nullable=True)
    custom_order_code = Column(String(120), nullable=True)
    remark_text = Column(Text, nullable=True)
    remark_image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sales = relationship("User", back_populates="orders")
    product = relationship("Product")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    attribute_name = Column(String(120), nullable=False)
    option_label = Column(String(120), nullable=False)
    price_delta = Column(Float, default=0)
    option_image_url = Column(String(255), nullable=True)

    order = relationship("Order", back_populates="items")


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(30), nullable=False)
    action = Column(String(200), nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
