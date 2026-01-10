from fastapi import APIRouter, HTTPException, File, UploadFile
import pandas as pd
import io
from sqlmodel import select
from typing import List
from app.config.database import SessionDep
from app.models.category import Category

# https://fastapi.tiangolo.com/tutorial/bigger-applications/#another-module-with-apirouter

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[Category])
def read_categories(session: SessionDep):
    return session.exec(select(Category)).all()

@router.get("/{category_id}", response_model=Category)
def read_category(category_id: int, session: SessionDep):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return category

@router.post("/", response_model=Category)
async def create_category(category: Category, session: SessionDep):
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.put("/{category_id}", response_model=Category)
async def update_category(category_id: str, category_data: Category, session: SessionDep):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category Not Found")
    
    input_data = category_data.model_dump(exclude_unset=True)
    category.sqlmodel_update(input_data)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.delete("/{category_id}")
async def delete_category(category_id: int, session: SessionDep):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category Not Found")
    session.delete(category)
    session.commit()
    return {"message": "Category Deleted"}

@router.post("/import_csv")
def import_categories_csv( session: SessionDep, file: UploadFile = File(...)):
    contents = file.file.read()
    df = pd.read_csv(io.BytesIO(contents))
    count = 0
    for index, row in df.iterrows():
        if not session.get(Category, row['id']):
            category = Category(id=row['id'], name=row['name'])
            session.add(category)
            count += 1
    session.commit()
    return {"message": f"Succesfully Added {count} Categories"}