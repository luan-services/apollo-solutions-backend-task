from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config.database import create_db_and_tables
from app.api.main import api_router

# importing models for create_db_and_tables to work
from app.models.category import Category
from app.models.product import Product
from app.models.sale import Sale

# https://fastapi.tiangolo.com/advanced/events/#lifespan

""" a context manager in Python is something that you can use in a with statement, the first part of the function, before the 
yield, will be executed before the application starts. and the part after the yield will be executed after the application has finished. """
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database and tables...")
    create_db_and_tables()
    yield
    # code here will be executed after the app is finished.
    print("Shutting down database...")

app = FastAPI(
    title="SmartMart Solutions API",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Hello World!"}