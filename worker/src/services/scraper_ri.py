import urllib.parse
from playwright.sync_api import sync_playwright

class ScraperRIService:
    def __init__(self):
        self.portais_ri = {
            "MRV": "https://ri.mrv.com.br/informacoes-financeiras/central-de-resultados/",
            "Direcional": "https://ri.direcional.com.br/informacoes-financeiras/central-de-resultados/",
            "Tenda": "https://ri.tenda.com/informacoes-financeiras/central-de-resultados/",
            "Cyrela": "https://ri.cyrela.com.br/informacoes-financeiras/central-de-resultados/",
            "Cury": "https://ri.cury.net/informacoes-financeiras/central-de-resultados/",
            "Plano & Plano": "https://ri.planoeplano.com.br/informacoes-financeiras/central-de-resultados/",
            "Eztec": "https://ri.eztec.com.br/informacoes-financeiras/central-de-resultados/"
        }

    def coletar_links_documentos(self, empresa: str) -> set:
        url_base = self.portais_ri.get(empresa)
        links_encontrados = set()
        
        if not url_base:
            return links_encontrados

        print(f"\n[{empresa}] Iniciando Coleta Bruta de Arquivos...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            
            try:
                page.goto(url_base, timeout=60000)
                page.wait_for_load_state("networkidle")
                
                # Rola a página para garantir carregamento de elementos
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

                todos_links = page.locator("a").element_handles()
                
                for link in todos_links:
                    href = link.get_attribute("href") or ""
                    href_lower = href.lower()
                    
                    is_arquivo = (
                        ".pdf" in href_lower or 
                        "download" in href_lower or 
                        "mzfilemanager" in href_lower or 
                        "mziq.com" in href_lower or
                        "file" in href_lower
                    )
                    
                    if is_arquivo:
                        link_final = urllib.parse.urljoin(page.url, href)
                        links_encontrados.add(link_final)

                print(f"[{empresa}] Total de possíveis arquivos capturados: {len(links_encontrados)}")
                return links_encontrados
                
            except Exception as e:
                print(f"[{empresa}] Erro no Scraper: {str(e)}")
                return links_encontrados
            finally:
                browser.close()