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


def test_create_and_list_products():
    response = client.post(
        "/products",
        json={"name": "Siringhe", "unit": "confezione", "current_stock": 10},
    )
    assert response.status_code == 201
    product = response.json()
    assert product["name"] == "Siringhe"

    list_response = client.get("/products")
    assert list_response.status_code == 200
    assert any(item["name"] == "Siringhe" for item in list_response.json())
