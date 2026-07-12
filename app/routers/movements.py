from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import create_movement, list_movements
from app.database import get_db
from app.models import Product
from app.schemas import StockMovementCreate, StockMovementResponse

router = APIRouter(prefix="/movements", tags=["movements"])


@router.post("", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
def create_movement_endpoint(movement: StockMovementCreate, db: Session = Depends(get_db)) -> StockMovementResponse:
    try:
        created_movement = create_movement(db, movement)
        product = db.get(Product, movement.product_id)
        return StockMovementResponse(
            id=created_movement.id,
            product_id=created_movement.product_id,
            movement_type=created_movement.movement_type,
            quantity=created_movement.quantity,
            movement_date=created_movement.movement_date,
            note=created_movement.note,
            created_at=created_movement.created_at,
            name=product.name if product else None,
            unit=product.unit if product else None,
            current_stock=product.current_stock if product else None,
        )
    except ValueError as exc:
        if str(exc) == "Product not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("", response_model=list[StockMovementResponse])
def list_movements_endpoint(
    product_id: int | None = Query(None, gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[StockMovementResponse]:
    movements = list_movements(db, product_id=product_id)
    return movements[skip : skip + limit]
