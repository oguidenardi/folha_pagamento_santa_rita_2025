# 📊 Análise de Dados do Portal da Transparência Municipal

Este repositório reúne um projeto de **análise de dados públicos** a partir de informações disponibilizadas no **Portal da Transparência de uma prefeitura municipal**, com foco em servidores públicos, cargos, remunerações e vínculos.

O objetivo principal é transformar dados brutos em **informações compreensíveis, analisáveis e acessíveis**, tanto para a **população em geral** quanto para **profissionais da área de dados**.

---

## 🎯 Objetivos do Projeto

- Analisar dados de servidores públicos municipais
- Entender a distribuição de cargos, categorias e regimes
- Explorar informações salariais (proventos, descontos e valores líquidos)
- Produzir análises transparentes e reprodutíveis
- Preparar a base para visualizações e comunicação pública dos dados

---

## 🧠 Metodologia

O projeto segue a metodologia **CRISP-DM**, amplamente utilizada em projetos de Ciência de Dados:

1. Business Understanding  
2. Data Understanding  
3. Data Preparation  
4. Exploratory Data Analysis (EDA) *(em andamento)*  
5. Modeling *(futuro)*  
6. Deployment *(visualização pública)*  

---

## 📂 Estrutura do Repositório

```text
data/
├── raw/        # Dados brutos, conforme disponibilizados pela fonte oficial
├── interim/    # Arquivos intermediários usados durante tratamentos
├── processed/  # Base final tratada para análise (não versionada)

notebooks/
├── 01_business_understanding.ipynb
├── 02_data_understanding.ipynb
├── 03_data_preparation.ipynb
├── 04_exploratory_data_analysis.ipynb (em construção)
