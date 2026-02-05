import pandas as pd
import streamlit as st
from pathlib import Path
from config.constants import PROCESSED_DATA_DIR

@st.cache_data(show_spinner="Carregando base processada...")
def load_folha_pagamento_2025(filename: str) -> pd.DataFrame:
    # Monta o caminho completo
    path = Path(PROCESSED_DATA_DIR) / filename

    # Verifica existência
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {path.resolve()}\n"
            f"Verifique se ele está em '{PROCESSED_DATA_DIR}' "
            f"e se o nome informado em DF_FINAL_FILE está correto."
        )

    # Verifica formato
    if path.suffix.lower() != ".parquet":
        raise ValueError(
            f"Formato inválido: {path.suffix}. "
            "Use um arquivo .parquet em data/processed."
        )

    # Carrega o parquet
    df = pd.read_parquet(path)

    # Limpeza defensiva de colunas
    df.columns = [c.strip() for c in df.columns]

    return df
