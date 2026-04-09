import json
import os
import pandas as pd

class AuditorCMN:
    """
    Motor de Compliance Regulatório para Fundos de Pensão (EFPCs).
    Lê os dados dinamicamente e valida a alocação contra a Resolução CMN.
    """
    
    def __init__(self, regras_cmn: dict):
        # O motor agora é inicializado carregando a lei injetada via JSON
        self.limites_legais = regras_cmn.get("limites_percentuais", {})
        self.resolucao_nome = regras_cmn.get("resolucao", "CMN 4.994/2021")

    def auditar_carteira(self, pl_total: float, carteira_atual: dict) -> dict:
        """
        Cruza a fotografia atual da carteira com a lei vigente.
        """
        print("\n" + "="*60)
        print(f"⚖️  PREVQUANT: AUDITORIA DE ENQUADRAMENTO ({self.resolucao_nome})")
        print("="*60)
        print(f"💰 PL Auditado (Ofuscado): R$ {pl_total:,.2f}")
        print("-" * 60)
        
        status_geral = "APROVADO"
        relatorio = []
        
        for classe, valor_alocado in carteira_atual.items():
            # Proteção contra classes não mapeadas na política
            if classe not in self.limites_legais:
                print(f"⚠️  ALERTA: Classe '{classe}' não reconhecida na política.")
                continue
                
            exposicao_atual = valor_alocado / pl_total
            limite_teto = self.limites_legais[classe]
            margem = limite_teto - exposicao_atual
            
            # Validação do Teto
            if exposicao_atual > limite_teto:
                status_classe = "DESENQUADRADO"
                status_geral = "REPROVADO"
                print(f"❌ {classe.replace('_', ' ')}: {exposicao_atual*100:.2f}% rompe o teto de {limite_teto*100:.0f}%!")
            else:
                status_classe = "ENQUADRADO"
                print(f"✅ {classe.replace('_', ' ')}: {exposicao_atual*100:.2f}% (Teto: {limite_teto*100:.0f}% | Folga: {margem*100:.2f}%)")
                
            relatorio.append({
                'Classe de Ativo': classe.replace('_', ' '),
                'Volume Alocado (R$)': valor_alocado,
                'Exposição Atual (%)': round(exposicao_atual * 100, 2),
                'Teto Legal (%)': round(limite_teto * 100, 2),
                'Status': status_classe
            })

        print("-" * 60)
        if status_geral == "REPROVADO":
            print("🚨 STATUS DO FUNDO: REPROVADO PELO COMPLIANCE.")
            print("   AÇÃO EXIGIDA: Rebalanceamento imediato para evitar sanções da PREVIC.")
        else:
            print("🟢 STATUS DO FUNDO: APROVADO.")
            print("   CARTEIRA LEGAL: Liberada para simulação atuarial (ALM).")
            
        return {
            "status_geral": status_geral,
            "detalhamento": pd.DataFrame(relatorio)
        }

# ==========================================
# ORQUESTRAÇÃO (O Cérebro Integrador)
# ==========================================
def executar_auditoria_integrada():
    # Pega a pasta onde este script está salvo (motor_compliance)
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    
    # Volta uma pasta (para a raiz PrevQuant_Engine) e entra na camada_dados
    diretorio_raiz = os.path.dirname(diretorio_atual)
    pasta_dados = os.path.join(diretorio_raiz, "camada_dados")
    
    # Mapeia os caminhos corretos dos arquivos JSON
    caminho_regras = os.path.join(pasta_dados, "limites_cmn_4994.json")
    caminho_carteira = os.path.join(pasta_dados, "alocacao_atual_efpc.json")
    
    # 1. Tenta carregar as regras (A Lei via RAG)
    try:
        with open(caminho_regras, 'r', encoding='utf-8') as f:
            regras_cmn = json.load(f)
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo de regras não encontrado em: {caminho_regras}")
        print("💡 DICA: Certifique-se de que o script 'rag_auditor_cmn.py' foi rodado com sucesso.")
        return

    # 2. Tenta carregar a carteira (A Realidade Ofuscada)
    try:
        with open(caminho_carteira, 'r', encoding='utf-8') as f:
            dados_carteira = json.load(f)
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo da carteira não encontrado em: {caminho_carteira}")
        print("💡 DICA: Certifique-se de que o script 'ingestao_dados_publicos.py' foi rodado.")
        return

    # 3. Extrai as variáveis necessárias do JSON da carteira
    nome_fundo = dados_carteira.get("identificacao", {}).get("nome_fundo", "Fundo Desconhecido")
    pl_total = dados_carteira.get("financeiro", {}).get("pl_total_mascarado", 0.0)
    alocacao_atual = dados_carteira.get("financeiro", {}).get("alocacao_atual", {})
    
    print(f"🏛️ Iniciando pipeline de auditoria para o {nome_fundo}...")
    
    # 4. Instancia o motor passando a lei, e audita passando a carteira
    motor_compliance = AuditorCMN(regras_cmn)
    resultado = motor_compliance.auditar_carteira(pl_total=pl_total, carteira_atual=alocacao_atual)

if __name__ == "__main__":
    executar_auditoria_integrada()