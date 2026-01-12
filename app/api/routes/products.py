from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd
import io
from sqlmodel import select
from typing import List
from app.config.database import SessionDep
from app.models.product import Product


# https://fastapi.tiangolo.com/tutorial/bigger-applications/#another-module-with-apirouter

router = APIRouter(prefix="/products", tags=["products"])

# SessionDep must be passed to all routes function, it is a abreviation of the session object on database.py and it is used to comunicate with the db
# response_model is the same as a 'schema' for the response on the db, it ensures the responses are exactly an Product object

@router.get("/", response_model=List[Product])
async def read_products(session: SessionDep, category_id: int | None = None, brand: str | None  = None, min_price: float | None  = None, max_price: float | None  = None):
    query = select(Product)

    if category_id:
        query = query.where(Product.category_id == category_id)
    if brand:
        query = query.where(Product.brand == brand)

    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    
    return session.exec(query).all()

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
async def import_products_csv(session: SessionDep, file: UploadFile):
    # if it is not a .csv file, raise Error
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File Must be a CSV")

    contents = await file.read()
    
    try:
        df = pd.read_csv(io.BytesIO(contents))
        df = df[['id', 'name', 'description', 'price', 'brand', 'category_id']].dropna()

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Reading CSV: {str(e)}")

    # getting all ids on the csv and turning into array
    csv_ids = df['id'].tolist()
    # searching on the database all ids that already exists
    statement = select(Product.id).where(Product.id.in_(csv_ids))
    # turning the list of ids into a set is a good practice to reduce search time
    existing_ids = session.exec(statement).all()
    existing_ids_set = set(existing_ids)

    count = 0
    # store new products to be added
    new_products = []
    
    # turning into a dict
    records = df.to_dict(orient="records")

    for row in records:
        if row['id'] not in existing_ids_set:
            product = Product(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                price=float(row['price']), 
                brand=row['brand'],
                category_id=int(row['category_id'])
            )
            new_products.append(product)
            count += 1

    # save all categories at once
    if new_products:
        session.add_all(new_products)
        session.commit()

    return {"message": f"Successfully added {count} new products."}