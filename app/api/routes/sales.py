from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd
import io
from datetime import datetime, date
from sqlmodel import select
from typing import List
from app.config.database import SessionDep
from app.models.sale import Sale

# https://fastapi.tiangolo.com/tutorial/bigger-applications/#another-module-with-apirouter

router = APIRouter(prefix="/sales", tags=["sales"])

# SessionDep must be passed to all routes function, it is a abreviation of the session object on database.py and it is used to comunicate with the db
# response_model is the same as a 'schema' for the response on the db, it ensures the responses are exactly an Sale object

@router.get("/", response_model=List[Sale])
async def read_sales(session: SessionDep, product_id: int | None = None, start_date: date | None = None, end_date: date | None  = None):
    query = select(Sale)

    if product_id:
        query = query.where(Sale.product_id == product_id)
    
    if start_date:
        query = query.where(Sale.date >= start_date)
    if end_date:
        query = query.where(Sale.date <= end_date)

    query = query.order_by(Sale.date.desc())

    return session.exec(query).all()

@router.get("/{sale_id}", response_model=Sale)
def read_sale(sale_id: int, session: SessionDep):
    sale = session.get(Sale, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale Not Found")
    return sale

@router.post("/", response_model=Sale)
async def create_sale(sale: Sale, session: SessionDep):
    session.add(sale)
    session.commit()
    session.refresh(sale)
    return sale

@router.put("/{sale_id}", response_model=Sale)
async def update_sale(sale_id: int, sale_data: Sale, session: SessionDep):
    sale = session.get(Sale, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale Not Found")
    
    input_data = sale_data.model_dump(exclude_unset=True)
    sale.sqlmodel_update(input_data)
    
    session.add(sale)
    session.commit()
    session.refresh(sale)
    return sale

@router.delete("/{sale_id}")
async def delete_sale(sale_id: int, session: SessionDep):
    sale = session.get(Sale, sale_id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale Not Found")
    session.delete(sale)
    session.commit()
    return {"message": "Sale Deleted"}

@router.post("/import_csv")
async def import_sales_csv(session: SessionDep, file: UploadFile):
    # if it is not a .csv file, raise Error
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File Must be a CSV")

    contents = await file.read()

    try:
        df = pd.read_csv(io.BytesIO(contents))
        df = df[['id', 'product_id', 'quantity', 'total_price', 'date']].dropna()

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Reading CSV: {str(e)}")

    # getting all ids on the csv and turning into array
    csv_ids = df['id'].tolist()
    # searching on the database all ids that already exists
    statement = select(Sale.id).where(Sale.id.in_(csv_ids))
    existing_ids = session.exec(statement).all()
    # turning the list of ids into a set is a good practice to reduce search time
    existing_ids_set = set(existing_ids)

    count = 0
    # store new categories to be added
    new_sales = []

    # turning into a dict
    records = df.to_dict(orient="records")

    for row in records:
        if row['id'] not in existing_ids_set:
            try:
                sale_date = datetime.strptime(str(row['date']), '%Y-%m-%d').date()
            except ValueError:
                continue 

            sale = Sale(
                id=row['id'],
                product_id=int(row['product_id']),
                quantity=int(row['quantity']),
                total_price=float(row['total_price']),
                date=sale_date
            )
            new_sales.append(sale)
            count += 1

    # save all categories at once
    if new_sales:
        session.add_all(new_sales)
        session.commit()

    return {"message": f"Successfully added {count} new sales."}