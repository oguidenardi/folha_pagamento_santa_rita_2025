import streamlit as st
from config.app_texts import APP_TITLE, APP_SUBTITLE, DATA_SOURCE


def render_header():
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)

def render_footer():
    st.divider()
    st.caption(DATA_SOURCE)
    st.caption("Desenvolvido em Python + Streamlit + Metodologia CRISP-DM")