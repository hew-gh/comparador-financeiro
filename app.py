import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Bloomberg Clone - Performance", layout="wide")

st.title("📊 Comparador de Performance Financeira")
st.markdown("Compare o rendimento acumulado de ativos (Base 100).")

# --- BARRA LATERAL ---
st.sidebar.header("Configurações")

# Seleção de Ativos
sugestoes = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', '^BVSP', 'BTC-USD']
papeis_selecionados = st.sidebar.multiselect("Selecione os ativos:", options=sugestoes, default=['AAPL', '^BVSP'])

# Campo para novos ativos (Autocomplete manual)
novo_ativo = st.sidebar.text_input("Adicionar outro (ex: NVDA, ETH-USD):")
if novo_ativo:
    ticker = novo_ativo.strip().upper()
    if ticker not in papeis_selecionados:
        papeis_selecionados.append(ticker)

# Datas
col1, col2 = st.sidebar.columns(2)
with col1:
    data_inicio = st.date_input("Início", value=datetime.now() - timedelta(days=365))
with col2:
    data_fim = st.date_input("Fim", value=datetime.now())

# --- FUNÇÃO DE CÁLCULO DE PERFORMANCE ---
def calcular_retornos(dados):
    resumo = []
    for col in dados.columns:
        serie = dados[col].dropna()
        if len(serie) < 2: continue
        
        ultimo = serie.iloc[-1]
        
        # 30 Dias
        alvo_30 = serie.index[-1] - timedelta(days=30)
        val_30 = serie.asof(alvo_30) if alvo_30 >= serie.index[0] else serie.iloc[0]
        ret_30 = (ultimo / val_30) - 1
        
        # YTD (Desde o início do ano atual)
        inicio_ano = serie[serie.index.year == datetime.now().year]
        ret_ytd = (ultimo / inicio_ano.iloc[0]) - 1 if not inicio_ano.empty else 0
        
        # 1 Ano
        alvo_1y = serie.index[-1] - timedelta(days=365)
        val_1y = serie.asof(alvo_1y) if alvo_1y >= serie.index[0] else serie.iloc[0]
        ret_1y = (ultimo / val_1y) - 1
        
        # Período Total Selecionado
        ret_total = (ultimo / serie.iloc[0]) - 1
        
        resumo.append({
            "Ativo": col,
            "30 Dias": ret_30,
            "YTD": ret_ytd,
            "1 Ano": ret_1y,
            "Total Período": ret_total
        })
    return pd.DataFrame(resumo).set_index("Ativo")

# --- EXECUÇÃO ---
if papeis_selecionados:
    with st.spinner('Buscando dados...'):
        # Download (buscamos um pouco antes para garantir o cálculo de 1 ano se necessário)
        df = yf.download(papeis_selecionados, start=data_inicio, end=data_fim)['Close']
        
        if not df.empty:
            # Se for apenas um ativo, o pandas retorna uma Series, convertemos para DataFrame
            if isinstance(df, pd.Series):
                df = df.to_frame(name=papeis_selecionados[0])
            
            df = df.dropna()
            
            # Gráfico de Performance (Base 100)
            df_norm = (df / df.iloc[0]) * 100
            
            fig = go.Figure()
            for col in df_norm.columns:
                fig.add_trace(go.Scatter(x=df_norm.index, y=df_norm[col], name=col))
            
            fig.update_layout(template="plotly_dark", hovermode="x unified", height=500,
                              yaxis_title="Performance (Início = 100)")
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela de Performance Colorida
            st.subheader("📊 Resumo de Performance (%)")
            df_perf = calcular_retornos(df)
            
            def colorir_valor(val):
                color = '#00ff00' if val > 0 else '#ff4b4b'
                return f'color: {color}'

            st.dataframe(
                df_perf.style.applymap(colorir_valor).format("{:.2%}"),
                use_container_width=True
            )
        else:
            st.error("Nenhum dado encontrado para os ativos selecionados.")
else:
    st.info("Selecione ativos na barra lateral para começar.")
