from sqlalchemy.orm import Session
from sqlalchemy import text
from domain.catalog import CatalogIngestion
from domain.metrics import HousingMetricsContract

class CatalogRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def exists_by_url(self, url: str) -> bool:
        return self.db.query(CatalogIngestion).filter(CatalogIngestion.document_url == url).first() is not None

    def exists_by_hash(self, file_hash: str) -> bool:
        return self.db.query(CatalogIngestion).filter(CatalogIngestion.file_hash == file_hash).first() is not None

    def save(self, company_name: str, document_url: str, file_hash: str) -> CatalogIngestion:
        new_doc = CatalogIngestion(company_name=company_name, document_url=document_url, file_hash=file_hash, status='PENDING')
        self.db.add(new_doc)
        self.db.commit()
        self.db.refresh(new_doc)
        return new_doc

    def update_status(self, catalog_id: int, status: str):
        doc = self.db.query(CatalogIngestion).filter(CatalogIngestion.id == catalog_id).first()
        if doc:
            doc.status = status
            self.db.commit()

    def save_fact_metrics(self, catalog_id: int, metrics: HousingMetricsContract):
        query = text("""
            INSERT INTO fact_housing_performance 
            (catalog_id, company_name, year_reference, quarter_reference, vgv_launched_millions, units_sold, net_revenue_millions)
            VALUES (:cid, :name, :yr, :qt, :vgv, :units, :rev)
        """)
        self.db.execute(query, {
            "cid": catalog_id, "name": metrics.company_name, "yr": metrics.year,
            "qt": metrics.quarter, "vgv": metrics.vgv_launched_millions,
            "units": metrics.units_sold, "rev": metrics.net_revenue_millions
        })
        self.db.commit()