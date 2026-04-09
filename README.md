# 🏛️ PrevQuant Engine: RegTech & ALM para Fundos de Pensão

O **PrevQuant Engine** é uma plataforma institucional *End-to-End* desenvolvida em Python para automatizar o Compliance Regulatório e projetar o Risco Atuarial de Entidades Fechadas de Previdência Complementar (EFPCs).

## 🚀 Arquitetura e Módulos
O projeto é dividido em dois motores principais:

1. **Motor de Compliance (RegTech & GenAI):**
   - Utiliza a API do **Google Gemini (RAG)** para ler documentos jurídicos reais em PDF (Resolução CMN 4.994).
   - Extrai e converte limites regulatórios em matrizes de dados (JSON) atuando como *Fonte da Verdade*.
   - Audita a alocação do fundo anonimizado contra a legislação em tempo real.

2. **Motor Quantitativo (Simulador ALM):**
   - Roda o método estocástico de **Monte Carlo** para estressar a carteira do fundo.
   - Projeta 5.000 universos paralelos ao longo de 30 anos cruzando rentabilidade vs. passivo atuarial.
   - Calcula a Probabilidade de Solvência de forma matemática.

## 🛠️ Stack Tecnológico
- **Linguagem:** Python 3
- **Data Science:** NumPy, Pandas
- **Inteligência Artificial:** Google GenAI SDK (Gemini 2.5 Flash), PyPDF2
- **Data Visualization & UI:** Streamlit, Plotly

## ⚙️ Como executar na sua máquina
1. Clone o repositório: `git clone https://github.com/SeuUsuario/PrevQuant_Engine.git`
2. Instale as dependências: `pip install -r requirements.txt`
3. Adicione sua chave do Google Gemini no arquivo `.env`
4. Inicie o Dashboard Executivo: `streamlit run interface_executiva/app_streamlit.py`

*Nota Metodológica: O fundo de pensão analisado passou por ofuscação de valores absolutos (Data Masking) para conformidade com a LGPD, mantendo as proporções reais da base de dados abertos da PREVIC.*
