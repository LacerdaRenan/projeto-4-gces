import hashlib
import requests
import os
from repositories.catalog_repo import CatalogRepository
from services.uda_engine import UnstructuredDataAnalysisEngine

class IngestionService:
    def __init__(self, catalog_repo: CatalogRepository):
        self.repo = catalog_repo
        self.uda = UnstructuredDataAnalysisEngine()

    def _calcular_hash(self, conteudo: bytes) -> str:
        return hashlib.sha256(conteudo).hexdigest()

    def processar_lote(self, empresa: str, urls_documentos: set) -> None:
        for url in urls_documentos:
            try:
                print(f"[{empresa}] Baixando arquivo suspeito: {url[-30:]}...")
                resposta = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
                if resposta.status_code != 200:
                    continue

                conteudo_pdf = resposta.content
                file_hash = self._calcular_hash(conteudo_pdf)

                if self.repo.exists_by_hash(file_hash):
                    print(f"[{empresa}] Hash já existe (Arquivo repetido). Ignorando.")
                    continue

                novo_doc = self.repo.save(empresa, url, file_hash)
                temp_path = f"temp_{empresa}_{novo_doc.id}.pdf"
                
                with open(temp_path, "wb") as f:
                    f.write(conteudo_pdf)

                try:
                    print(f"[{empresa}] Arquivo enviado para julgamento da IA...")
                    metrics = self.uda.extract_structured_data(temp_path)
                    
                    if metrics.is_valid_document and metrics.year and metrics.quarter:
                        metrics.company_name = empresa 
                        self.repo.save_fact_metrics(novo_doc.id, metrics)
                        self.repo.update_status(novo_doc.id, 'PROCESSED')
                        print(f"[{empresa}] APROVADO! Dados salvos do {metrics.quarter} {metrics.year}.")
                    else:
                        self.repo.update_status(novo_doc.id, 'PROCESSED')
                        print(f"[{empresa}] DESCARTADO: A IA determinou que o PDF não é uma Prévia Operacional.")
                    
                except Exception as e:
                    self.repo.update_status(novo_doc.id, 'ERROR')
                    print(f"[{empresa}] Erro durante análise UDA: {e}")
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

            except Exception as e:
                print(f"[{empresa}] Erro de conexão/download: {e}")