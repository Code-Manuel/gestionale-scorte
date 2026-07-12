
# Gestionale Scorte

Progetto portfolio in Python per gestire scorte di magazzino, registrare movimenti di carico/scarico e generare alert di riordino.

## Funzionalità

- Gestione prodotti con nome, categoria, unità di misura e stock corrente
- Registrazione di movimenti di carico e scarico
- Calcolo automatico di soglia e quantità da ordinare
- Home page minimale con ricerca e drawer per creare prodotti e consultare gli alert
- API REST con FastAPI, documentazione Swagger/OpenAPI e test con pytest

## Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite
- Uvicorn
- Jinja2
- Pytest

## Installazione

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Avvio

```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

La documentazione API sarà disponibile su:

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc

## Esempio di chiamata API

Creazione di un prodotto:

```bash
curl -X POST "http://127.0.0.1:8000/products" -H "Content-Type: application/json" -d "{\"name\":\"Siringhe\",\"unit\":\"confezione\",\"current_stock\":10}"
```

Registrazione di uno scarico:

```bash
curl -X POST "http://127.0.0.1:8000/movements" -H "Content-Type: application/json" -d "{\"product_id\":1,\"movement_type\":\"scarico\",\"quantity\":3,\"movement_date\":\"2026-07-06\"}"
```

## Logica di riordino

Il calcolo segue esattamente la regola richiesta:

1. `scarico_totale_anno` = somma degli scarichi dall'inizio dell'anno corrente fino ad oggi
2. `settimana_corrente` = numero della settimana ISO dell'anno corrente
3. `consumo_medio_settimanale` = `scarico_totale_anno / settimana_corrente`
4. `soglia_riordino` = `consumo_medio_settimanale * 4`
5. `quantita_da_ordinare` = `soglia_riordino - current_stock`

Se la quantità è maggiore di zero, viene generato un alert; altrimenti no.

Se l'anno è ancora agli inizi e non ci sono dati sufficienti, il sistema usa lo storico dell'anno precedente; se non esiste, il prodotto viene segnato come dati insufficienti.

Esempio numerico:

- scarico totale anno: 24 unità
- settimana corrente: 6
- consumo medio settimanale: 4
- soglia di riordino: 16
- stock attuale: 10
- quantità da ordinare: 6

## Test

```bash
pytest -q
```
=======
# gestionale-scorte
Progetto portfolio per la gestione di scorte di magazzino
>>>>>>> 5b18cfd304515466be7c723591f42dee3a3bd9b4
