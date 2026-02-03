from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..auth import require_role
from ..database import get_db
from ..models import OperationLog, Order, OrderItem, Product, ProductAttributeOption, User
from ..schemas import OrderCreate, OrderRead, OrderUpdate

router = APIRouter(prefix="/api/orders", tags=["orders"])


def build_order_code(db: Session, user: User, product: Product) -> str:
    prefix = user.order_prefix or "SA"
    category = product.category.name if product.category else "UNCAT"
    date_code = datetime.utcnow().strftime("%y%m%d")
    existing_codes = (
        db.query(Order.order_code)
        .filter(
            Order.sales_id == user.id,
            func.date(Order.created_at) == datetime.utcnow().date(),
        )
        .all()
    )
    seq = 1
    if existing_codes:
        parsed = []
        for (code,) in existing_codes:
            parts = code.split("-")
            if len(parts) == 4 and parts[-1].isdigit():
                parsed.append(int(parts[-1]))
        if parsed:
            seq = max(parsed) + 1
    return f"{prefix}-{category}-{date_code}-{seq:03d}"


@router.get("", response_model=list[OrderRead])
def list_orders(db: Session = Depends(get_db), user=Depends(require_role("sales", "admin"))):
    query = db.query(Order).filter(Order.sales_id == user.id) if user.role == "sales" else db.query(Order)
    return query.order_by(Order.created_at.desc()).all()


@router.post("", response_model=OrderRead)
def create_order(payload: OrderCreate, db: Session = Depends(get_db), user=Depends(require_role("sales", "admin"))):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    options = (
        db.query(ProductAttributeOption)
        .filter(ProductAttributeOption.id.in_(payload.selected_options))
        .all()
    )
    if len(options) != len(payload.selected_options):
        raise HTTPException(status_code=400, detail="属性选项不完整")
    total_price = product.base_price + sum(option.price_delta for option in options)
    total_price *= payload.qty
    remark_image_url = payload.remark_image_url
    if payload.remark_images:
        remark_image_url = ",".join(payload.remark_images)
    order = Order(
        order_code=build_order_code(db, user, product),
        sales_id=user.id,
        product_id=product.id,
        qty=payload.qty,
        total_price=total_price,
        distributor=payload.distributor,
        custom_order_code=payload.custom_order_code,
        remark_text=payload.remark_text,
        remark_image_url=remark_image_url,
    )
    db.add(order)
    db.flush()
    for option in options:
        db.add(
            OrderItem(
                order_id=order.id,
                attribute_name=option.attribute.name,
                option_label=option.label,
                price_delta=option.price_delta,
                option_image_url=option.image_url,
            )
        )
    db.add(
        OperationLog(
            user_id=user.id,
            role=user.role,
            action="create_order",
            detail=order.order_code,
        )
    )
    db.commit()
    db.refresh(order)
    return order


@router.put("/{order_id}", response_model=OrderRead)
def update_order(order_id: int, payload: OrderUpdate, db: Session = Depends(get_db), user=Depends(require_role("sales", "admin"))):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if user.role == "sales" and order.sales_id != user.id:
        raise HTTPException(status_code=403, detail="无权限")
    if payload.qty is not None:
        order.qty = payload.qty
    if payload.distributor is not None:
        order.distributor = payload.distributor
    if payload.custom_order_code is not None:
        order.custom_order_code = payload.custom_order_code
    if payload.remark_text is not None:
        order.remark_text = payload.remark_text
    if payload.remark_image_url is not None:
        order.remark_image_url = payload.remark_image_url
    if payload.remark_images is not None:
        order.remark_image_url = ",".join(payload.remark_images)
    if payload.selected_options is not None:
        options = (
            db.query(ProductAttributeOption)
            .filter(ProductAttributeOption.id.in_(payload.selected_options))
            .all()
        )
        if len(options) != len(payload.selected_options):
            raise HTTPException(status_code=400, detail="属性选项不完整")
        order.items = []
        for option in options:
            order.items.append(
                OrderItem(
                    attribute_name=option.attribute.name,
                    option_label=option.label,
                    price_delta=option.price_delta,
                    option_image_url=option.image_url,
                )
            )
        order.total_price = (order.product.base_price + sum(option.price_delta for option in options)) * order.qty
    db.add(
        OperationLog(
            user_id=user.id,
            role=user.role,
            action="update_order",
            detail=order.order_code,
        )
    )
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db), user=Depends(require_role("sales", "admin"))):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if user.role == "sales" and order.sales_id != user.id:
        raise HTTPException(status_code=403, detail="无权限")
    db.delete(order)
    db.add(
        OperationLog(
            user_id=user.id,
            role=user.role,
            action="delete_order",
            detail=order.order_code,
        )
    )
    db.commit()
    return {"ok": True}
