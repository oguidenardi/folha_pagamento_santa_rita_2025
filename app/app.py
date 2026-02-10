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

df_base = df.copy()

# Flag comissionado por LINHA (robusta a NaN e espaços)
df_base["is_comissionado"] = (
    df_base["cargo"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.lower()
    .str.endswith(".c")
)

# Helper: primeiro valor não nulo
def first_notna(s: pd.Series):
    s = s.dropna()
    return s.iloc[0] if len(s) else None

df_unico = (
    df_base.groupby("id_servidor", as_index=False)
    .agg(
        genero=("genero", first_notna),
        categoria_cargo=("categoria_cargo", first_notna),
        is_comissionado=("is_comissionado", "any"),
    )
)

# Se ANY ".c" => categoria vira comissionado (regra por servidor)
df_unico.loc[df_unico["is_comissionado"], "categoria_cargo"] = "comissionado"

# padroniza categoria para evitar inconsistências de casing/espaço
df_unico["categoria_cargo"] = (
    df_unico["categoria_cargo"]
    .astype(str)
    .str.strip()
    .str.lower()
    .replace({"nan": None})
)

# Remove a coluna auxiliar
df_unico = df_unico.drop(columns=["is_comissionado"])

# Agregações por categoria
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

# evita divisão por zero
perfil["percentual_feminino"] = (
    (perfil["total_feminino"] / perfil["total_categoria"].replace({0: pd.NA})) * 100
).round(1).fillna(0.0)

perfil["percentual_masculino"] = (
    (perfil["total_masculino"] / perfil["total_categoria"].replace({0: pd.NA})) * 100
).round(1).fillna(0.0)

# Ordena por tamanho da categoria
perfil = perfil.sort_values("total_categoria", ascending=False)

# ---------------------------------------------
# Mapa de nomes
# ---------------------------------------------
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
    cat = str(cat).strip().lower()
    return NOME_CATEGORIA.get(cat, cat)

def servidor_singular_plural(n: int) -> str:
    return "servidor" if int(n) == 1 else "servidores"

DONUT_DOMAIN = ["Masculino", "Feminino"]
DONUT_RANGE = ["#0068c9", "#e377c2"]

def donut_genero_categoria(perfil_df: pd.DataFrame, categoria: str):
    categoria = str(categoria).strip().lower()
    subset = perfil_df.loc[perfil_df["categoria_cargo"].astype(str).str.strip().str.lower() == categoria]

    if subset.empty:
        st.warning(f"Categoria não encontrada: {categoria}")
        return

    linha = subset.iloc[0]
    categoria_fmt = formatar_categoria(categoria)

    total_cat = int(linha["total_categoria"])
    total_f = int(linha["total_feminino"])
    total_m = int(linha["total_masculino"])

    # percentuais recalculados a partir dos totais (evita drift por arredondamento)
    if total_cat > 0:
        pct_f = round((total_f / total_cat) * 100, 1)
        pct_m = round((total_m / total_cat) * 100, 1)
    else:
        pct_f, pct_m = 0.0, 0.0

    donut_df = pd.DataFrame({
        "genero": ["Masculino", "Feminino"],
        "percentual": [pct_m, pct_f],
        "total": [total_m, total_f],
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
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("genero:N", title="Gênero"),
                alt.Tooltip("total:Q", title="Servidores"),
                alt.Tooltip("percentual:Q", title="Percentual", format=".1f"),
            ],
        )
        .properties(width=300, height=240)
    )

    center_text = f"{total_cat}\n{servidor_singular_plural(total_cat)}"
    center = (
        alt.Chart(pd.DataFrame({"text": [center_text]}))
        .mark_text(fontSize=16, fontWeight="bold", lineHeight=18)
        .encode(text="text:N")
    )

    st.altair_chart(donut + center, use_container_width=True)

    st.caption(f"F: {pct_f:.1f}% ({total_f}) • M: {pct_m:.1f}% ({total_m})")


# Render 2 por linha
cats = (
    perfil["categoria_cargo"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.lower()
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

# -----------------------
# Top 10 salários geral
# -----------------------
st.markdown("""
# Maiores Salários de 2025
            
O levantamento dos 10 maiores salários pagos pela Prefeitura ao longo de 2025 revela uma forte presença da área da Saúde no topo da remuneração do funcionalismo. 
As três primeiras posições são ocupadas por profissionais médicos, com destaque para o **Médico PSF**, que lidera o ranking, 
seguido por outro servidor da mesma função.
Em 5º lugar, mais um médico do PSF reforça esse predomínio.
O alto escalão jurídico aparece em seguida: o **Procurador Geral do Município** ocupa a **3ª posição**, enquanto o **Procurador Jurídico** surge em **4º**.

Entre os cargos de direção, o **Prefeito** se encontra na **6ª colocação**.

Funções administrativas também marcam presença no topo da lista. O cargo de **Agente Administrativo** aparece na **7ª posição**, evidenciando que, 
embora seja uma função de natureza administrativa, pode alcançar remunerações próximas às de chefia.

Fechando o ranking, outras duas posições são ocupadas por profissionais médicos — ambos com o mesmo salário
— e o **Médico de Pronto Atendimento**, completa a 10ª posição.

No conjunto, o ranking evidencia que a **Saúde lidera com folga** entre os maiores salários, seguida pelo **núcleo jurídico** e 
pelos **cargos de direção** do Executivo Municipal.
""")

st.markdown("<br><br>", unsafe_allow_html=True)

df_mensal = df[df["tipo_pagamento"] == "folha_mensal"].copy()

df_mensal_unico = (
    df_mensal
    .sort_values(["id_servidor", "proventos"], ascending=[True, False])
    .drop_duplicates(subset=["id_servidor"], keep="first")
    .copy()
)

# Ranking dos 10 maiores salários de 2025
top_10_salarios_geral = (
    df_mensal_unico.groupby(["id_servidor", "cargo", "genero"])["proventos"]
    .max()
    .reset_index(name="salario_maximo")
    .sort_values("salario_maximo", ascending=False)
    .head(10)
    .reset_index(drop=True)
)

# Formatar para exibição
top_10_salarios_geral["salario_str"] = top_10_salarios_geral["salario_maximo"].apply(br_money)

# ranking numerico
top_10_salarios_geral["rank"] = top_10_salarios_geral.index + 1
top_10_salarios_geral["rank_label"] = top_10_salarios_geral["rank"].astype(str) + "º"

df_plot = top_10_salarios_geral.copy()

max_sal = float(df_plot["salario_maximo"].max())

base = alt.Chart(df_plot).encode(
    y=alt.Y(
        "rank_label:N",
        sort=alt.SortField(field="rank", order="ascending"),
        title=None,
        axis=alt.Axis(labelAngle=0)
    ),
    x=alt.X(
        "salario_maximo:Q",
        title="Salário base mensal (R$)",
        scale=alt.Scale(domain=[0, max_sal * 1.12])
    ),
    tooltip=[
        alt.Tooltip("rank:Q", title="Rank"),
        alt.Tooltip("cargo:N", title="Cargo"),
        alt.Tooltip("genero:N", title="Gênero"),
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
    padding={"right": 20},
    title=alt.TitleParams(
        text="Top 10 Maiores Salários",
        anchor="middle",
        fontSize=16,
        fontWeight="bold",
        offset=12
    )
)

st.altair_chart(chart, use_container_width=True)

# Lista textual para mobile
st.markdown("**Cargos (por ordem do ranking):**")
for _, row in df_plot.iterrows():
    st.caption(f"**{int(row['rank'])}º** — {row['cargo']} — Salário: {row['salario_str']}")


# -------------------------
# Top 10 genero masculino
# -------------------------
st.markdown("""
## Os 10 maiores salários por gênero - 2025
            
### Gênero masculino
""")
st.markdown("<br>", unsafe_allow_html=True)
# Filtra apenas servidores do gênero masculino + folha mensal
df_masc = df[
    (df["genero"] == "M") &
    (df["tipo_pagamento"] == "folha_mensal")
].copy()

# Mantém somente 1 linha por servidor (maior salário mensal observado no ano)
df_masc_1por = (
    df_masc.sort_values(["id_servidor", "proventos"], ascending=[True, False])
           .drop_duplicates(subset=["id_servidor"], keep="first")
           .copy()
)

# Seleciona top 10 salários
top_10_salarios_masc = (
    df_masc_1por.groupby(["id_servidor", "cargo"])["proventos"]
    .max()
    .reset_index(name="salario_maximo")
    .sort_values("salario_maximo", ascending=False)
    .head(10)
    .reset_index(drop=True)
)

# Formatação para exibição
top_10_salarios_masc["salario_str"] = top_10_salarios_masc["salario_maximo"].apply(br_money)

# Ranking numérico
top_10_salarios_masc["rank"] = top_10_salarios_masc.index + 1
top_10_salarios_masc["rank_label"] = top_10_salarios_masc["rank"].astype(str) + "º"


df_plot = top_10_salarios_masc.copy()
max_sal = float(df_plot["salario_maximo"].max())

base = alt.Chart(df_plot).encode(
    y=alt.Y(
        "rank_label:N",
        sort=alt.SortField(field="rank", order="ascending"),
        title=None,
        axis=alt.Axis(labelAngle=0)
    ),
    x=alt.X(
        "salario_maximo:Q",
        title="Salário base mensal (R$)",
        scale=alt.Scale(domain=[0, max_sal * 1.12])
    ),
    tooltip=[
        alt.Tooltip("rank:Q", title="Rank"),
        alt.Tooltip("cargo:N", title="Cargo"),
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
    padding={"right": 20},
    title=alt.TitleParams(
        text="Top 10 Maiores Salários — Servidores do Gênero Masculino (2025)",
        anchor="middle",
        fontSize=16,
        fontWeight="bold",
        offset=12
    )
)

st.altair_chart(chart, use_container_width=True)

# Lista textual para facilitar leitura no mobile
st.markdown("**Cargos (por ordem do ranking):**")
for _, row in df_plot.iterrows():
    st.caption(f"**{int(row['rank'])}º** — {row['cargo']} — Salário: {row['salario_str']}")

st.markdown("<br>", unsafe_allow_html=True)


# -------------------------
# Top 10 genero feminino
# -------------------------

st.markdown("""
### Gênero Feminino
""")
st.markdown("<br>", unsafe_allow_html=True)
# Filtra apenas servidores do gênero masculino + folha mensal
df_fem = df[
    (df["genero"] == "F") &
    (df["tipo_pagamento"] == "folha_mensal")
].copy()

# Mantém somente 1 linha por servidor (maior salário mensal observado no ano)
df_fem_1por = (
    df_fem.sort_values(["id_servidor", "proventos"], ascending=[True, False])
           .drop_duplicates(subset=["id_servidor"], keep="first")
           .copy()
)

# Seleciona top 10 salários
top_10_salarios_fem = (
    df_fem_1por.groupby(["id_servidor", "cargo"])["proventos"]
    .max()
    .reset_index(name="salario_maximo")
    .sort_values("salario_maximo", ascending=False)
    .head(10)
    .reset_index(drop=True)
)

# Formatação para exibição
top_10_salarios_fem["salario_str"] = top_10_salarios_fem["salario_maximo"].apply(br_money)

# Ranking numérico
top_10_salarios_fem["rank"] = top_10_salarios_fem.index + 1
top_10_salarios_fem["rank_label"] = top_10_salarios_fem["rank"].astype(str) + "º"


df_plot = top_10_salarios_fem.copy()
max_sal = float(df_plot["salario_maximo"].max())

base = alt.Chart(df_plot).encode(
    y=alt.Y(
        "rank_label:N",
        sort=alt.SortField(field="rank", order="ascending"),
        title=None,
        axis=alt.Axis(labelAngle=0)
    ),
    x=alt.X(
        "salario_maximo:Q",
        title="Salário base mensal (R$)",
        scale=alt.Scale(domain=[0, max_sal * 1.12])
    ),
    tooltip=[
        alt.Tooltip("rank:Q", title="Rank"),
        alt.Tooltip("cargo:N", title="Cargo"),
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
    padding={"right": 20},
    title=alt.TitleParams(
        text="Top 10 Maiores Salários — Servidores do Gênero Feminino (2025)",
        anchor="middle",
        fontSize=16,
        fontWeight="bold",
        offset=12
    )
)

st.altair_chart(chart, use_container_width=True)

# Lista textual para facilitar leitura no mobile
st.markdown("**Cargos (por ordem do ranking):**")
for _, row in df_plot.iterrows():
    st.caption(f"**{int(row['rank'])}º** — {row['cargo']} — Salário: {row['salario_str']}")

st.markdown("""
## Conclusão — Maiores Salários de 2025

A análise dos maiores salários pagos pela Prefeitura ao longo de 2025 revela um cenário em que a **área da Saúde domina amplamente as primeiras posições**, tanto entre homens quanto entre mulheres. O cargo de **Médico PSF** aparece no topo dos dois rankings, reforçando o peso estratégico desse serviço dentro da administração municipal.

No grupo masculino, além da Saúde, aparecem funções de alto impacto institucional, como **Procurador Jurídico**, **Prefeito** e cargos administrativos especializados. Já entre as mulheres, destaca-se a presença da **Procuradora Geral do Município**, ocupando a 2ª posição, além de um número expressivo de **professoras**, que compõem boa parte das posições intermediárias do ranking feminino.

Em síntese, os dados mostram que os salários mais elevados estão concentrados principalmente em três frentes:  
- **Profissionais da Saúde** (PSF, clínico geral, pediatria, pronto atendimento);  
- **Carreiras jurídicas e de direção** (Procurador Jurídico, Procurador Geral, Prefeito, Diretor de Departamento);  
- **Funções administrativas qualificadas**, com destaque para Agente Administrativo.

A combinação desses fatores evidencia que as remunerações mais altas se distribuem entre cargos de **alta responsabilidade técnica**, **chefia** e **atendimento direto à população**, revelando a estrutura salarial das áreas que sustentam as atividades essenciais da gestão pública no município.

""")
st.divider()

# ---------------------
# Cargos Comissionados
# ---------------------

st.markdown("""
# Cargos Comissionados

Os cargos comissionados representam uma parcela estratégica da estrutura administrativa da Prefeitura. 
Diferentemente dos cargos efetivos, eles são ocupados por profissionais nomeados diretamente pela gestão, geralmente para funções de confiança, 
direção, assessoramento ou coordenação de políticas públicas.

Em 2025, Santa Rita do Passa Quatro contou com um grupo expressivo de servidores comissionados, 
distribuídos em áreas como administração, assistência social, planejamento, educação, saúde e gestão de pessoas. 
Esses profissionais desempenham papéis essenciais no funcionamento do governo, atuando em postos que envolvem tomada de decisão, 
supervisão de equipes e execução de projetos de interesse público.

A seguir, apresentamos uma lista detalhada de todos os cargos comissionados existentes no município ao longo do ano, 
acompanhada do número de pessoas que ocuparam cada função. Essa transparência é fundamental para que o cidadão possa compreender como 
a máquina pública é organizada e onde estão alocados os cargos de confiança da administração municipal.
""")

df_cargos_c = df[df["cargo"].str.endswith(".c", na=False)].copy()

df_cargos_c_unico = df_cargos_c.drop_duplicates(subset="id_servidor").copy()

cargos_comissionados_lista = (
    df_cargos_c_unico
    .groupby("cargo")["id_servidor"]
    .nunique()
    .reset_index(name="quantidade_servidores")
    .sort_values("quantidade_servidores", ascending=False)
    .reset_index(drop=True)
)

st.markdown("""
## Lista de Cargos Comissionados e Quantidade de Servidores (2025)
""")
st.dataframe(
    cargos_comissionados_lista.rename(columns={
        "cargo": "Cargo Comissionado",
        "quantidade_servidores": "Quantidade de Servidores"
    }),
    use_container_width=True,
    hide_index=True
)

st.markdown("""
### O que mostra a lista de cargos comissionados

A distribuição dos cargos comissionados ao longo de 2025 revela uma estrutura voltada principalmente para funções de assessoria e coordenação. 
O cargo com maior número de ocupantes foi o de **Assessor de Implementação de Políticas Públicas**, com **19 servidores**, 
evidenciando a necessidade de suporte operacional e técnico em áreas estratégicas da administração.

Em seguida, a função de **Assessor de Gabinete de Diretor de Departamento** aparece com **12 ocupantes**, 
reforçando o papel de apoio direto às chefias das diferentes áreas da Prefeitura. Já o cargo de **Assessor de Gabinete**, com **4 servidores**, 
também se destaca como uma função que oferece suporte administrativo à gestão.

Os demais cargos comissionados são majoritariamente posições de direção, cada uma exercida por apenas **1 ou 2 servidores**, 
como **Diretor do Departamento de Administração**, **Procurador Geral do Município**, **Diretor de Finanças**, **Diretor de Obras e Engenharia**, 
**Diretor de Educação**, entre outros. Isso mostra que a estrutura comissionada é composta, em grande parte, 
por postos de liderança que coordenam setores essenciais do governo municipal.

No conjunto, a listagem revela que os cargos comissionados cumprem papéis distintos: 
uma base numerosa de assessores garantindo o funcionamento diário da administração e um conjunto de diretores 
responsáveis pela condução estratégica das políticas públicas. Essa divisão ajuda a entender como a Prefeitura distribui 
responsabilidades e organiza sua força de trabalho de confiança ao longo do ano.
""")

st.markdown("""
### Distribuição por gênero entre os cargos comissionados

Entre os **53 servidores comissionados** que atuaram na Prefeitura ao longo de 2025, a distribuição por gênero mostra 
um quadro relativamente equilibrado, mas ainda com leve predominância masculina. 
Do total, **29 cargos foram ocupados por homens** (54,7%) e **24 por mulheres** (45,3%).

Esse equilíbrio aparece tanto em funções de assessoria quanto nos cargos de direção, 
demonstrando que a presença feminina está distribuída por diferentes áreas da administração. 
A leitura conjunta desses números ajuda a entender como os cargos de confiança são ocupados e como se 
desenha a composição da equipe estratégica do governo municipal.
""")
st.markdown("<br>", unsafe_allow_html=True)

df_comissionados = df[df["categoria_cargo"] == "comissionado"].drop_duplicates("id_servidor")
total_masc = (df_comissionados["genero"] == "M").sum()
total_fem = (df_comissionados["genero"] == "F").sum()


total = total_masc + total_fem
pct_masc = round((total_masc / total) * 100, 1)
pct_fem = round((total_fem / total) * 100, 1)


dados_genero = pd.DataFrame({
    "genero": ["Masculino", "Feminino"],
    "quantidade": [total_masc, total_fem],
    "percentual": [pct_masc, pct_fem]
})


cores_genero = {
    "Masculino": "#0068c9",
    "Feminino": "#e377c2"
}


dados_genero["meio_barra"] = dados_genero["quantidade"] / 2
dados_genero["percentual_formatado"] = dados_genero["percentual"].round(0).astype(int).astype(str) + "%"


cores_genero = {
    "Masculino": "#0068c9",
    "Feminino": "#e377c2"
}


chart = (
    alt.Chart(dados_genero)
    .mark_bar(size=130)
    .encode(
        x=alt.X("genero:N", title="", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("quantidade:Q", title="Quantidade de Servidores"),
        color=alt.Color(
            "genero:N",
            scale=alt.Scale(domain=list(cores_genero.keys()),
                            range=list(cores_genero.values())),
            legend=None
        ),
        tooltip=[
            alt.Tooltip("genero:N", title="Gênero"),
            alt.Tooltip("quantidade:Q", title="Total"),
            alt.Tooltip("percentual:Q", title="Percentual (%)", format=".0f")
        ]
    )
    .properties(
        width=450,
        height=420,
        title=alt.TitleParams(
            text="Distribuição de Servidores Comissionados por Gênero (2025)",
            anchor="middle",
            fontSize=16,
            fontWeight="bold",
            offset=12
        )
    )
)


labels_top = (
    alt.Chart(dados_genero)
    .mark_text(
        dy=-12,
        fontSize=16,
        fontWeight="bold"
    )
    .encode(
        x="genero:N",
        y="quantidade:Q",
        text="quantidade:Q"
    )
)


labels_inside = (
    alt.Chart(dados_genero)
    .mark_text(
        align="center",
        baseline="middle",
        color="white",
        fontSize=16,
        fontWeight="bold"
    )
    .encode(
        x="genero:N",
        y=alt.Y("meio_barra:Q"),
        text="percentual_formatado:N"
    )
)


st.altair_chart(chart + labels_top + labels_inside, use_container_width=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
### Lista completa de Cargos Comissionados e seus salários
""")
st.markdown("<br>", unsafe_allow_html=True)

df_com_all = df[df["categoria_cargo"] == "comissionado"].copy()
df_com_all["id_servidor"] = df_com_all["id_servidor"].astype(str)
df_com_all["cargo"] = df_com_all["cargo"].astype(str)

df_com = df[
    (df["categoria_cargo"] == "comissionado") &
    (df["tipo_pagamento"] == "folha_mensal")
].copy()

df_com["proventos"] = pd.to_numeric(df_com["proventos"], errors="coerce")
df_com = df_com.dropna(subset=["proventos", "id_servidor", "cargo"]).copy()
df_com["id_servidor"] = df_com["id_servidor"].astype(str)
df_com["cargo"] = df_com["cargo"].astype(str)

df_com_1por_servidor = (
    df_com.sort_values(["id_servidor", "proventos"], ascending=[True, False])
    .drop_duplicates(subset=["id_servidor"], keep="first")
    .copy()
)

tabela_competa = (
    df_com_1por_servidor.groupby("cargo", as_index=False)
    .agg(
        salario_base_mensal = ("proventos", "max"),
        quantidade_pessoas = ("id_servidor", "nunique")
    )
)

ids_all = set(df_com_all["id_servidor"].unique())
ids_fm = set(df_com["id_servidor"].unique())
faltantes_ids = list(ids_all - ids_fm)

df_faltantes = (
    df_com_all[df_com_all["id_servidor"].isin(faltantes_ids)][
        ["id_servidor", "cargo", "tipo_pagamento"]
    ]
    .drop_duplicates(subset=["id_servidor"])
    .copy()
)

if not df_faltantes.empty:
    linhas_extra = (
        df_faltantes.groupby("cargo", as_index=False)
        .agg(quantidade_pessoas=("id_servidor", "nunique"))
    )
    linhas_extra["salario_base_mensal"] = pd.NA
    tabela_completa = pd.concat([tabela_competa, linhas_extra], ignore_index=True)

tabela_completa["salario_str"] = tabela_completa["salario_base_mensal"].apply(br_money)

tabela_completa = tabela_completa.sort_values(
    by="salario_base_mensal",
    ascending=False,
    na_position="last"
).reset_index(drop=True)

tabela_exibicao = tabela_completa[
    ["cargo", "salario_str", "quantidade_pessoas"]
].rename(
    columns = {
        "cargo": "Cargo Comissionado",
        "salario_str": "Salário Base",
        "quantidade_pessoas": "Qtd. de Pessoas"
    }
)

st.dataframe(tabela_exibicao, use_container_width=True, hide_index=True)
st.caption(
    f"Total de Servidores comissionados identificados: {len(ids_all)}.\n"
    f"Servidores exclusivamente com rescisão em 2025: {len(faltantes_ids)}"
)

st.markdown("""
### Entenda a Estrutura dos Cargos Comissionados em 2025

A lista completa dos cargos comissionados da Prefeitura revela como está distribuída a estrutura de confiança da 
administração municipal ao longo de 2025. Os dados mostram uma combinação de **cargos de direção**, 
que concentram os maiores salários, e um **grande contingente de assessores**, 
responsáveis por dar suporte às diferentes áreas do governo.

O posto mais bem remunerado é o de **Procurador Geral do Município**, 
com salário base mensal de **R\$ 24.687,05**, ocupando isoladamente o topo da estrutura. 
Na sequência, aparecem diretores de áreas estratégicas, como **Agricultura e Meio Ambiente**, 
**Educação**, **Desenvolvimento Urbano** e **Assistência Social**, 
todos com salários acima de **R\$ 10 mil**, refletindo funções de alta responsabilidade dentro da gestão.

Entre os cargos mais numerosos, destacam-se os de **Assessor de Implementação de Políticas Públicas**, 
com **17 servidores**, e **Assessor de Gabinete de Diretor de Departamento**, com **12 servidores**, 
indicando que grande parte da força comissionada está concentrada em funções de apoio direto à administração. 
Já o cargo de **Assessor de Gabinete** aparece duas vezes na listagem: quatro servidores com salário base e 
mais um caso registrado apenas com rescisão, sem pagamento mensal.

Na base da estrutura aparece o cargo de **Gestor Adjunto de Ensino Fundamental**, 
com salário de **R\$ 2.217,63**, representando o menor vencimento entre os comissionados.

A leitura da tabela completa evidencia uma estrutura com salários bastante variados, 
mas com um padrão claro: **altas remunerações nos cargos de direção** e **grande volume de servidores em funções de assessoria**, 
que compõem a espinha administrativa da Prefeitura.
""")

df_com_gastos = df[df["categoria_cargo"] == "comissionado"].copy()

df_com_gastos["proventos"] = pd.to_numeric(df_com_gastos["proventos"], errors="coerce")

df_com_gastos = df_com_gastos.dropna(subset=["proventos"])

gasto_anual_comissionados = df_com_gastos["proventos"].sum()

gasto_anual_comissionados_str = br_money(gasto_anual_comissionados)

st.markdown("""
### Quanto custam os cargos comissionados?

Ao longo de 2025, a Prefeitura investiu **R\$ 4.008.750,36** no pagamento de salários, 
benefícios e encargos vinculados aos cargos comissionados. Esse valor considera todos os tipos de pagamento realizados no ano — 
incluindo salário base mensal, gratificações, férias, 13º salário e eventuais rescisões.

O montante evidencia o peso financeiro dessa estrutura dentro da folha municipal. 
Embora os cargos de direção concentrem as maiores remunerações individuais, é o conjunto formado por assessores e 
equipes de apoio que representa a parcela mais significativa do gasto total, devido ao número maior de servidores nessas funções.
""")

st.markdown(f"""
<div style='text-align:center;'>
    <div class="kpi-card">
        <div class="kpi-title">Gasto anual com Cargos Comissionados</div>
        <p class="kpi-value">{gasto_anual_comissionados_str}</p>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# CARGA HORÁRIA DOS COMISSIONADOS (2025)
# ============================================
df_com_unico = (
    df[df["categoria_cargo"] == "comissionado"]
    .drop_duplicates(subset="id_servidor")
    .copy()
)

df_com_unico["carga_horaria_semanal"] = pd.to_numeric(
    df_com_unico["carga_horaria_semanal"],
    errors="coerce"
)

df_ch = df_com_unico.dropna(subset=["carga_horaria_semanal"]).copy()

# metricas
carga_min = int(df_ch["carga_horaria_semanal"].min())
carga_max = int(df_ch["carga_horaria_semanal"].max())

# moda
carga_moda = int(df_ch["carga_horaria_semanal"].mode().iloc[0])

# quantos servidores têm essa carga predominante
qtd_moda = int((df_ch["carga_horaria_semanal"] == carga_moda).sum())
total_com = int(df_ch["id_servidor"].nunique())

# strings de exibicao
carga_moda_str = f"{carga_moda}h/sem"
carga_min_str = f"{carga_min}h/sem"
carga_max_str = f"{carga_max}h/sem"
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("### Carga horária semanal dos cargos comissionados")
st.markdown("<br>", unsafe_allow_html=True)

card_style = """
<div class="kpi-card" style="
    height: 160px;
    display: flex;
    flex-direction: column;
    justify-content: center;
">
    {content}
</div>
"""

c1, c2, c3 = st.columns(3, gap="large")

with c1:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-title">Carga horária predominante</div>
      <p class="kpi-value">{carga_moda_str}</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-title">Menor carga registrada</div>
      <p class="kpi-value">{carga_min_str}</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-title">Maior carga registrada</div>
      <p class="kpi-value">{carga_max_str}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
### O que revela a carga horária dos cargos comissionados

A análise da carga horária semanal dos cargos comissionados mostra um padrão bem definido dentro da Prefeitura. 
A grande maioria dos servidores desse grupo cumpre **40 horas semanais**, que aparece como a carga 
horária predominante e também como o limite máximo registrado.

O menor valor encontrado foi de **30 horas semanais**, 
observado em poucos cargos específicos. Isso indica que a estrutura comissionada opera, em sua maior parte, 
em regime de jornada completa, reforçando o caráter de funções de direção, 
coordenação e assessoramento que exigem dedicação integral.

Apesar da variação pontual, o quadro geral revela uma distribuição bastante homogênea da carga horária entre os comissionados.
""")

st.divider()
