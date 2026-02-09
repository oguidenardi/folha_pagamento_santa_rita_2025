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


# ---------------------
# Panorama Geral 2025
# ---------------------
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


# ---------------------------------------------
# percentual de gênero por categoria de cargo
# ---------------------------------------------
st.markdown("""
# Percentual de gênero por categoria
""")
st.markdown("<br>", unsafe_allow_html=True)

# Dedup global + perfil por categoria
df_unico = df.drop_duplicates(subset="id_servidor").copy()

total_categoria = (
    df_unico.groupby("categoria_cargo")["id_servidor"]
    .nunique()
    .reset_index(name="total_categoria")
)

total_feminino = (
    df_unico[df_unico["genero"] == "F"]
    .groupby("categoria_cargo")["id_servidor"]
    .nunique()
    .reset_index(name="total_feminino")
)

perfil = total_categoria.merge(total_feminino, on="categoria_cargo", how="left")

perfil["total_feminino"] = perfil["total_feminino"].fillna(0).astype(int)
perfil["total_masculino"] = (perfil["total_categoria"] - perfil["total_feminino"]).astype(int)

perfil["percentual_feminino"] = (
    perfil["total_feminino"] / perfil["total_categoria"] * 100
).round(1)

perfil["percentual_masculino"] = (
    perfil["total_masculino"] / perfil["total_categoria"] * 100
).round(1)

# Ordena por tamanho da categoria (opcional)
perfil = perfil.sort_values("total_categoria", ascending=False)

# Mapa de nomes
NOME_CATEGORIA = {
    "operacional": "Operacional",
    "educacao": "Educação",
    "saude": "Saúde",
    "administrativo": "Administrativo",
    "comissionado": "Comissionado",
    "assistencia_social": "Assistência Social",
    "tecnico": "Técnico",
    "cultura": "Cultura",
    "politico": "Político",
    "juridico": "Jurídico",
}

def formatar_categoria(cat: str) -> str:
    cat = str(cat).strip()
    return NOME_CATEGORIA.get(cat, cat)

def servidor_singular_plural(n: int) -> str:
    return "servidor" if int(n) == 1 else "servidores"

# Donut function
DONUT_DOMAIN = ["Masculino", "Feminino"]
DONUT_RANGE = ["#0068c9", "#e377c2"]

def donut_genero_categoria(perfil_df: pd.DataFrame, categoria: str):
    subset = perfil_df.loc[perfil_df["categoria_cargo"] == categoria]
    if subset.empty:
        st.warning(f"Categoria não encontrada: {categoria}")
        return

    linha = subset.iloc[0]
    categoria_fmt = formatar_categoria(categoria)

    donut_df = pd.DataFrame({
        "genero": ["Masculino", "Feminino"],
        "percentual": [linha["percentual_masculino"], linha["percentual_feminino"]],
        "total": [linha["total_masculino"], linha["total_feminino"]],
    })

    st.markdown(f"#### {categoria_fmt}")

    donut = (
        alt.Chart(donut_df)
        .mark_arc(innerRadius=68, outerRadius=110)
        .encode(
            theta=alt.Theta("percentual:Q"),
            color=alt.Color(
                "genero:N",
                scale=alt.Scale(domain=DONUT_DOMAIN, range=DONUT_RANGE),
                legend=None
            ),
            tooltip=[
                alt.Tooltip("genero:N", title="Gênero"),
                alt.Tooltip("total:Q", title="Servidores"),
                alt.Tooltip("percentual:Q", title="Percentual", format=".1f"),
            ],
        )
        .properties(width=300, height=240)
    )

    total_cat = int(linha["total_categoria"])
    center_text = f"{total_cat}\n{servidor_singular_plural(total_cat)}"

    # Texto central único com plural correto (sem sobreposição)
    center = alt.Chart(pd.DataFrame({"text": [center_text]})).mark_text(
        fontSize=16,
        fontWeight="bold",
        lineHeight=18
    ).encode(text="text:N")

    st.altair_chart(donut + center, use_container_width=True)

    st.caption(
        f"F: {linha['percentual_feminino']:.1f}% ({int(linha['total_feminino'])}) • "
        f"M: {linha['percentual_masculino']:.1f}% ({int(linha['total_masculino'])})"
    )

# Render 2 por linha (usando as categorias do perfil)
cats = (
    perfil["categoria_cargo"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

for i in range(0, len(cats), 2):
    col1, col2 = st.columns(2)

    with col1:
        donut_genero_categoria(perfil, cats[i])

    with col2:
        if i + 1 < len(cats):
            donut_genero_categoria(perfil, cats[i + 1])
        else:
            st.empty()

    st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)

st.divider()



# --------------------------
# Custo anual por categoria
# --------------------------

st.markdown("""
# Custo anual por categoria
            
Esta análise apresenta o custo total da prefeitura com servidores públicos ao longo de 2025,
agrupado por categoria de cargo, considerando **todos os tipos de pagamento disponíveis na base**, incluindo:

- Salário base
- Vale-alimentação  
- Adiantamento do 13º salário  
- Fechamento do 13º salário  
- Rescisões  
- Folhas complementares com encargos
""")
st.markdown("<br>", unsafe_allow_html=True)
custo_anual_categoria = (
    df.groupby("categoria_cargo")["proventos"]
    .sum()
    .reset_index(name="custo_folha_anual_categoria")
    .sort_values("custo_folha_anual_categoria", ascending=False)
    .reset_index(drop=False)
)

custo = custo_anual_categoria.copy()

total_geral = custo["custo_folha_anual_categoria"].sum()

custo["percentual"] = (custo["custo_folha_anual_categoria"] / total_geral * 100).round(2)

def brl_label(v):
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:.1f} mi"
    return f"R$ {v/1_000:.0f} mil"

custo["valor_str"] = custo["custo_folha_anual_categoria"].apply(brl_label)
custo["label"] = custo["valor_str"] + " (" + custo["percentual"].map(lambda x: f"{x:.1f}%") + ")"


max_v = float(custo["custo_folha_anual_categoria"].max())

base = alt.Chart(custo).encode(
    y=alt.Y(
        "categoria_cargo:N",
        sort="-x",
        title=None,
        axis=alt.Axis(labelLimit=0)  # não truncar nomes (se precisar, depois a gente faz wrap)
    ),
    x=alt.X(
        "custo_folha_anual_categoria:Q",
        title="Custo total anual (R$)",
        axis=alt.Axis(format="~s"),  # exibe 1M, 2M, etc (apoio visual)
        scale=alt.Scale(domain=[0, max_v * 1.18])  # folga para não cortar labels
    ),
    tooltip=[
        alt.Tooltip("categoria_cargo:N", title="Categoria"),
        alt.Tooltip("valor_str:N", title="Custo anual"),
        alt.Tooltip("percentual:Q", title="% do total", format=".1f"),
    ]
)

bars = base.mark_bar(size=28)

labels = base.mark_text(
    align="left",
    baseline="middle",
    dx=10,
    fontSize=14,
    fontWeight="bold"
).encode(
    text="label:N"
)

chart = (bars + labels).properties(
    width=760,
    height=min(700, 38 * len(custo) + 80),
    padding={"right": 20},
    title=alt.TitleParams(
        text="Custo Anual Por Categoria",
        anchor="middle",
        fontSize=16,
        fontWeight="bold",
        offset=12
    )
)

st.altair_chart(chart, use_container_width=True)
st.markdown("""
- **Educação, Saúde e Operacional** concentram a maior parte das despesas anuais, representando
a espinha dorsal dos serviços públicos essenciais.
- Áreas como **Cultura, Jurídico e Técnico** possuem impacto financeiro significativamente menor,
tanto por menor número de servidores quanto pela estrutura salarial típica dessas funções.
- A análise evidencia como determinadas categorias — independentemente de salário médio —
carregam grande peso orçamentário devido ao seu **volume de servidores**.
- É possível observar a importância de separar o impacto de categorias com muitos servidores
(Operacional, Educação) das categorias com salários médios mais elevados, porém menor quadro funcional.
""")
st.divider()

#------------------------------------
# Top 10 salários mulheres e homens
#------------------------------------

st.markdown("""
# Os 10 maiores salários por gênero
""")
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<h3 style='text-align: center;'>10 maiores salários gênero masculino</h3>
""", unsafe_allow_html=True)

df_base_masc = df.copy()
df_masc_salario = df_base_masc[
    (df_base_masc["genero"] == "M") &
    (df_base_masc["tipo_pagamento"] == "folha_mensal")
]

top_10_salarios_masc = (
    df_masc_salario
    .groupby("cargo")["proventos"]
    .max()
    .reset_index(name="salario_maximo")
    .sort_values("salario_maximo", ascending=False)
)
top_10_salarios_masc = top_10_salarios_masc.head(10)

top_10_salarios_masc["salario_str"] = top_10_salarios_masc["salario_maximo"].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)


# Garantir índice limpo e criar ranking (1 a 10)
top_10_salarios_masc = top_10_salarios_masc.reset_index(drop=True).copy()
top_10_salarios_masc["rank"] = top_10_salarios_masc.index + 1
top_10_salarios_masc["rank_label"] = top_10_salarios_masc["rank"].astype(str) + "º"

# Folga no eixo X para não cortar o label do salário
max_sal = float(top_10_salarios_masc["salario_maximo"].max())

base = alt.Chart(top_10_salarios_masc).encode(
    y=alt.Y(
        "rank_label:N",
        sort=alt.SortField(field="rank", order="ascending"),
        title=None,
        axis=alt.Axis(labelAngle=0)
    ),
    x=alt.X(
        "salario_maximo:Q",
        title="Salário base (R$)",
        scale=alt.Scale(domain=[0, max_sal * 1.12])
    ),
    tooltip=[
        alt.Tooltip("rank:Q", title="Rank"),
        alt.Tooltip("cargo:N", title="Cargo (completo)"),
        alt.Tooltip("salario_str:N", title="Salário Máximo"),
    ]
)

bars = base.mark_bar(size=26, color="#0068c9")

labels = base.mark_text(
    align="left",
    baseline="middle",
    dx=10,
    fontSize=14,
    fontWeight="bold"
).encode(
    text="salario_str:N"
)

chart = (bars + labels).properties(
    width=720,
    height=430,
    padding={"right": 10}
)

st.altair_chart(chart, use_container_width=True)

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
st.markdown("**Cargos (por ordem do ranking):**")

for _, row in top_10_salarios_masc.iterrows():
    st.caption(f"**{int(row['rank'])}º** — {row['cargo']}")

st.markdown("""
- Cargo(s) com final .c refere-se a cargo comissionado/confiança.
""")
st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------
# Top 10 salários feminino
# ----------------------------
df_base_fem = df.copy()

df_fem_salario = df_base_fem[
    (df_base_fem["genero"] == "F") &
    (df_base_fem["tipo_pagamento"] == "folha_mensal")
]

top_10_salarios_fem = (
    df_fem_salario
    .groupby("cargo")["proventos"]
    .max()
    .reset_index(name="salario_maximo")
    .sort_values("salario_maximo", ascending=False)
    .head(10)
    .reset_index(drop=True)
)

# Ranking (1 a 10)
top_10_salarios_fem["rank"] = top_10_salarios_fem.index + 1
top_10_salarios_fem["rank_label"] = top_10_salarios_fem["rank"].astype(str) + "º"

# Formatação BR do salário
top_10_salarios_fem["salario_str"] = top_10_salarios_fem["salario_maximo"].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

st.markdown(
    "<h3 style='text-align: center;'>10 maiores salários gênero feminino</h3>",
    unsafe_allow_html=True
)

max_sal = float(top_10_salarios_fem["salario_maximo"].max())

base = alt.Chart(top_10_salarios_fem).encode(
    y=alt.Y(
        "rank_label:N",
        sort=alt.SortField(field="rank", order="ascending"),
        title=None,
        axis=alt.Axis(labelAngle=0)
    ),
    x=alt.X(
        "salario_maximo:Q",
        title="Salário base (R$)",
        scale=alt.Scale(domain=[0, max_sal * 1.12])  # folga para não cortar labels
    ),
    tooltip=[
        alt.Tooltip("rank:Q", title="Rank"),
        alt.Tooltip("cargo:N", title="Cargo (completo)"),
        alt.Tooltip("salario_str:N", title="Salário Máximo"),
    ]
)

bars = base.mark_bar(size=26, color="#e377c2")

labels = base.mark_text(
    align="left",
    baseline="middle",
    dx=10,
    fontSize=14,
    fontWeight="bold"
).encode(
    text="salario_str:N"
)

chart = (bars + labels).properties(
    width=720,
    height=430,
    padding={"right": 10}
)

st.altair_chart(chart, use_container_width=True)


st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
st.markdown("**Cargos (por ordem do ranking):**")

for _, row in top_10_salarios_fem.iterrows():
    st.caption(f"**{int(row['rank'])}º** — {row['cargo']}")

st.markdown("""
- Cargo(s) com final .c refere-se a cargo comissionado/confiança.
""")
st.divider()
