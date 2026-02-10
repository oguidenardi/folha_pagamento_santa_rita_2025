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
# Os maiores salários de 2025

Um levantamento realizado a partir dos dados oficiais de **folha mensal da Prefeitura** revela quais são 
os **10 maiores salários pagos ao longo de 2025**. A lista, composta por diferentes áreas da administração, 
mostra um cenário marcado sobretudo pela presença da **Saúde**, do **Jurídico** e do **alto escalão do Executivo**.

O topo do ranking é dominado pela área da **Saúde**, com três cargos de **Médico PSF** ocupando as três primeiras 
colocações — dois profissionais do gênero masculino e uma profissional do gênero feminino. 
Logo depois, na **4ª posição**, aparece o cargo de **Procurador Geral do Município**, exercido por uma servidora mulher.

Na sequência, a **5ª posição** é ocupada pelo **Prefeito**, único cargo eletivo da lista. 
O setor jurídico volta a aparecer na **6ª colocação**, com o cargo de **Procurador Jurídico**, desempenhado por um servidor homem.

O ranking também inclui duas posições de **Agente Administrativo**, nos **7º e 9º lugares**, 
exercidas por uma mulher e um homem, respectivamente — mostrando que, embora seja uma função administrativa, 
há casos em que o salário alcança valores elevados dentro da estrutura municipal.

Já a **8ª posição** é ocupada por um **Médico** (fora da categoria PSF), reforçando novamente o peso 
da área da Saúde entre as maiores remunerações. O grupo se encerra com o cargo de **Veterinário**, que ocupa o **10º lugar**, 
também desempenhado por um servidor homem.

""")
st.markdown("<br> <br>", unsafe_allow_html=True)

df_mensal = df[df["tipo_pagamento"] == "folha_mensal"].copy()

df_mensal_unico = df_mensal.drop_duplicates(
    subset=["id_servidor", "cargo"],
    keep="last"
)

top_10_salarios_geral = (
    df_mensal_unico.groupby(["id_servidor", "cargo", "genero"])["proventos"]
    .max()
    .reset_index(name="salario_maximo")
    .sort_values("salario_maximo", ascending=False)
    .head(10)
    .reset_index(drop=True)
)

top_10_salarios_geral["salario_str"] = top_10_salarios_geral["salario_maximo"].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

top_10_salarios_geral = top_10_salarios_geral.copy()
top_10_salarios_geral["salario_maximo"] = pd.to_numeric(top_10_salarios_geral["salario_maximo"], errors="coerce")
top_10_salarios_geral = top_10_salarios_geral.dropna(subset=["salario_maximo"]).reset_index(drop=True)


top_10_salarios_geral["rank"] = (top_10_salarios_geral.index + 1).astype(int)
top_10_salarios_geral["rank_label"] = top_10_salarios_geral["rank"].astype(str) + "º"

max_sal = float(top_10_salarios_geral["salario_maximo"].max())

base = alt.Chart(top_10_salarios_geral).encode(
    y=alt.Y(
        "rank_label:N",
        sort=alt.SortField(field="rank", order="ascending"),
        title=None,
        axis=alt.Axis(labelAngle=0)
    ),
    x=alt.X(
        "salario_maximo:Q",
        title="Salário base (R$)",
        scale=alt.Scale(domain=[0, max_sal * 1.12])  # folga para rótulos
    ),
    tooltip=[
        alt.Tooltip("rank:Q", title="Rank"),
        alt.Tooltip("cargo:N", title="Cargo (completo)"),
        alt.Tooltip("genero:N", title="Gênero"),
        alt.Tooltip("salario_str:N", title="Salário Máximo"),
        alt.Tooltip("id_servidor:N", title="ID (anon.)"),
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
        text="10 maiores salários da Prefeitura em 2025",
        anchor="middle",
        fontSize=16,
        fontWeight="bold",
        offset=12
    )
)

st.altair_chart(chart, use_container_width=True)



#------------------------------------
# Top 10 salários homens
#------------------------------------

st.markdown("""
## Os 10 maiores salários por gênero

### 10 maiores salários gênero masculino

Os dados da folha mensal de 2025 mostram que os maiores salários entre servidores homens estão concentrados principalmente na **Saúde**, no **Executivo** e no **Jurídico**.

No topo do ranking aparecem dois **Médicos do PSF**, que ocupam a **1ª e 2ª posições**, seguidos pelo **Prefeito** na **3ª colocação** — único cargo eletivo da lista.

A **4ª posição** é do **Procurador Jurídico**, responsável pela representação legal do município. Em **5º lugar**, surge mais um **Médico**, fora da estrutura do PSF.

O cargo de **Agente Administrativo** aparece duas vezes, nas **6ª e 9ª posições**, mostrando que, em alguns casos, funções administrativas também alcançam remunerações elevadas.

Em **7º lugar**, está o **Veterinário**, evidenciando o peso de áreas técnicas especializadas. Já a **8ª posição** fica com o **Médico de Pronto Atendimento**, essencial nos serviços de urgência.

O ranking se encerra com outro **Médico** na **10ª posição**, reforçando que a Saúde domina a maior parte das remunerações mais altas entre servidores do gênero masculino em 2025.

""")
st.markdown("<br>", unsafe_allow_html=True)

# Filtrar folha mensal + genero
df_mensal_masc = df[
    (df["tipo_pagamento"] == "folha_mensal") &
    (df["genero"] == "M")
].copy()

# Remover duplicações do mesmo servidor/cargo
df_mensal_masc_unico = df_mensal_masc.drop_duplicates(
    subset=["id_servidor", "cargo"],
    keep="last"
)

# Calculando maior salário mensal por servidor
top_10_salarios_masc = (
    df_mensal_masc_unico
    .groupby(["id_servidor", "cargo"])["proventos"]
    .max()
    .reset_index(name="salario_maximo")
    .sort_values("salario_maximo", ascending=False)
    .head(10)
    .reset_index(drop=True)
)

# Criando coluna com salário formatado (BRL)
top_10_salarios_masc["salario_str"] = top_10_salarios_masc["salario_maximo"].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

# Adicionando ranking numérico
top_10_salarios_masc["rank"] = top_10_salarios_masc.index + 1
top_10_salarios_masc["rank_label"] = top_10_salarios_masc["rank"].astype(str) + "º"

# Sanitização rápida para evitar "undefined"
df_plot = top_10_salarios_masc.copy()
df_plot["salario_maximo"] = pd.to_numeric(df_plot["salario_maximo"], errors="coerce")
df_plot = df_plot.dropna(subset=["salario_maximo"]).reset_index(drop=True)

# Garante rank (caso ainda não tenha)
if "rank" not in df_plot.columns:
    df_plot["rank"] = (df_plot.index + 1).astype(int)
if "rank_label" not in df_plot.columns:
    df_plot["rank_label"] = df_plot["rank"].astype(str) + "º"

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
        title="Salário base (R$)",
        scale=alt.Scale(domain=[0, max_sal * 1.12])
    ),
    tooltip=[
        alt.Tooltip("rank:Q", title="Rank"),
        alt.Tooltip("cargo:N", title="Cargo (completo)"),
        alt.Tooltip("salario_str:N", title="Salário Máximo"),
        alt.Tooltip("id_servidor:N", title="ID (anon.)") if "id_servidor" in df_plot.columns else alt.value(None),
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
        text="10 maiores salários da Prefeitura em 2025 - Gênero Masculino",
        anchor="middle",
        fontSize=16,
        fontWeight="bold",
        offset=12

    )
)

st.altair_chart(chart, use_container_width=True)

# Legenda editorial
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
st.markdown("**Cargos (por ordem do ranking):**")

for _, row in df_plot.iterrows():
    st.caption(f"**{int(row['rank'])}º** — {row['cargo']}")


# ----------------------------
# Top 10 salários feminino
# ----------------------------
st.markdown("""
### 10 maiores salários gênero feminino

Os dados da folha mensal de 2025 mostram que os maiores salários entre servidoras estão 
concentrados principalmente na **Saúde**, no **Jurídico** e na **Educação**.

A **1ª posição** é ocupada por uma **Médica do PSF**, seguida na **2ª colocação** pela **Procuradora Geral do Município**, 
o mais alto cargo jurídico da administração.

O **3º lugar** fica com uma **Agente Administrativa**, indicando que funções de apoio também alcançam salários relevantes.

Da **4ª à 9ª posição**, o ranking é dominado pelo cargo de **Professora**, reforçando a forte presença feminina na Educação e
a importância da categoria dentro do funcionalismo.

Fechando a lista, na **10ª posição**, aparece uma **Médica Pediatra**, destacando novamente a área da Saúde entre as maiores remunerações femininas de 2025.

""")
st.markdown("<br>", unsafe_allow_html=True)

# Filtrar folha mensal e gênero
df_mensal_fem = df[
    (df["tipo_pagamento"] == "folha_mensal") &
    (df["genero"] == "F")
].copy()

# Remover duplicações do mesmo servidor/cargo
df_mensal_fem_unico = df_mensal_fem.drop_duplicates(
    subset=["id_servidor", "cargo"],
    keep="last"
)

# Calculando maior salário mensal por servidor
top_10_salarios_fem = (
    df_mensal_fem_unico
    .groupby(["id_servidor", "cargo"])["proventos"]
    .max()
    .reset_index(name="salario_maximo")
    .sort_values("salario_maximo", ascending=False)
    .head(10)
    .reset_index(drop=True)
)

# Criando coluna com salário formatado (BRL)
top_10_salarios_fem["salario_str"] = top_10_salarios_fem["salario_maximo"].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

# Adicionando ranking numérico
top_10_salarios_fem["rank"] = top_10_salarios_fem.index + 1
top_10_salarios_fem["rank_label"] = top_10_salarios_fem["rank"].astype(str) + "º"

# Sanitização rápida para evitar undefined
df_plot_fem = top_10_salarios_fem.copy()
df_plot_fem["salario_maximo"] = pd.to_numeric(df_plot["salario_maximo"], errors="coerce")
df_plot_fem = df_plot_fem.dropna(subset=["salario_maximo"]).reset_index(drop=True)

# Garante rank (caso ainda não tenha)
if "rank" not in df_plot_fem.columns:
    df_plot["rank"] = (df_plot_fem.index + 1).astype(int)
if "rank_label" not in df_plot_fem.columns:
    df_plot["rank_label"] = df_plot_fem["rank"].astype(str) + "º"

max_sal = float(df_plot_fem["salario_maximo"].max())

base = alt.Chart(df_plot_fem).encode(
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
        alt.Tooltip("id_servidor:N", title="ID (anon.)") if "id_servidor" in df_plot.columns else alt.value(None),
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
        text="10 maiores salários da Prefeitura em 2025 - Gênero Feminino",
        anchor="middle",
        fontSize=16,
        fontWeight="bold",
        offset=12

    )
)

st.altair_chart(chart, use_container_width=True)

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
st.markdown("**Cargos (por ordem do ranking):**")

for _, row in df_plot_fem.iterrows():
    st.caption(f"**{int(row['rank'])}º** — {row['cargo']}")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
#### Conclusão:
A análise dos maiores salários pagos pela Prefeitura em 2025 mostra um padrão claro na estrutura de remunerações do município. 
A **área da Saúde** concentra boa parte dos valores mais altos, com diferentes especialidades médicas presentes tanto no ranking geral quanto 
nas listas específicas de homens e mulheres. O **Jurídico** e o **Executivo** também aparecem como setores de destaque, 
refletindo a relevância institucional desses cargos.

Entre os homens, a Saúde domina as primeiras posições, seguida por funções de comando e atuação jurídica. 
Já entre as mulheres, os maiores salários se distribuem entre a Saúde, o Jurídico e principalmente a **Educação**, 
onde o cargo de Professora aparece de forma recorrente.

No ranking geral, a presença masculina é maior, mas os dados mostram que **as servidoras também ocupam posições estratégicas e 
de alta responsabilidade**, como Procuradora Geral e Médica PSF. 

Em resumo, os maiores salários de 2025 refletem áreas essenciais para o funcionamento da administração pública — 
Saúde, Educação, Jurídico e Executivo — evidenciando como cada uma delas contribui para a manutenção dos serviços prestados à população.
""")
st.divider()