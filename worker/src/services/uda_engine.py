import os
import pymupdf4llm
from google import genai
from google.genai import types
from domain.metrics import HousingMetricsContract

class UnstructuredDataAnalysisEngine:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Chave API do Gemini não configurada.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

    def extract_structured_data(self, temp_pdf_path: str) -> HousingMetricsContract:
        texto_completo_markdown = pymupdf4llm.to_markdown(temp_pdf_path)
        prompt_sistema = (
            "Você é um Engenheiro de Dados validando relatórios. "
            "Sua PRIMEIRA tarefa é classificar o documento: verifique se o texto fornecido "
            "é efetivamente uma 'Prévia Operacional' ou 'Relatório de Resultados'. Se for um documento irrelevante "
            "(como editais, ESG, convocações), marque is_valid_document como false e retorne null no resto. "
            "Se for válido, marque true e extraia o Ano, Trimestre e as métricas absolutas. "
            "Atenção: O documento pode ser uma tabela contínua ou uma apresentação de slides. Leia tudo antes de responder."
        )

        resposta = self.client.models.generate_content(
            model=self.model_name,
            contents=f"Analise este relatório corporativo em Markdown:\n\n{texto_completo_markdown}",
            config=types.GenerateContentConfig(
                system_instruction=prompt_sistema,
                response_mime_type="application/json",
                response_schema=HousingMetricsContract,
                temperature=0.0
            )
        )
        return HousingMetricsContract.model_validate_json(resposta.text)
