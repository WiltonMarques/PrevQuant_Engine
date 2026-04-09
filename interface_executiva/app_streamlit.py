import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import json
import os

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="PrevQuant Engine | ALM",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. FUNÇÕES DE CARREGAMENTO DE DADOS
# ==========================================
@st.cache_data
def carregar_dados():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    pasta_dados = os.path.join(os.path.dirname(diretorio_atual), "camada_dados")
    
    try:
        with open(os.path.join(pasta_dados, "limites_cmn_4994.json"), 'r', encoding='utf-8') as f:
            regras = json.load(f)
        with open(os.path.join(pasta_dados, "alocacao_atual_efpc.json"), 'r', encoding='utf-8') as f:
            carteira = json.load(f)
        return regras, carteira
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None, None

regras_cmn, dados_carteira = carregar_dados()

if not regras_cmn or not dados_carteira:
    st.stop()

pl_total = dados_carteira["financeiro"]["pl_total_mascarado"]
nome_fundo = dados_carteira["identificacao"]["nome_fundo"]

# ==========================================
# TEXTO PADRÃO DE GOVERNANÇA (DISCLAIMER)
# ==========================================
texto_governanca = """
**🛡️ Nota Metodológica e Governança de Dados:** Este painel foi desenvolvido exclusivamente para fins didáticos e de demonstração de arquitetura quantitativa. 
Os dados base de alocação foram extraídos do portal de **Dados Abertos da PREVIC** (Superintendência Nacional de Previdência Complementar). 
Para garantir o sigilo institucional e o compliance com a LGPD, o fundo original passou por um rigoroso processo de **Data Masking (Anonimização)**. 
Os valores financeiros absolutos foram ofuscados mediante a aplicação de um divisor aleatório, preservando estritamente as proporções de alocação percentual necessárias para a auditoria de limites legais (CMN 4.994).
"""

# ==========================================
# 3. SIDEBAR (PAINEL DE CONTROLE LATERAL)
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3256/3256114.png", width=80)
st.sidebar.title("PrevQuant Engine")
st.sidebar.markdown(f"**Fundo:** {nome_fundo}")
st.sidebar.markdown("---")

st.sidebar.header("⚙️ Parâmetros Macroeconômicos")
retorno_aa = st.sidebar.slider("Retorno Esperado da Carteira (% a.a.)", min_value=1.0, max_value=20.0, value=9.0, step=0.5) / 100
volatilidade_aa = st.sidebar.slider("Risco / Volatilidade (% a.a.)", min_value=1.0, max_value=30.0, value=8.0, step=0.5) / 100

st.sidebar.header("📉 Passivo Atuarial")
passivo_mensal = st.sidebar.number_input("Desembolso Mensal Estimado (R$)", min_value=1_000_000, value=6_000_000, step=500_000)

st.sidebar.header("🔀 Simulação (Monte Carlo)")
anos = st.sidebar.slider("Horizonte (Anos)", min_value=10, max_value=50, value=30, step=5)
num_cenarios = st.sidebar.selectbox("Cenários Gerados", [500, 1000, 2000], index=1)

# ==========================================
# 4. TELA PRINCIPAL (DASHBOARD)
# ==========================================
st.title("🏛️ Painel Executivo ALM (Asset Liability Management)")
st.markdown("Plataforma institucional de Compliance e Risco Atuarial baseada em simulações estocásticas.")

col1, col2, col3 = st.columns(3)
col1.metric("Patrimônio Líquido (Ofuscado)", f"R$ {pl_total:,.2f}")
col2.metric("Teto Regulatório (CMN)", "Auditado ✅")
col3.metric("Passivo Anualizado", f"R$ {(passivo_mensal * 12):,.2f}")

st.markdown("---")

aba1, aba2 = st.tabs(["⚖️ Compliance (Regras CMN)", "🎲 Solvência (Monte Carlo)"])

# --- ABA 1: COMPLIANCE ---
with aba1:
    st.subheader("Auditoria de Enquadramento da Carteira")
    
    alocacao = dados_carteira["financeiro"]["alocacao_atual"]
    limites = regras_cmn["limites_percentuais"]
    
    dados_tabela = []
    for classe, valor in alocacao.items():
        peso = valor / pl_total
        teto = limites.get(classe, 0)
        status = "✅ OK" if peso <= teto else "❌ Desenquadrado"
        dados_tabela.append([classe.replace('_', ' '), f"R$ {valor:,.2f}", f"{peso*100:.2f}%", f"{teto*100:.2f}%", status])
        
    df_compliance = pd.DataFrame(dados_tabela, columns=["Classe de Ativo", "Valor Alocado", "Peso Atual", "Teto Legal", "Status"])
    st.dataframe(df_compliance, use_container_width=True)
    
    st.write("") # Espaçamento
    st.info(texto_governanca) # <--- AVISO ADICIONADO AQUI

# --- ABA 2: MONTE CARLO ---
with aba2:
    st.subheader(f"Projeção de Solvência para {anos} anos")
    
    if st.button("🚀 Rodar Simulação de Monte Carlo", type="primary"):
        with st.spinner("Processando matriz estocástica..."):
            
            retorno_m = (1 + retorno_aa) ** (1/12) - 1
            volatilidade_m = volatilidade_aa / np.sqrt(12)
            meses = anos * 12
            
            trajetorias = np.zeros((meses, num_cenarios))
            trajetorias[0] = pl_total
            ruina = 0
            
            for c in range(num_cenarios):
                pl = pl_total
                for m in range(1, meses):
                    choque = np.random.normal(retorno_m, volatilidade_m)
                    pl = (pl * (1 + choque)) - passivo_mensal
                    if pl <= 0:
                        pl = 0
                        trajetorias[m:, c] = 0
                        ruina += 1
                        break
                    trajetorias[m, c] = pl
                    
            probabilidade = ((num_cenarios - ruina) / num_cenarios) * 100
            
            cor_prob = "normal"
            if probabilidade > 95: st.success(f"🟢 **Risco Baixíssimo.** Probabilidade de sucesso: **{probabilidade:.2f}%**")
            elif probabilidade > 80: st.warning(f"🟡 **Atenção (Risco Moderado).** Probabilidade de sucesso: **{probabilidade:.2f}%**")
            else: st.error(f"🚨 **ALERTA DE INSOLVÊNCIA.** Probabilidade de sucesso: **{probabilidade:.2f}%**")

            fig = go.Figure()
            eixo_x = np.arange(meses)
            
            amostra = min(50, num_cenarios)
            indices_amostra = np.random.choice(num_cenarios, amostra, replace=False)
            for i in indices_amostra:
                fig.add_trace(go.Scatter(x=eixo_x, y=trajetorias[:, i], mode='lines', line=dict(color='rgba(150,150,150,0.1)', width=1), showlegend=False, hoverinfo='skip'))
                
            mediana = np.median(trajetorias, axis=1)
            fig.add_trace(go.Scatter(x=eixo_x, y=mediana, mode='lines', name='Mediana (Cenário Base)', line=dict(color='blue', width=3)))
            
            p5 = np.percentile(trajetorias, 5, axis=1)
            fig.add_trace(go.Scatter(x=eixo_x, y=p5, mode='lines', name='5º Percentil (Pior Cenário)', line=dict(color='red', width=3, dash='dash')))
            
            fig.update_layout(
                title="Evolução do Patrimônio Líquido (Caminhos Aleatórios)",
                xaxis_title="Meses",
                yaxis_title="Patrimônio (R$)",
                template="plotly_white",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
    st.write("") # Espaçamento
    st.info(texto_governanca) # <--- AVISO ADICIONADO AQUI TAMBÉM