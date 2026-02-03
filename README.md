# 企业销售下单系统（内网部署）

## 项目结构

- `backend/`：FastAPI + MySQL 后端
- `frontend/`：Vue 3 + Element Plus 前端
- `sql/`：数据库建表与初始化说明

## 后端启动

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端 `vite` 已配置 `/api`、`/media` 代理到 `http://localhost:8000`。

## 数据库初始化

1. 创建数据库与表结构：

```bash
mysql -u root -p < sql/schema.sql
```

2. 创建初始化账号（请先安装 `passlib[bcrypt]` 生成密码哈希）：

```bash
python - <<'PY'
from passlib.context import CryptContext
pwd=CryptContext(schemes=['bcrypt_sha256'], deprecated='auto')
for username, password, role, prefix in [
    ('sales01','Sales123!','sales','SA'),
    ('product01','Product123!','product_manager',None),
    ('admin01','Admin123!','admin','AD'),
]:
    print(username, pwd.hash(password), role, prefix)
PY
```

将生成的密码哈希填入 `sql/seed.sql` 并执行：

```bash
mysql -u root -p < sql/seed.sql
```

## 测试账号建议

- 业务员：`sales01` / `Sales123!`
- 产品配置员：`product01` / `Product123!`
- 管理员：`admin01` / `Admin123!`

> 注意：前端已实现 30 天游客缓存自动登录；若出现 `bcrypt_sha256` 校验异常，请确认数据库内密码哈希与 `passlib[bcrypt]` 生成一致。

## 图片索引

产品图片应放在 `media/` 目录。管理员在产品新增完成后执行：

```bash
python backend/scripts/build_image_index.py --media-dir media --output media/image_index.pkl
```

索引完成后，图片搜索接口将读取该索引（当前后端接口已预留）。
