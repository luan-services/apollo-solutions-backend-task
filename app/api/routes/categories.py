from fastapi import APIRouter, HTTPException, File, UploadFile
import pandas as pd
import io
from sqlmodel import select
from typing import List
from app.config.database import SessionDep
from app.models.category import Category

# https://fastapi.tiangolo.com/tutorial/bigger-applications/#another-module-with-apirouter

router = APIRouter(prefix="/categories", tags=["categories"])

# SessionDep must be passed to all routes function, it is a abreviation of the session object on database.py and it is used to comunicate with the db
# response_model is the same as a 'schema' for the response on the db, it ensures the responses are exactly an Category object

@router.get("/", response_model=List[Category])
def read_categories(session: SessionDep):
    return session.exec(select(Category)).all()

@router.get("/{category_id}", response_model=Category)
def read_category(category_id: int, session: SessionDep):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category Not Found")
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
async def import_categories_csv(session: SessionDep, file: UploadFile):
    # if it is not a .csv file, raise Error
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File Must be a CSV")

    contents = await file.read() 
    
    try:
        df = pd.read_csv(io.BytesIO(contents))
        df = df[['id', 'name']].dropna() 

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Reading CSV: {str(e)}")

    # getting all ids on the csv and turning into array
    csv_ids = df['id'].tolist()
    # searching on the database all ids that already exists
    statement = select(Category.id).where(Category.id.in_(csv_ids))
    existing_ids = session.exec(statement).all()
    # turning the list of ids into a set is a good practice to reduce search time
    existing_ids_set = set(existing_ids)

    count = 0
    # store new categories to be added
    new_categories = []

    # turning into a dict
    records = df.to_dict(orient="records") 

    for row in records:
        if row['id'] not in existing_ids_set:
            category = Category(id=row['id'], name=row['name'])
            new_categories.append(category)
            count += 1
    
    # save all categories at once
    if new_categories:
        session.add_all(new_categories)
        session.commit()

    return {"message": f"Successfully added {count} new categories."}