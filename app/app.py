import pandas as pd
import altair as alt
import streamlit as st
from pathlib import Path


st.set_page_config(
    page_title="Santa Rita Data",
    page_icon="📊",
    layout="centered",
)

DATA_PATH = Path("data/processed/folha-pagamento-2025.parquet")
CURRENCY_PREFIX = "R$"

#carregar dados do parquet
@st.cache_data(show_spinner="Carregando dados..")
def load_data():
    return pd.read_parquet(DATA_PATH)

df = load_data()


# Utilidades de formatação
def br_money(x: float) -> str:
    if pd.isna(x):
        return "-"
    
    s = f"{x:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    
    return f"{CURRENCY_PREFIX} {s}"

def section_divider():
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

st.image("assets/images/santa-rita-data.png")

st.markdown("""
# Folha Pagamento 2025 - Santa Rita do Passa Quatro(SP)

A disponibilização de dados públicos por meio do **Portal da Transparência** permite avaliar como os recursos municipais são aplicados, especialmente no que diz respeito às despesas com **pessoal**, que representam uma das maiores parcelas do orçamento público.

Fonte dos dados:  
- Portal da Transparência — Prefeitura de Santa Rita do Passa Quatro/SP  
  https://www.transparencia.prefsrpq.com.br/transparencia/
            
## Considerações Éticas e LGPD

Embora os dados utilizados sejam **públicos** e disponibilizados oficialmente pelo Portal da Transparência, este projeto adota boas práticas de **privacidade, ética e conformidade com a LGPD**, incluindo:

- Anonimização de nomes e qualquer informação que possa identificar indivíduos.
- Não exposição de dados sensíveis ou inferências que possam causar constrangimento ou interpretação indevida.
- Uso dos dados exclusivamente para fins **educacionais**, **analíticos** e de **transparência pública**, sem finalidade comercial.
- Documentação clara das transformações aplicadas, garantindo rastreabilidade e respeito ao caráter público dos dados.
            
### Abaixo uma amostra dos dados utilizados:
""")

st.dataframe(df.head(), use_container_width=True, hide_index=True)

st.divider()

# Panorama geral 2025
st.markdown("""
<style>
.kpi-card {
  border: 1px solid rgba(0,0,0,.18);
  border-radius: 18px;
  padding: 24px 28px;
  box-shadow: 0 8px 30px rgba(0,0,0,.06);
  background: rgba(255,255,255,.95);
}

.kpi-title {
  color: rgba(0,0,0,.70);
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 12px;
}

p.kpi-value {
  font-size: 2.1rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.1;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
# Panorama Geral 2025
""")

total_servidores = df["id_servidor"].nunique()
total_proventos = df["proventos"].sum()

total_servidores_str = f"{total_servidores}"
total_proventos_str = br_money(total_proventos)

c1, c2 = st.columns(2)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-title">Total de servidores</div>
      <p class="kpi-value">{total_servidores_str}</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-title">Total Gasto</div>
      <p class="kpi-value">{total_proventos_str}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)


# distribuição por gênero
st.markdown("""
## Distribuição de servidores por gênero
""")

df_unico = df.drop_duplicates(subset="id_servidor")

total_masculino = df_unico[df_unico["genero"] == "M"].shape[0]
total_feminino = df_unico[df_unico["genero"] == "F"].shape[0]

total_masc_str = f"{total_masculino}"
total_fem_str = f"{total_feminino}"

c3, c4 = st.columns(2)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-title">Feminino</div>
      <p class="kpi-value">{total_fem_str}</p>
    </div>
""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-title">Masculino</div>
      <p class="kpi-value">{total_masc_str}</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# gráfico % de gênero
df_unico = df.drop_duplicates(subset="id_servidor")

contagem_genero = (
    df_unico["genero"]
    .value_counts()
    .rename_axis("genero")
    .reset_index(name="total_servidores")
)

contagem_genero["percentual"] = (
    contagem_genero["total_servidores"] /
    contagem_genero["total_servidores"].sum() * 100
).round(1)

# string já com %
contagem_genero["percentual_str"] = contagem_genero["percentual"].astype(int).astype(str) + "%"

base = alt.Chart(contagem_genero).encode(
    x=alt.X("genero:N", title="Gênero", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("total_servidores:Q", title="Total de Servidores")
)

bars = base.mark_bar(size=90)

# número absoluto em cima
labels_top = base.mark_text(
    dy=-8,
    fontSize=16,
    fontWeight="bold"
).encode(
    text="total_servidores:Q"
)

# percentual no meio (com %)
labels_center = (
    alt.Chart(contagem_genero)
    .transform_calculate(y_mid="datum.total_servidores / 2")
    .mark_text(
        fontSize=18,
        fontWeight="bold",
        color="white"
    )
    .encode(
        x=alt.X("genero:N", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("y_mid:Q", title=None),
        text=alt.Text("percentual_str:N")
    )
)

chart = (bars + labels_top + labels_center).properties(
    width=500,
    height=350
)

st.altair_chart(chart, use_container_width=True)
st.divider()


# desligamentos por genero
st.markdown("""
# Desligamentos de servidores por gênero em 2025
Em 2025 foram registrados 155 desligamentos, abaixo podemos verificar o número de desligamento por gênero e suas respectivas porcentagens.
""")
df_desligados_2025 = df[
    df["data_desligamento"].notna() &
    (df["data_desligamento"].dt.year == 2025)
]
desligados_genero = (
    df_desligados_2025["genero"]
    .value_counts()
    .loc[["F", "M"]]
    .reset_index()
)
desligados_genero.columns = ["genero", "total_desligados"]

total_desligado = desligados_genero["total_desligados"].sum()
desligados_genero["percentual"] = (
    desligados_genero["total_desligados"] / total_desligado * 100
).round(1)

desligados_genero["percentual_str"] = desligados_genero["percentual"].astype(int).astype(str) + "%"

st.markdown("<br><br>", unsafe_allow_html=True)

df_desligados_2025 = df[
    df["data_desligamento"].notna() &
    (df["data_desligamento"].dt.year == 2025)
]

desligados_genero = (
    df_desligados_2025["genero"]
    .value_counts()
    .loc[["F", "M"]]
    .reset_index()
)
desligados_genero.columns = ["genero", "total_desligados"]

total_desligado = desligados_genero["total_desligados"].sum()

desligados_genero["percentual"] = (
    desligados_genero["total_desligados"] / total_desligado * 100
)

desligados_genero["percentual_str"] = desligados_genero["percentual"].round(1).astype(str) + "%"

# Gráfico de barras
base2 = alt.Chart(desligados_genero).encode(
    x=alt.X("genero:N", title="Gênero", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("total_desligados:Q", title="Total de desligados")
)

bars2 = base2.mark_bar(size=90)

# Número absoluto em cima
labels_top2 = base2.mark_text(
    dy=-8,
    fontSize=16,
    fontWeight="bold"
).encode(
    text="total_desligados:Q"
)

# Percentual dentro da barra
labels_center2 = (
    alt.Chart(desligados_genero)
    .transform_calculate(y_mid="datum.total_desligados / 2")
    .mark_text(
        fontSize=18,
        fontWeight="bold",
        color="white"
    )
    .encode(
        x="genero:N",
        y="y_mid:Q",
        text="percentual_str:N"
    )
)

chart2 = (bars2 + labels_top2 + labels_center2).properties(
    width=500,
    height=350
)

st.altair_chart(chart2, use_container_width=True)
st.divider()
