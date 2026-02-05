import pandas as pd
import streamlit as st

from config.constants import DF_FINAL_FILE
from components.data import load_folha_pagamento_2025
from components.layout import render_header, render_footer

render_header()
st.header("📌 Visão Geral (2025)")

df = load_folha_pagamento_2025(DF_FINAL_FILE)

# ===== Sidebar =====
st.sidebar.header("⚙️ Configuração")
st.sidebar.caption("Dataset carregado do diretório data/processed.")
st.sidebar.code(DF_FINAL_FILE)

# ===== KPIs rápidos (sanity check) =====
col1, col2, col3 = st.columns(3)
col1.metric("Linhas", f"{df.shape[0]:,}".replace(",", "."))
col2.metric("Colunas", f"{df.shape[1]}")
col3.metric("Memória (aprox.)", f"{df.memory_usage(deep=True).sum() / (1024**2):.2f} MB")

st.divider()

# ===== Estrutura do dataset =====
with st.expander("🔎 Estrutura do dataset (df_final)", expanded=True):
    st.subheader("Colunas")
    st.write(list(df.columns))

    st.subheader("Tipos (dtypes)")
    dtypes_df = pd.DataFrame({"coluna": df.columns, "dtype": [str(t) for t in df.dtypes]})
    st.dataframe(dtypes_df, use_container_width=True, hide_index=True)

    st.subheader("Prévia (50 linhas)")
    st.dataframe(df.head(50), use_container_width=True)

st.divider()

# ===== Próximos passos (narrativa pública) =====
st.subheader("O que este painel vai mostrar")
st.markdown("""
Nesta etapa inicial, estamos conectando a base tratada para publicação.

Em seguida, esta página terá:
- KPIs: gasto total em 2025, gasto médio mensal, nº de servidores únicos
- Série temporal mensal do custo total
- Ranking por categoria (ex.: saúde, educação, etc.)
- Recorte de cargos comissionados (.c), quando aplicável
""")

render_footer()
