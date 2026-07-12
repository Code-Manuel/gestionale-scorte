from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import get_alerts
from app.database import get_db
from app.schemas import AlertResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
def list_alerts(db: Session = Depends(get_db)) -> list[AlertResponse]:
    return get_alerts(db)
