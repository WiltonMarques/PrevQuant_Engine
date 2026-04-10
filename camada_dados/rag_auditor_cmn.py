import os
import json
import PyPDF2
from google import genai

# ==========================================
# 1. CONFIGURAÇÃO DO AGENTE DE IA (Novo SDK)
# ==========================================
# Substitua pela sua chave de API real do Google Gemini
API_KEY = "" 
cliente = genai.Client(api_key=API_KEY)

# ==========================================
# 2. MOTOR DE EXTRAÇÃO DE TEXTO (PDF)
# ==========================================
def extrair_texto_pdf(caminho_pdf):
    """Lê o arquivo PDF da Resolução e converte as páginas em texto bruto."""
    print(f"📄 Lendo o arquivo jurídico: {caminho_pdf}...")
    texto_completo = ""
    try:
        with open(caminho_pdf, 'rb') as arquivo:
            leitor = PyPDF2.PdfReader(arquivo)
            for pagina in leitor.pages:
                texto_completo += pagina.extract_text() + "\n"
        return texto_completo
    except FileNotFoundError:
        print(f"❌ ERRO: O arquivo '{os.path.basename(caminho_pdf)}' não foi encontrado.")
        print(f"💡 DICA: Certifique-se de salvar o PDF exatamente nesta pasta: {os.path.dirname(caminho_pdf)}")
        return None

# ==========================================
# 3. PIPELINE RAG (Retrieval-Augmented Generation)
# ==========================================
def gerar_limites_via_rag(texto_lei):
    """
    Envia o texto da lei para a IA com um 'System Prompt' rigoroso,
    forçando a devolução do resultado estritamente em formato JSON.
    """
    print("🧠 Inicializando processamento de linguagem natural (NLP)...")
    print("⚖️ A IA está auditando os artigos e extraindo os tetos percentuais...")
    
    prompt_engenharia = f"""
    Você é um Engenheiro de Dados e Auditor de Compliance especializado em Fundos de Pensão (EFPCs) no Brasil.
    Sua tarefa é ler o texto jurídico fornecido abaixo e extrair os LIMITES PERCENTUAIS MÁXIMOS (Teto) permitidos para alocação de recursos.

    Converta os percentuais encontrados (ex: 30%, 10%) em formato decimal (ex: 0.30, 0.10).
    Se o limite for 100%, use 1.00.

    Você deve retornar EXATAMENTE e APENAS um arquivo JSON válido, sem formatação markdown (```json), sem explicações ou texto adicional. Use a exata estrutura de chaves abaixo:

    {{
        "resolucao": "CMN 4.994/2021",
        "origem_dados": "Extração RAG Automatizada via PDF",
        "limites_percentuais": {{
            "Renda_Fixa": <valor_decimal>,
            "Renda_Variavel": <valor_decimal>,
            "Investimentos_Estruturados": <valor_decimal>,
            "Exterior": <valor_decimal>,
            "Imoveis": <valor_decimal>,
            "Operacoes_Participantes": <valor_decimal>
        }}
    }}

    TEXTO DA LEI:
    {texto_lei}
    """

    try:
        # Nova sintaxe da biblioteca google-genai
        resposta = cliente.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_engenharia
        )
        
        # Limpeza de segurança caso a IA retorne blocos de código markdown
        texto_json = resposta.text.strip()
        if texto_json.startswith("```json"):
            texto_json = texto_json[7:]
        if texto_json.endswith("```"):
            texto_json = texto_json[:-3]
            
        # Valida se o que a IA retornou é um JSON perfeito
        dicionario_regras = json.loads(texto_json.strip())
        return dicionario_regras
        
    except json.JSONDecodeError:
        print("❌ ERRO: A IA não retornou um JSON válido. Tente rodar novamente.")
        return None
    except Exception as e:
        print(f"❌ ERRO na comunicação com a API: {e}")
        return None

# ==========================================
# 4. ORQUESTRADOR E ESCRITA DO ARQUIVO
# ==========================================
def atualizar_regras_compliance():
    # Captura a pasta exata onde este script Python está salvo (camada_dados)
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    
    # Monta os caminhos absolutos para evitar o erro de "FileNotFound"
    caminho_pdf = os.path.join(diretorio_atual, "resolucao_cmn_4994.pdf")
    caminho_json = os.path.join(diretorio_atual, "limites_cmn_4994.json")
    
    texto_documento = extrair_texto_pdf(caminho_pdf)
    
    if texto_documento:
        regras_extraidas = gerar_limites_via_rag(texto_documento)
        
        if regras_extraidas:
            with open(caminho_json, 'w', encoding='utf-8') as f:
                json.dump(regras_extraidas, f, indent=4, ensure_ascii=False)
            print(f"✅ SUCESSO! A IA gerou a matriz de compliance imutável em: {caminho_json}")
            
if __name__ == "__main__":
    atualizar_regras_compliance()