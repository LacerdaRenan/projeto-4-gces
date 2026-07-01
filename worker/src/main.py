import time
import schedule
from core.db_config import SessionLocal
from repositories.catalog_repo import CatalogRepository
from services.ingestion import IngestionService
from services.scraper_ri import ScraperRIService

def executar_pipeline_ingestao():
    print("\n[Worker] Iniciando Rede de Arrasto (Bulk Scraping)...")
    scraper = ScraperRIService()
    
    with SessionLocal() as db_session:
        repo = CatalogRepository(db_session)
        ingestao = IngestionService(repo)
        
        # 1. Processar PDFs locais na pasta de upload
        diretorio_local = "/app/local_pdfs"
        print(f"\n=========================================")
        print(f"Verificando arquivos manuais em: {diretorio_local}")
        print(f"=========================================")
        ingestao.processar_arquivos_locais(diretorio_local)

        # 2. Iniciar raspagem nas URLs
        empresas_alvo = [
            "MRV", 
            "Direcional", 
            "Tenda", 
            "Cyrela", 
            "Cury", 
            "Plano & Plano", 
            "Eztec"
        ]        
        for empresa in empresas_alvo:
            print(f"\n=========================================")
            print(f"Analisando construtora via Scrapper: {empresa}")
            print(f"=========================================")
            
            links_capturados = scraper.coletar_links_documentos(empresa)
            
            if links_capturados:
                ingestao.processar_lote(empresa, links_capturados)
            else:
                print(f"Nenhum documento compatível encontrado para {empresa}.")
                
    print("\n[Worker] Varredura em massa finalizada.\n")

if __name__ == "__main__":
    executar_pipeline_ingestao()
    schedule.every().day.at("02:00").do(executar_pipeline_ingestao)
    while True:
        schedule.run_pending()
        time.sleep(60)