from fastapi import APIRouter

# https://fastapi.tiangolo.com/tutorial/bigger-applications/#another-module-with-apirouter

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/")
async def read_categories():
    return {"category" : "get endpoint"}

@router.post("/")
async def create_category():
    return {"category" : "create endpoint"}

@router.put("/{category_id}")
async def create_category():
    return {"category" : "update endpoint"}

@router.delete("/{category_id}")
async def delete_category():
    return {"category" : "delete endpoint"}
