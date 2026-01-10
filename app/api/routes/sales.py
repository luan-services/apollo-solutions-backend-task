from fastapi import APIRouter

# https://fastapi.tiangolo.com/tutorial/bigger-applications/#another-module-with-apirouter

router = APIRouter(prefix="/sales", tags=["sales"])

@router.get("/")
async def read_sales():
    return {"sale" : "get endpoint"}

@router.post("/")
async def create_sale():
    return {"sale" : "create endpoint"}

@router.put("/{category_id}")
async def create_sale():
    return {"sale" : "update endpoint"}

@router.delete("/{category_id}")
async def delete_sale():
    return {"sale" : "delete endpoint"}
