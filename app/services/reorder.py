from __future__ import annotations

import math
from datetime import date
from typing import Any


def calculate_reorder(
    movements: list[dict[str, Any]],
    current_stock: float,
    reference_date: date | None = None,
) -> dict[str, float | bool]:
    """Calcola soglia di riordino e quantità suggerita seguendo la logica richiesta."""
    ref_date = reference_date or date.today()
    start_of_year = date(ref_date.year, 1, 1)
    current_week = ref_date.isocalendar()[1]

    outflows = [
        movement
        for movement in movements
        if movement.get("movement_type") == "scarico"
        and isinstance(movement.get("movement_date"), date)
        and start_of_year <= movement["movement_date"] <= ref_date
    ]

    if not outflows and current_week <= 2:
        previous_year_start = date(ref_date.year - 1, 1, 1)
        previous_year_end = date(ref_date.year - 1, 12, 31)
        outflows = [
            movement
            for movement in movements
            if movement.get("movement_type") == "scarico"
            and isinstance(movement.get("movement_date"), date)
            and previous_year_start <= movement["movement_date"] <= previous_year_end
        ]

    if not outflows:
        return {
            "consumo_medio_settimanale": 0.0,
            "soglia_riordino": 0.0,
            "quantita_da_ordinare": 0.0,
            "serve_ordine": False,
            "data_insufficient": True,
        }

    if current_week <= 0:
        current_week = 1

    scarico_totale_anno = sum(float(movement.get("quantity", 0)) for movement in outflows)
    consumo_medio_settimanale = scarico_totale_anno / current_week
    soglia_riordino = consumo_medio_settimanale * 4
    quantita_da_ordinare = max(soglia_riordino - float(current_stock), 0.0)

    return {
        "consumo_medio_settimanale": round(consumo_medio_settimanale, 2),
        "soglia_riordino": round(soglia_riordino, 2),
        "quantita_da_ordinare": round(math.ceil(quantita_da_ordinare), 2),
        "serve_ordine": quantita_da_ordinare > 0,
        "data_insufficient": False,
    }
