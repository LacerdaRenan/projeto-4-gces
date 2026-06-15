from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.db_config import SessionLocal
from domain.response_schema import ConjunturaDataDTO
from repositories.performance_repo import PerformanceRepository

app = FastAPI(title="MCidades API", version="1.0.0")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.get("/api/conjuntura", response_model=List[ConjunturaDataDTO])
def obter_dados_conjuntura(
    empresa: Optional[str] = Query(None),
    ano: Optional[int] = Query(None),
    trimestre: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    repo = PerformanceRepository(db)
    return repo.get_conjuntura_filtrada(empresa=empresa, ano=ano, trimestre=trimestre)