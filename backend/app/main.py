from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from .routes import admin, auth, customers, orders, products, search

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sales Order System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(search.router)
app.include_router(customers.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
