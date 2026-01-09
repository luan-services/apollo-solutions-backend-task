from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config.database import create_db_and_tables

# https://fastapi.tiangolo.com/advanced/events/#lifespan

# import models here later

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

@app.get("/")
def root():
    return {"message": "Hello World!"}