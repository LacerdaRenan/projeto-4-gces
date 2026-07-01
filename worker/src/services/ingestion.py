import hashlib
import requests
import os
import glob
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

    def processar_arquivos_locais(self, diretorio: str) -> None:
        if not os.path.exists(diretorio):
            print(f"[Local] Diretório {diretorio} não encontrado. Nenhuma ingestão local realizada.")
            return

        arquivos_pdf = glob.glob(os.path.join(diretorio, "*.pdf"))
        if not arquivos_pdf:
            print(f"[Local] Nenhum arquivo PDF encontrado em {diretorio}.")
            return

        for filepath in arquivos_pdf:
            try:
                filename = os.path.basename(filepath)
                empresa_local = "Upload Local"
                
                with open(filepath, "rb") as f:
                    conteudo_pdf = f.read()

                file_hash = self._calcular_hash(conteudo_pdf)

                if self.repo.exists_by_hash(file_hash):
                    print(f"[{empresa_local}] Arquivo {filename} já processado anteriormente (Hash repetido). Ignorando.")
                    continue

                url_falsa = f"local://{filename}"
                if self.repo.exists_by_url(url_falsa):
                    print(f"[{empresa_local}] Arquivo {filename} já processado anteriormente (URL). Ignorando.")
                    continue

                novo_doc = self.repo.save(empresa_local, url_falsa, file_hash)

                try:
                    print(f"[{empresa_local}] Arquivo local {filename} enviado para julgamento da IA...")
                    metrics = self.uda.extract_structured_data(filepath)
                    
                    if metrics.is_valid_document and metrics.year and metrics.quarter:
                        nome_final = metrics.company_name if metrics.company_name else empresa_local
                        metrics.company_name = nome_final
                        self.repo.save_fact_metrics(novo_doc.id, metrics)
                        self.repo.update_status(novo_doc.id, 'PROCESSED')
                        print(f"[{nome_final}] APROVADO! Dados salvos do {metrics.quarter} {metrics.year} a partir de arquivo local.")
                    else:
                        self.repo.update_status(novo_doc.id, 'PROCESSED')
                        print(f"[{empresa_local}] DESCARTADO: A IA determinou que o PDF local {filename} não é uma Prévia Operacional.")
                    
                except Exception as e:
                    self.repo.update_status(novo_doc.id, 'ERROR')
                    print(f"[{empresa_local}] Erro durante análise UDA no arquivo local: {e}")

            except Exception as e:
                print(f"[Local] Erro de leitura no arquivo local {filepath}: {e}")