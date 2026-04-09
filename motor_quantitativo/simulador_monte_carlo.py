import numpy as np
import pandas as pd
import os
import json

class SimuladorALM:
    """
    Motor Quantitativo baseado no método de Monte Carlo.
    Projeta o Patrimônio Líquido (PL) do fundo ao longo de décadas,
    cruzando a rentabilidade estocástica com o passivo atuarial.
    """
    
    def __init__(self, premissas_macro: dict):
        # Lê dinamicamente as premissas injetadas via JSON
        retorno_aa = premissas_macro.get("retorno_esperado_aa", 0.09)
        volatilidade_aa = premissas_macro.get("volatilidade_aa", 0.08)
        
        # Converte taxas anuais para mensais para o laço de repetição
        self.retorno_mensal = (1 + retorno_aa) ** (1/12) - 1
        self.volatilidade_mensal = volatilidade_aa / np.sqrt(12)

    def rodar_simulacao(self, pl_inicial: float, passivo_mensal: float, anos: int, num_cenarios: int):
        """
        Executa o Movimento Browniano Geométrico para simular o futuro do Fundo.
        """
        print("\n" + "="*60)
        print("🎲 PREVQUANT: SIMULADOR ALM (MONTE CARLO)")
        print("="*60)
        print(f"💰 PL Inicial: R$ {pl_inicial:,.2f} | 📉 Passivo Mensal: R$ {passivo_mensal:,.2f}")
        print(f"⏳ Horizonte: {anos} anos | 🔀 Cenários: {num_cenarios}")
        
        meses = anos * 12
        # Matriz para armazenar todos os caminhos [meses x cenarios]
        trajetorias = np.zeros((meses, num_cenarios))
        trajetorias[0] = pl_inicial
        
        ruina_contagem = 0

        print("⚙️ Processando matriz estocástica... (Isso pode levar alguns segundos)")
        for cenario in range(num_cenarios):
            pl_atual = pl_inicial
            
            for mes in range(1, meses):
                # 1. Injeta a aleatoriedade do mercado (Movimento Browniano)
                choque_mercado = np.random.normal(self.retorno_mensal, self.volatilidade_mensal)
                
                # 2. Calcula o novo PL: (PL Anterior * Rentabilidade) - Pagamento de Aposentados
                pl_atual = (pl_atual * (1 + choque_mercado)) - passivo_mensal
                
                # Se o dinheiro acabar, o fundo quebra (Ruína)
                if pl_atual <= 0:
                    pl_atual = 0
                    trajetorias[mes:, cenario] = 0
                    ruina_contagem += 1
                    break # Fundo quebrou neste cenário, para a simulação
                    
                trajetorias[mes, cenario] = pl_atual

        # Calcula a Probabilidade de Sobrevivência
        probabilidade_sucesso = ((num_cenarios - ruina_contagem) / num_cenarios) * 100
        
        print("-" * 60)
        print(f"💸 Probabilidade de Solvência Atuarial: {probabilidade_sucesso:.2f}%")
        
        if probabilidade_sucesso > 95:
            print("🟢 FUNDO SÓLIDO: Risco de ruína baixíssimo. Passivo garantido.")
        elif probabilidade_sucesso > 80:
            print("🟡 ATENÇÃO: Risco moderado. Comitê de investimentos deve revisar a carteira.")
        else:
            print("🚨 ALERTA CRÍTICO: Alta probabilidade de insolvência. Risco de não pagamento!")
            
        return trajetorias

# ==========================================
# ORQUESTRAÇÃO (O Cérebro Integrador)
# ==========================================
def executar_simulacao_integrada():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_dados = os.path.join(os.path.dirname(diretorio_atual), "camada_dados")
    
    # 1. Carrega os Parâmetros Econômicos e de Simulação
    caminho_parametros = os.path.join(pasta_dados, "parametros_economicos.json")
    try:
        with open(caminho_parametros, 'r', encoding='utf-8') as f:
            config = json.load(f)
            premissas_macro = config["premissas_macro"]
            passivo_mensal = config["passivo_atuarial"]["pagamento_mensal_estimado"]
            anos = config["configuracao_simulacao"]["horizonte_anos"]
            num_cenarios = config["configuracao_simulacao"]["numero_cenarios"]
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo de parâmetros não encontrado em: {caminho_parametros}")
        return

    # 2. Carrega a Carteira do Fundo (Para pegar o Patrimônio Líquido atual)
    caminho_carteira = os.path.join(pasta_dados, "alocacao_atual_efpc.json")
    try:
        with open(caminho_carteira, 'r', encoding='utf-8') as f:
            dados_carteira = json.load(f)
            pl_total_fundo = dados_carteira["financeiro"]["pl_total_mascarado"]
    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo da carteira não encontrado em: {caminho_carteira}")
        return

    # 3. Instancia o motor e executa
    motor_mc = SimuladorALM(premissas_macro)
    
    matriz_resultados = motor_mc.rodar_simulacao(
        pl_inicial=pl_total_fundo,
        passivo_mensal=passivo_mensal,
        anos=anos,
        num_cenarios=num_cenarios
    )

if __name__ == "__main__":
    executar_simulacao_integrada()