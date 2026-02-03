from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth import require_role
from ..database import get_db
from ..models import Customer, OperationLog, User
from ..schemas import CustomerCreate, CustomerRead, CustomerUpdate, SalesRead

router = APIRouter(prefix="/api/customers", tags=["customers"])


def normalize_country(country: str) -> str:
    return country.strip().upper()


def build_full_name(name: str, country: str) -> str:
    return f"{name.strip()}_{normalize_country(country)}"


@router.get("", response_model=list[CustomerRead])
def list_customers(db: Session = Depends(get_db), user=Depends(require_role("admin", "finance"))):
    return db.query(Customer).order_by(Customer.id.desc()).all()


@router.get("/assigned", response_model=list[CustomerRead])
def list_assigned_customers(
    db: Session = Depends(get_db),
    user=Depends(require_role("sales", "admin", "finance")),
):
    if user.role == "sales":
        return sorted(user.assigned_customers, key=lambda item: item.id, reverse=True)
    return db.query(Customer).order_by(Customer.id.desc()).all()


@router.get("/sales-users", response_model=list[SalesRead])
def list_sales_users(db: Session = Depends(get_db), user=Depends(require_role("admin", "finance"))):
    return db.query(User).filter(User.role == "sales").order_by(User.id.desc()).all()


@router.post("", response_model=CustomerRead)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "finance")),
):
    full_name = build_full_name(payload.name, payload.country)
    existing = db.query(Customer).filter(Customer.full_name == full_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="客户已存在")
    customer = Customer(
        name=payload.name.strip(),
        country=normalize_country(payload.country),
        customer_type=payload.customer_type,
        full_name=full_name,
    )
    if payload.assigned_user_ids:
        sales_users = (
            db.query(User)
            .filter(User.id.in_(payload.assigned_user_ids), User.role == "sales")
            .all()
        )
        customer.assigned_users = sales_users
    db.add(customer)
    db.add(
        OperationLog(
            user_id=user.id,
            role=user.role,
            action="create_customer",
            detail=customer.full_name,
        )
    )
    db.commit()
    db.refresh(customer)
    return customer


@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "finance")),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    if payload.name is not None:
        customer.name = payload.name.strip()
    if payload.country is not None:
        customer.country = normalize_country(payload.country)
    if payload.customer_type is not None:
        customer.customer_type = payload.customer_type
    if payload.name is not None or payload.country is not None:
        full_name = build_full_name(customer.name, customer.country)
        existing = (
            db.query(Customer)
            .filter(Customer.full_name == full_name, Customer.id != customer_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="客户已存在")
        customer.full_name = full_name
    if payload.assigned_user_ids is not None:
        sales_users = (
            db.query(User)
            .filter(User.id.in_(payload.assigned_user_ids), User.role == "sales")
            .all()
        )
        customer.assigned_users = sales_users
    db.add(
        OperationLog(
            user_id=user.id,
            role=user.role,
            action="update_customer",
            detail=customer.full_name,
        )
    )
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin", "finance")),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    db.delete(customer)
    db.add(
        OperationLog(
            user_id=user.id,
            role=user.role,
            action="delete_customer",
            detail=customer.full_name,
        )
    )
    db.commit()
    return {"ok": True}
