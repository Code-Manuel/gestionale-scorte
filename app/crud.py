from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Product, StockMovement
from app.schemas import ProductCreate, ProductUpdate, StockMovementCreate
from app.services.reorder import calculate_reorder


def create_product(db: Session, product: ProductCreate) -> Product:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products(db: Session, skip: int = 0, limit: int = 100) -> list[Product]:
    return db.scalars(select(Product).order_by(Product.name).offset(skip).limit(limit)).all()


def get_product(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


def search_products(db: Session, query: str, limit: int = 10) -> list[Product]:
    normalized_query = query.strip().lower()
    if not normalized_query:
        return []

    search_pattern = f"%{normalized_query}%"
    return db.scalars(
        select(Product)
        .where(
            Product.name.ilike(search_pattern)
            | Product.category.ilike(search_pattern)
            | Product.code.ilike(search_pattern)
            | Product.lot_number.ilike(search_pattern)
        )
        .order_by(Product.name)
        .limit(limit)
    ).all()


def update_product(db: Session, db_product: Product, product: ProductUpdate) -> Product:
    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    db_product = db.get(Product, product_id)
    if db_product is None:
        return False
    db.delete(db_product)
    db.commit()
    return True


def create_movement(db: Session, movement: StockMovementCreate) -> StockMovement:
    product = db.get(Product, movement.product_id)
    if product is None:
        raise ValueError("Product not found")

    if movement.movement_type == "scarico" and product.current_stock < movement.quantity:
        raise ValueError("Stock insufficiente per lo scarico richiesto")

    db_movement = StockMovement(**movement.model_dump())
    if movement.movement_type == "scarico":
        product.current_stock -= movement.quantity
    else:
        product.current_stock += movement.quantity

    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
    return db_movement


def list_movements(db: Session, product_id: int | None = None) -> list[StockMovement]:
    statement = select(StockMovement)
    if product_id is not None:
        statement = statement.where(StockMovement.product_id == product_id)
    statement = statement.order_by(StockMovement.movement_date.desc(), StockMovement.id.desc())
    return db.scalars(statement).all()


def get_alerts(db: Session) -> list[dict[str, Any]]:
    products = db.scalars(select(Product).order_by(Product.name)).all()
    alerts: list[dict[str, Any]] = []
    for product in products:
        movements = [
            {
                "movement_type": movement.movement_type,
                "quantity": movement.quantity,
                "movement_date": movement.movement_date,
            }
            for movement in product.movements
        ]
        reorder_info = calculate_reorder(movements, product.current_stock)
        if reorder_info["serve_ordine"]:
            alerts.append(
                {
                    "product_id": product.id,
                    "name": product.name,
                    "current_stock": product.current_stock,
                    "reorder_point": reorder_info["soglia_riordino"],
                    "suggested_order_quantity": reorder_info["quantita_da_ordinare"],
                    "urgency_ratio": round(product.current_stock / reorder_info["soglia_riordino"], 2)
                    if reorder_info["soglia_riordino"]
                    else 0.0,
                    "data_insufficient": bool(reorder_info.get("data_insufficient")),
                }
            )
    alerts.sort(key=lambda item: (item["urgency_ratio"] if item["urgency_ratio"] > 0 else 999, item["name"].lower()))
    return alerts
