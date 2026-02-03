from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    name: str
    username: str
    role: str
    order_prefix: Optional[str] = None


class UserCreate(BaseModel):
    name: str
    username: str
    password: str
    role: str


class UserRead(UserBase):
    id: int
    is_active: bool
    is_approved: bool
    last_login_at: Optional[datetime]
    last_login_location: Optional[str]

    class Config:
        from_attributes = True


class SalesRead(BaseModel):
    id: int
    name: str
    username: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    role: Optional[str] = None
    order_prefix: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None


class CategoryRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ProductImageRead(BaseModel):
    id: int
    image_url: str
    is_primary: bool

    class Config:
        from_attributes = True


class ProductAttributeOptionRead(BaseModel):
    id: int
    label: str
    price_delta: float
    image_url: Optional[str]
    is_default: bool = False

    class Config:
        from_attributes = True


class ProductAttributeRead(BaseModel):
    id: int
    name: str
    sort_order: int
    options: List[ProductAttributeOptionRead] = []

    class Config:
        from_attributes = True


class ProductRead(BaseModel):
    id: int
    title: str
    short_description: Optional[str]
    brand: Optional[str]
    material: Optional[str]
    base_price: float
    remark_enabled: bool
    distributor_enabled: bool
    custom_order_code_enabled: bool
    category: Optional[CategoryRead]
    images: List[ProductImageRead] = []
    attributes: List[ProductAttributeRead] = []

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    title: str
    short_description: Optional[str] = None
    brand: Optional[str] = None
    material: Optional[str] = None
    base_price: float
    category_id: Optional[int] = None
    remark_enabled: bool = True
    distributor_enabled: bool = True
    custom_order_code_enabled: bool = True


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = None
    brand: Optional[str] = None
    material: Optional[str] = None
    base_price: Optional[float] = None
    category_id: Optional[int] = None
    remark_enabled: Optional[bool] = None
    distributor_enabled: Optional[bool] = None
    custom_order_code_enabled: Optional[bool] = None


class ProductImagePayload(BaseModel):
    image_url: str
    is_primary: bool = False


class ProductAttributeOptionPayload(BaseModel):
    label: str
    price_delta: float = 0
    image_url: Optional[str] = None
    is_default: bool = False


class ProductAttributePayload(BaseModel):
    name: str
    sort_order: int = 0
    options: List[ProductAttributeOptionPayload] = []


class ProductAssetPayload(BaseModel):
    images: List[ProductImagePayload] = []
    attributes: List[ProductAttributePayload] = []


class OrderItemRead(BaseModel):
    id: int
    attribute_name: str
    option_label: str
    price_delta: float
    option_image_url: Optional[str]

    class Config:
        from_attributes = True


class OrderRead(BaseModel):
    id: int
    order_code: str
    status: str
    qty: int
    total_price: float
    distributor: Optional[str]
    custom_order_code: Optional[str]
    remark_text: Optional[str]
    remark_image_url: Optional[str]
    created_at: datetime
    sales: Optional[SalesRead]
    product: ProductRead
    items: List[OrderItemRead] = []

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    product_id: int
    qty: int
    selected_options: List[int]
    distributor: Optional[str] = None
    custom_order_code: Optional[str] = None
    remark_text: Optional[str] = None
    remark_image_url: Optional[str] = None
    remark_images: Optional[List[str]] = None


class OrderUpdate(BaseModel):
    qty: Optional[int] = None
    selected_options: Optional[List[int]] = None
    distributor: Optional[str] = None
    custom_order_code: Optional[str] = None
    remark_text: Optional[str] = None
    remark_image_url: Optional[str] = None
    remark_images: Optional[List[str]] = None


class OperationLogRead(BaseModel):
    id: int
    user_id: int
    role: str
    action: str
    detail: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
