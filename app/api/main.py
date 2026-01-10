from fastapi import APIRouter
from app.api.routes import categories, products, sales

api_router = APIRouter()

api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(sales.router)