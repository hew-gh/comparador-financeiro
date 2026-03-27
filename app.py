import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Terminal Financeiro", layout="wide")

# --- CABEÇALHO ---
st.title("📊 Comparador de Performance")
st.markdown("Compare ativos normalizados pela base 100.")

# --- BARRA LATERAL (INPUTS) ---
st.sidebar.header("Configurações do Filtro")

# 1. Sugestão Automática de Papéis (Autocomplete)
# Criamos uma lista de sugestões comuns para facilitar
sugestoes = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', '^BVSP', 'BTC-USD']
papeis_selecionados = st.sidebar.multiselect(
    "Escolha os ativos:", 
    options=sugestoes + ["Adicione outros..."], 
    default=['AAPL', '^BVSP']
)

# Se o usuário quiser digitar um que não está na lista
input_manual = st.sidebar.text_input("Ou digite outros códigos (separados por vírgula):")
if input_manual:
    papeis_selecionados += [x.strip().upper() for x in input_manual.split(",")]

# 2. Ajuste de Período Personalizado
col1, col2 = st.sidebar.columns(2)
with col1:
    data_inicio = st.date_input("Início:", datetime.now() - timedelta(days=365))
with col2:
    data_fim = st.date_input("Fim:", datetime.now())

# --- LÓGICA DE PROCESSAMENTO ---
if st.sidebar.button("Atualizar Comparação"):
    if papeis_selecionados:
        with st.spinner('Buscando dados no Yahoo Finance...'):
            # Download
            dados = yf.download(papeis_selecionados, start=data_inicio, end=data_fim)['Close']
            
            if not dados.empty:
                dados = dados.dropna()
                
                # Normalização
                dados_norm = (dados / dados.iloc[0]) * 100
                
                # Gráfico Interativo
                fig = go.Figure()
                for col in (dados_norm.columns if len(papeis_selecionados) > 1 else [dados_norm.name]):
                    fig.add_trace(go.Scatter(x=dados_norm.index, y=dados_norm[col], name=col))
                
                fig.update_layout(template="plotly_dark", hovermode="x unified", height=600)
                st.plotly_chart(fig, use_container_width=True)
                
                # Tabela de Performance (Abaixo do gráfico)
                st.subheader("Tabela de Performance")
                # (Aqui entraria a lógica de cores que fizemos antes, adaptada para o Streamlit)
                st.dataframe(dados.pct_change().cumsum().iloc[[-1]].style.format("{:.2%}"))
            else:
                st.error("Nenhum dado encontrado para esses ativos/período.")
    else:
        st.warning("Selecione pelo menos um ativo.")
