from fastapi import APIRouter

# https://fastapi.tiangolo.com/tutorial/bigger-applications/#another-module-with-apirouter

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/")
async def read_Products():
    return {"product" : "get endpoint"}

@router.post("/")
async def create_products():
    return {"product" : "create endpoint"}

@router.put("/{category_id}")
async def create_products():
    return {"product" : "update endpoint"}

@router.delete("/{category_id}")
async def delete_products():
    return {"product" : "delete endpoint"}
