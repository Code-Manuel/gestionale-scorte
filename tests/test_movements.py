from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import Product, StockMovement

client = TestClient(app)


def setup_function():
    db = SessionLocal()
    db.query(StockMovement).delete()
    db.query(Product).delete()
    db.commit()
    db.close()


def test_create_movement_updates_stock():
    product_response = client.post(
        "/products",
        json={"name": "Guanti", "unit": "paio", "current_stock": 5},
    )
    product_id = product_response.json()["id"]

    movement_response = client.post(
        "/movements",
        json={"product_id": product_id, "movement_type": "scarico", "quantity": 2, "movement_date": "2026-07-06"},
    )

    assert movement_response.status_code == 201
    assert movement_response.json()["current_stock"] == 3
