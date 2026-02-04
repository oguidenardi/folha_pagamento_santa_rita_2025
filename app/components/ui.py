import streamlit as st

def info_box(title: str, md: str, expanded: bool = True):
    with st.expander(title, expanded=expanded):
        st.markdown(md)
