from sqlmodel import SQLModel, Field, Relationship
from typing import List, TYPE_CHECKING

# https://fastapi.tiangolo.com/tutorial/sql-databases/#update-the-app-with-multiple-models
# https://github.com/fastapi/full-stack-fastapi-template/blob/master/backend/app/models.py

if TYPE_CHECKING:
    from .category import Category
    from .sale import Sale

class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: str
    price: float
    brand: str
    
    # foreign key, every sale must have a category id
    category_id: int = Field(foreign_key="category.id")
    
    # we must set the relationship here, this does not create a table, it only works as a helper if you want to do product.sales
    category: "Category" = Relationship(back_populates="products")
    sales: List["Sale"] = Relationship(back_populates="product")