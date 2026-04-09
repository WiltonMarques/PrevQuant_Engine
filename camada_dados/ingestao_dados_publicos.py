import json
import random
from datetime import datetime
import os

def gerar_carteira_anonimizada():
    """
    Simula a extração de dados públicos da PREVIC.
    Aplica Data Masking (Anonimização do nome) e Ofuscação Proporcional
    (Divisor aleatório) para preservar o sigilo das informações reais.
    """
    print("🌐 Conectando à base de Dados Abertos (Simulação PREVIC)...")
    
    # 1. Dados base de um fundo "Real" (Valores hipotéticos baseados na média de mercado)
    pl_real = 5_850_000_000.00  # Fundo real com R$ 5.85 Bilhões
    
    # Proporções reais da alocação (A soma deve ser 1.0 ou 100%)
    proporcoes_reais = {
        "Renda_Fixa": 0.65,                 # 65%
        "Renda_Variavel": 0.18,             # 18%
        "Investimentos_Estruturados": 0.07, # 7%
        "Exterior": 0.05,                   # 5%
        "Imoveis": 0.03,                    # 3%
        "Operacoes_Participantes": 0.02     # 2%
    }

    # 2. PROCESSO DE ANONIMIZAÇÃO E OFUSCAÇÃO (Sua ideia aplicada)
    nome_anonimizado = f"Fundo de Pensão Escolar {random.choice(['Alpha', 'Beta', 'Gama', 'Sigma'])}"
    
    # Gera um divisor aleatório entre 2.5 e 7.8 para mascarar os valores
    divisor_aleatorio = random.uniform(2.5, 7.8)
    
    # Aplica o divisor no Patrimônio Líquido
    pl_ofuscado = pl_real / divisor_aleatorio
    
    print(f"🔒 Aplicando mascaramento de dados...")
    print(f"   -> Fundo Anonimizado: {nome_anonimizado}")
    print(f"   -> Divisor Aleatório Aplicado: {divisor_aleatorio:.4f}")
    
    # 3. CONSTRUINDO A CARTEIRA OFUSCADA
    carteira_ofuscada = {}
    for classe, percentual in proporcoes_reais.items():
        # O valor em R$ muda, mas a proporção frente ao PL ofuscado se mantém!
        valor_alocado_ofuscado = pl_ofuscado * percentual
        carteira_ofuscada[classe] = round(valor_alocado_ofuscado, 2)

    # 4. EMPACOTANDO O RESULTADO EM JSON
    snapshot_carteira = {
        "metadados": {
            "data_extracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status_dados": "Anonimizado para fins educacionais",
            "fator_ofuscacao_aplicado": True
        },
        "identificacao": {
            "nome_fundo": nome_anonimizado,
            "cnpj": "XX.XXX.XXX/0001-XX"
        },
        "financeiro": {
            "moeda": "BRL",
            "pl_total_mascarado": round(pl_ofuscado, 2),
            "alocacao_atual": carteira_ofuscada
        }
    }

    # Salvando o arquivo no diretório atual
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_arquivo = os.path.join(diretorio_atual, "alocacao_atual_efpc.json")
    
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        json.dump(snapshot_carteira, f, indent=4, ensure_ascii=False)
        
    print(f"✅ SUCESSO! Fotografia anonimizada salva em: {os.path.basename(caminho_arquivo)}")
    print(f"💰 PL Mascarado Resultante: R$ {pl_ofuscado:,.2f}")

if __name__ == "__main__":
    gerar_carteira_anonimizada()