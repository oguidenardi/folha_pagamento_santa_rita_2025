import streamlit as st

from components.ui import info_box
from config.app_texts import DISCLAIMER
from components.layout import render_header, render_footer


st.set_page_config(
    page_title="Sana Rita Data",
    page_icon="📊",
    layout="wide",
)

render_header()

st.markdown("""
Este site apresenta análises públicas sobre a **folha de pagamento de 2025** dos servidores municipais de
**Santa Rita do Passa Quatro (SP)**, com base em dados do Portal da Transparência.

Use o menu lateral para navegar pelas páginas do painel:
- **Visão Geral**
- **Pessoas & Estrutura**
- **Comissionados (.c)**
- **Top Salários**
- **Metodologia & Limitações**
""")

info_box("ℹ️ Avisos Importantes", DISCLAIMER, expanded=True)

render_footer()
