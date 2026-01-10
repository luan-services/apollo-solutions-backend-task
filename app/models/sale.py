from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import TYPE_CHECKING

# https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
# https://github.com/fastapi/full-stack-fastapi-template/blob/master/backend/app/models.py

if TYPE_CHECKING:
    from .product import Product

class Sale(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    quantity: int
    total_price: float
    date: date
    
    # foreign key, every sale must have a product id
    product_id: int = Field(foreign_key="product.id")

    # we must set the relationship here, this does not create a table, it only works as a helper if you want to do sale.product
    product: "Product" = Relationship(back_populates="sales")