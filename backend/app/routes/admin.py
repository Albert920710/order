from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..auth import get_password_hash, require_role
from ..database import get_db
from ..models import OperationLog, User
from ..schemas import OperationLogRead, UserRead, UserUpdate

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    return db.query(User).order_by(User.id.desc()).all()


@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    return target


@router.put("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    if payload.role is not None:
        target.role = payload.role
    if payload.order_prefix is not None:
        target.order_prefix = payload.order_prefix
    if payload.password:
        target.password_hash = get_password_hash(payload.password)
    if payload.is_active is not None:
        target.is_active = payload.is_active
    if payload.is_approved is not None:
        target.is_approved = payload.is_approved
    db.add(
        OperationLog(
            user_id=user.id,
            role=user.role,
            action="update_user",
            detail=target.username,
        )
    )
    db.commit()
    db.refresh(target)
    return target


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    if target.role == "admin":
        raise HTTPException(status_code=400, detail="不可删除管理员账号")
    db.delete(target)
    db.add(OperationLog(user_id=user.id, role=user.role, action="delete_user", detail=target.username))
    db.commit()
    return {"ok": True}

@router.post("/users/{user_id}/approve", response_model=UserRead)
def approve_user(user_id: int, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    target.is_approved = True
    db.add(OperationLog(user_id=user.id, role=user.role, action="approve_user", detail=target.username))
    db.commit()
    db.refresh(target)
    return target


@router.post("/users/{user_id}/prefix", response_model=UserRead)
def update_order_prefix(user_id: int, prefix: str, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    if len(prefix) > 4:
        raise HTTPException(status_code=400, detail="前缀过长")
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="用户不存在")
    target.order_prefix = prefix
    db.add(OperationLog(user_id=user.id, role=user.role, action="update_prefix", detail=prefix))
    db.commit()
    db.refresh(target)
    return target


@router.get("/logs", response_model=list[OperationLogRead])
def list_logs(db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    return db.query(OperationLog).order_by(OperationLog.created_at.desc()).all()
