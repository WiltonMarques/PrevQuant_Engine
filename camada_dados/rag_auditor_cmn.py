import os
import json
import PyPDF2
from dotenv import load_dotenv
from google import genai

# =====================================================================
# 1. CARREGAR VARIÁVEIS DE AMBIENTE (O Cofre de Segurança)
# =====================================================================
# A função abaixo lê o arquivo .env e carrega a chave para a memória do sistema
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("ERRO CRÍTICO: Chave da API não encontrada. Verifique o arquivo .env na raiz do projeto.")

# =====================================================================
# 2. CONFIGURAÇÃO DO AGENTE DE IA (Novo SDK GenAI)
# =====================================================================
# Instancia o cliente passando a chave de forma dinâmica e segura
cliente = genai.Client(api_key=API_KEY)

# =====================================================================
# 3. MOTOR DE EXTRAÇÃO DE TEXTO (PDF Parsing)
# =====================================================================
def extrair_texto_pdf(caminho_pdf):
    print(f"Lendo o documento jurídico: {caminho_pdf}...")
    texto_completo = ""
    
    try:
        with open(caminho_pdf, 'rb') as arquivo:
            leitor_pdf = PyPDF2.PdfReader(arquivo)
            for pagina in leitor_pdf.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_completo += texto_pagina + "\n"
                    
        print("✅ Extração do PDF concluída com sucesso!")
        return texto_completo
        
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo {caminho_pdf} não encontrado.")
        return None

# =====================================================================
# 4. MOTOR RAG / AUDITORIA DE COMPLIANCE (NLP via Gemini)
# =====================================================================
def auditar_limites_cmn(texto_legislacao):
    print("Enviando Resolução para a IA processar a matriz de compliance...")
    
    prompt_engenharia = """
    Você é um auditor sênior de compliance de Fundos de Pensão (EFPC).
    Com base no texto da Resolução CMN 4.994 fornecido, extraia os limites máximos de alocação
    para cada segmento de aplicação.
    
    Retorne APENAS um objeto JSON válido, sem formatação markdown adicional, no seguinte formato:
    {
        "renda_fixa": 100,
        "renda_variavel": 70,
        "imoveis": 8,
        "operacoes_participantes": 15,
        "exterior": 10
    }
    
    Texto da Resolução a ser auditado:
    """ + texto_legislacao[:30000] # Trava de segurança de contexto

    try:
        # Chamada ao LLM utilizando o modelo focado em tarefas rápidas e precisas
        response = cliente.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_engenharia
        )
        
        # Limpeza do JSON (remove blocos ```json caso a IA os gere)
        resultado_limpo = response.text.replace('```json', '').replace('```', '').strip()
        matriz_json = json.loads(resultado_limpo)
        
        return matriz_json
        
    except Exception as e:
        print(f"❌ Erro durante a extração via IA: {e}")
        return None

# =====================================================================
# 5. EXECUÇÃO PRINCIPAL DO PIPELINE
# =====================================================================
if __name__ == "__main__":
    # Mapeia dinamicamente a pasta exata onde este script está salvo (camada_dados)
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    
    # Junta o caminho da pasta com o nome dos arquivos
    caminho_arquivo = os.path.join(diretorio_script, "resolucao_cmn_4994.pdf")
    caminho_saida = os.path.join(diretorio_script, "limites_cmn_4994.json")
    
    # Executa a esteira de processamento
    texto_resolucao = extrair_texto_pdf(caminho_arquivo)
    
    if texto_resolucao:
        matriz_limites = auditar_limites_cmn(texto_resolucao)
        
        if matriz_limites:
            print("\n=== MATRIZ DE LIMITES REGULATÓRIOS EXTRAÍDA ===")
            print(json.dumps(matriz_limites, indent=4, ensure_ascii=False))
            
            # Salva o resultado final na mesma pasta do script
            with open(caminho_saida, 'w', encoding='utf-8') as f:
                json.dump(matriz_limites, f, indent=4, ensure_ascii=False)
                
            print(f"\n✅ Arquivo de parâmetros '{caminho_saida}' gerado com sucesso!")