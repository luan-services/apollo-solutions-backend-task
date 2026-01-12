from fastapi import APIRouter
from sqlmodel import select, func
from app.config.database import SessionDep
from app.models.category import Category
from app.models.product import Product
from app.models.sale import Sale

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/revenue")
async def get_dashboard_revenue(session: SessionDep):
    total_categories = session.exec(select(func.count(Category.id))).one()

    if total_categories is None:
        total_categories = 0

    total_products = session.exec(select(func.count(Product.id))).one()

    if total_products is None:
        total_products = 0

    total_sales = session.exec(select(func.count(Sale.id))).one()
    
    if total_sales is None:
        total_sales = 0

    total_revenue = session.exec(select(func.sum(Sale.total_price))).one()
    
    if total_revenue is None:
        total_revenue = 0

    sales = session.exec(select(Sale)).all()
    
    sales_by_month_dict = {}
    
    for sale in sales:
        month_key = sale.date.strftime("%Y-%m")
        current_val = sales_by_month_dict.get(month_key, 0)
        sales_by_month_dict[month_key] = current_val + sale.total_price

    monthly_data = []

    for key, value in sorted(sales_by_month_dict.items()):
        monthly_data.append({"date": key, "total": value} )

    return {
        "summary": {
            "total_categories": total_categories,
            "total_products": total_products,
            "total_sales": total_sales,
            "total_revenue": total_revenue
        },
        "charts": {
            "monthly_revenue": monthly_data
        }
    }