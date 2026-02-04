import streamlit as st
from components.layout import render_header, render_footer

render_header()
st.header("📌 Visão Geral")
st.info("Em seguida vamos conectar a base em data/processed e montar KPIs + série temporal + ranking.")
render_footer()
