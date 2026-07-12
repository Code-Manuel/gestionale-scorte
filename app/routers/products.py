from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import create_product, delete_product, get_product, get_products, search_products, update_product
from app.database import get_db
from app.schemas import ProductCreate, ProductDetailResponse, ProductResponse, ProductStockStatus, ProductUpdate
from app.services.reorder import calculate_reorder

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(product: ProductCreate, db: Session = Depends(get_db)) -> ProductResponse:
    return create_product(db, product)


@router.get("", response_model=list[ProductResponse])
def list_products(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200), db: Session = Depends(get_db)) -> list[ProductResponse]:
    return get_products(db, skip=skip, limit=limit)


@router.get("/search", response_model=list[ProductResponse])
def search_products_endpoint(
    q: str = Query(..., min_length=1, description="Nome o codice del prodotto"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
) -> list[ProductResponse]:
    return search_products(db, q, limit=limit)


@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product_detail(product_id: int, db: Session = Depends(get_db)) -> ProductDetailResponse:
    product = get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    movements = [
        {"movement_type": movement.movement_type, "quantity": movement.quantity, "movement_date": movement.movement_date}
        for movement in product.movements
    ]
    reorder_info = calculate_reorder(movements, product.current_stock)
    stock_status = ProductStockStatus(
        product_id=product.id,
        current_stock=product.current_stock,
        reorder_point=reorder_info["soglia_riordino"],
        needs_reorder=reorder_info["serve_ordine"],
        suggested_order_quantity=reorder_info["quantita_da_ordinare"],
    )
    return ProductDetailResponse(
        id=product.id,
        name=product.name,
        category=product.category,
        unit=product.unit,
        current_stock=product.current_stock,
        reorder_point=reorder_info["soglia_riordino"],
        expiry_date=product.expiry_date,
        created_at=product.created_at,
        updated_at=product.updated_at,
        stock_status=stock_status,
    )


@router.put("/{product_id}", response_model=ProductResponse)
def update_product_endpoint(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)) -> ProductResponse:
    db_product = get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return update_product(db, db_product, product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_endpoint(product_id: int, db: Session = Depends(get_db)) -> None:
    deleted = delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
