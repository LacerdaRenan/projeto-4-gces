from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional

class PerformanceRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_conjuntura_filtrada(self, empresa: Optional[str] = None, ano: Optional[int] = None, trimestre: Optional[str] = None) -> List[dict]:
        sql = """
            SELECT f.company_name AS empresa, f.year_reference AS ano, f.quarter_reference AS trimestre,
                   f.vgv_launched_millions AS vgv_lancado_milhoes, f.units_sold AS unidades_vendidas,
                   f.net_revenue_millions AS receita_liquida_milhoes, c.document_url AS fonte_pdf_original
            FROM fact_housing_performance f
            JOIN catalog_ingestion c ON f.catalog_id = c.id WHERE 1=1
        """
        params = {}
        if empresa:
            sql += " AND f.company_name = :empresa"
            params["empresa"] = empresa
        if ano:
            sql += " AND f.year_reference = :ano"
            params["ano"] = ano
        if trimestre:
            sql += " AND f.quarter_reference = :trimestre"
            params["trimestre"] = trimestre
        sql += " ORDER BY f.year_reference DESC, f.quarter_reference DESC"
        return [dict(row._mapping) for row in self.db.execute(text(sql), params)]