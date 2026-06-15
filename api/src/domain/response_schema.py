from pydantic import BaseModel
from typing import Optional

class ConjunturaDataDTO(BaseModel):
    empresa: str
    ano: int
    trimestre: str
    vgv_lancado_milhoes: Optional[float]
    unidades_vendidas: Optional[int]
    receita_liquida_milhoes: Optional[float]
    fonte_pdf_original: str
    class Config:
        from_attributes = True