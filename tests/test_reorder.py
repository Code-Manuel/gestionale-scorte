from datetime import date

from app.services.reorder import calculate_reorder


def test_sufficient_stock_no_order():
    reference_date = date(2024, 7, 15)
    movements = [
        {"movement_type": "scarico", "quantity": 10, "movement_date": date(2024, 1, 10)},
        {"movement_type": "scarico", "quantity": 5, "movement_date": date(2024, 6, 15)},
    ]

    result = calculate_reorder(movements, current_stock=3, reference_date=reference_date)

    assert result["serve_ordine"] is False
    assert result["soglia_riordino"] == 2.07
    assert result["quantita_da_ordinare"] == 0.0


def test_below_threshold_requires_order():
    reference_date = date(2024, 7, 15)
    movements = [
        {"movement_type": "scarico", "quantity": 10, "movement_date": date(2024, 1, 10)},
        {"movement_type": "scarico", "quantity": 5, "movement_date": date(2024, 6, 15)},
    ]

    result = calculate_reorder(movements, current_stock=1, reference_date=reference_date)

    assert result["serve_ordine"] is True
    assert result["soglia_riordino"] == 2.07
    assert result["quantita_da_ordinare"] == 2.0


def test_new_product_without_history():
    result = calculate_reorder([], current_stock=0, reference_date=date(2024, 1, 5))

    assert result["serve_ordine"] is False
    assert result["soglia_riordino"] == 0.0
    assert result["quantita_da_ordinare"] == 0.0


def test_early_year_history_falls_back_to_previous_year():
    reference_date = date(2024, 1, 5)
    movements = [
        {"movement_type": "scarico", "quantity": 8, "movement_date": date(2023, 1, 3)},
    ]

    result = calculate_reorder(movements, current_stock=1, reference_date=reference_date)

    assert result["serve_ordine"] is True
    assert result["soglia_riordino"] == 32.0
    assert result["quantita_da_ordinare"] == 31.0


def test_no_history_in_early_year_marks_insufficient_data():
    result = calculate_reorder([], current_stock=0, reference_date=date(2024, 1, 5))

    assert result["serve_ordine"] is False
    assert result["data_insufficient"] is True
