from sqlalchemy import Column, Integer, String, Text, Enum
from core.db_config import Base

class CatalogIngestion(Base):
    __tablename__ = "catalog_ingestion"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False)
    document_url = Column(Text, nullable=False)
    file_hash = Column(String(64), unique=True, nullable=False)
    status = Column(Enum('PENDING', 'PROCESSED', 'ERROR'), default='PENDING')