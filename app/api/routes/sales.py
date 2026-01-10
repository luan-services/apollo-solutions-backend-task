from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd
import io
from datetime import datetime
from sqlmodel import select
from typing import List
from app.config.database import SessionDep
from app.models.sale import Sale

# https://fastapi.tiangolo.com/tutorial/bigger-applications/#another-module-with-apirouter

router = APIRouter(prefix="/sales", tags=["sales"])

@router.get("/", response_model=List[Sale])
async def read_sales(session: SessionDep):
    return session.exec(select(Sale)).all()

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
def import_sales_csv(session: SessionDep, file: UploadFile = File(...)):
    contents = file.file.read()
    df = pd.read_csv(io.BytesIO(contents))
    count = 0
    for index, row in df.iterrows():
        if not session.get(Sale, row['id']):
            sale_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
            sale = Sale(
                id=row['id'],
                product_id=int(row['product_id']),
                quantity=int(row['quantity']),
                total_price=float(row['total_price']),
                date=sale_date
            )
            session.add(sale)
            count += 1
    session.commit()
    return {"message": f"Succesfully Added {count} Sales"}