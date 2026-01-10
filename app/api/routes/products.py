from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd
import io
from sqlmodel import select
from typing import List
from app.config.database import SessionDep
from app.models.product import Product


# https://fastapi.tiangolo.com/tutorial/bigger-applications/#another-module-with-apirouter

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[Product])
async def read_products(session: SessionDep):
    return session.exec(select(Product)).all()

@router.get("/{product_id}", response_model=Product)
def read_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product Not Found")
    return product

@router.post("/", response_model=Product)
async def create_product(product: Product, session: SessionDep):
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: int, product_data: Product, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product Not Found")
    
    input_data = product_data.model_dump(exclude_unset=True)
    product.sqlmodel_update(input_data)
    
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@router.delete("/{product_id}")
async def delete_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product Not Found")
    session.delete(product)
    session.commit()
    return {"message": "Product Deleted"}

@router.post("/import_csv")
def import_products_csv(session: SessionDep, file: UploadFile = File(...)):
    contents = file.file.read()
    df = pd.read_csv(io.BytesIO(contents))
    count = 0
    for index, row in df.iterrows():
        if not session.get(Product, row['id']):
            product = Product(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                price=float(row['price']),
                brand=row['brand'],
                category_id=int(row['category_id'])
            )
            session.add(product)
            count += 1
    session.commit()
    return {"message": f"Succesfully Added {count} Products"}