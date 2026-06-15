from pydantic import BaseModel, Field
from typing import Optional

class HousingMetricsContract(BaseModel):
    is_valid_document: bool = Field(description="Retorne true SOMENTE se o documento for uma 'Prévia Operacional' ou 'Relatório de Resultados' com métricas de lançamentos e vendas. Retorne false se for qualquer outro tipo de documento (ex: edital, sustentabilidade, aviso de dividendos).")
    
    company_name: Optional[str] = Field(None, description="Nome da construtora. Retorne null se is_valid_document for false.")
    year: Optional[int] = Field(None, description="Ano de referência do relatório com 4 dígitos. Retorne null se is_valid_document for false.")
    quarter: Optional[str] = Field(None, description="Trimestre ('1T', '2T', '3T' ou '4T'). Retorne null se is_valid_document for false.")
    
    vgv_launched_millions: Optional[float] = Field(None, description="VGV Lançado em milhões de reais.")
    units_sold: Optional[int] = Field(None, description="Número absoluto de unidades vendidas.")
    net_revenue_millions: Optional[float] = Field(None, description="Receita Líquida em milhões de reais.")