from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..auth import authenticate_user, create_access_token, get_password_hash
from ..database import get_db
from ..models import OperationLog, User
from ..schemas import Token, UserCreate, UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    if not form_data.username and not form_data.password:
        raise HTTPException(status_code=400, detail="请输入账号密码后登录")
    if not form_data.password:
        raise HTTPException(status_code=400, detail="请输入正确的密码后登录")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="账号或密码错误")
    if not user.is_approved:
        raise HTTPException(status_code=403, detail="账号等待管理员审核")
    user.last_login_at = datetime.utcnow()
    user.last_login_location = "内网"
    db.add(user)
    db.add(OperationLog(user_id=user.id, role=user.role, action="login", detail="用户登录"))
    db.commit()
    access_token = create_access_token({"sub": user.username, "role": user.role})
    return Token(access_token=access_token)


@router.post("/register", response_model=UserRead)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if payload.role not in {"sales", "product_manager"}:
        raise HTTPException(status_code=400, detail="非法角色")
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="账号已存在")
    user = User(
        name=payload.name,
        username=payload.username,
        role=payload.role,
        password_hash=get_password_hash(payload.password),
        is_approved=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.add(
        OperationLog(
            user_id=user.id,
            role="system",
            action="register",
            detail=f"注册账号 {payload.username}",
        )
    )
    db.commit()
    return user
