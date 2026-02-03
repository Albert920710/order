from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pathlib import Path
from uuid import uuid4
import shutil
from sqlalchemy.orm import Session
from ..auth import get_current_user, require_role
from ..database import get_db
from ..models import Category, OperationLog, Product, ProductAttribute, ProductAttributeOption, ProductImage
from ..schemas import (
    CategoryRead,
    ProductAssetPayload,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)

router = APIRouter(prefix="/api/products", tags=["products"])

MEDIA_ROOT = Path("media")
MEDIA_ROOT.mkdir(exist_ok=True)


def mask_product_prices(products: list[Product]) -> list[Product]:
    for product in products:
        product.base_price = None
        for attribute in product.attributes:
            for option in attribute.options:
                option.price_delta = None
    return products


@router.get("", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db), user=Depends(get_current_user)):
    products = db.query(Product).order_by(Product.id.desc()).all()
    if user.role not in {"admin", "finance"}:
        return mask_product_prices(products)
    return products


@router.post("", response_model=ProductRead)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("product_manager", "admin", "finance")),
):
    data = payload.dict()
    if user.role not in {"admin", "finance"}:
        data["base_price"] = 0
    if data.get("base_price") is None:
        data["base_price"] = 0
    product = Product(**data)
    db.add(product)
    db.add(
        OperationLog(
            user_id=user.id,
            role=user.role,
            action="create_product",
            detail=payload.title,
        )
    )
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("product_manager", "admin", "finance")),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    for key, value in payload.dict(exclude_none=True).items():
        if key == "base_price" and user.role not in {"admin", "finance"}:
            continue
        setattr(product, key, value)
    db.add(
        OperationLog(
            user_id=user.id,
            role=user.role,
            action="update_product",
            detail=str(product_id),
        )
    )
    db.commit()
    db.refresh(product)
    return product


@router.post("/{product_id}/assets", response_model=ProductRead)
def update_product_assets(
    product_id: int,
    payload: ProductAssetPayload,
    db: Session = Depends(get_db),
    user=Depends(require_role("product_manager", "admin", "finance")),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    existing_price_map = {
        option.id: option.price_delta
        for attribute in product.attributes
        for option in attribute.options
    }
    product.images = [
        ProductImage(image_url=item.image_url, is_primary=item.is_primary)
        for item in payload.images
    ]
    product.attributes = []
    for attribute in payload.attributes:
        attr = ProductAttribute(name=attribute.name, sort_order=attribute.sort_order)
        for option in attribute.options:
            price_delta = option.price_delta if option.price_delta is not None else 0
            if user.role not in {"admin", "finance"}:
                if option.id in existing_price_map:
                    price_delta = existing_price_map[option.id]
                else:
                    price_delta = 0
            attr.options.append(
                ProductAttributeOption(
                    label=option.label,
                    price_delta=price_delta,
                    image_url=option.image_url,
                    is_default=option.is_default,
                )
            )
        product.attributes.append(attr)
    db.add(
        OperationLog(
            user_id=user.id,
            role=user.role,
            action="update_product_assets",
            detail=str(product_id),
        )
    )
    db.commit()
    db.refresh(product)
    return product


@router.post("/uploads")
def upload_media(
    file: UploadFile = File(...),
    user=Depends(require_role("product_manager", "admin", "finance")),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="缺少文件")
    suffix = Path(file.filename).suffix
    filename = f"{uuid4().hex}{suffix}"
    destination = MEDIA_ROOT / filename
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"url": f"/media/{filename}"}


@router.get("/categories", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name.asc()).all()


@router.post("/categories", response_model=CategoryRead)
def create_category(
    name: str,
    db: Session = Depends(get_db),
    user=Depends(require_role("product_manager", "admin", "finance")),
):
    existing = db.query(Category).filter(Category.name == name).first()
    if existing:
        return existing
    category = Category(name=name)
    db.add(category)
    db.add(
        OperationLog(
            user_id=user.id,
            role=user.role,
            action="create_category",
            detail=name,
        )
    )
    db.commit()
    db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    name: str,
    db: Session = Depends(get_db),
    user=Depends(require_role("product_manager", "admin", "finance")),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    category.name = name
    db.add(
        OperationLog(
            user_id=user.id,
            role=user.role,
            action="update_category",
            detail=name,
        )
    )
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("product_manager", "admin", "finance")),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    db.delete(category)
    db.add(
        OperationLog(
            user_id=user.id,
            role=user.role,
            action="delete_category",
            detail=str(category_id),
        )
    )
    db.commit()
    return {"ok": True}


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("product_manager", "admin", "finance")),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    db.delete(product)
    db.add(
        OperationLog(
            user_id=user.id,
            role=user.role,
            action="delete_product",
            detail=str(product_id),
        )
    )
    db.commit()
    return {"ok": True}
