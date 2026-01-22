# Diretório de Dados (`data/`)

Este diretório contém a organização completa dos dados utilizados no projeto,
seguindo **boas práticas de Ciência de Dados** e a metodologia **CRISP-DM**.

O objetivo é garantir **transparência**, **reprodutibilidade** e **clareza**
tanto para o público em geral quanto para profissionais da área de dados que
estejam avaliando o projeto.

## Estrutura de Pastas

data/
├── raw/
├── interim/
└── processed/


### `raw/` — Dados Brutos
Contém os dados exatamente como foram obtidos da fonte original
(Portal da Transparência).

- Nenhuma modificação ou tratamento é aplicado
- Preserva a integridade da fonte original
- Permite auditoria e rastreabilidade dos dados
- Serve como ponto de partida para todo o pipeline analítico

> Boas práticas: dados brutos nunca devem ser alterados manualmente.

### `interim/` — Dados Intermediários
Armazena arquivos temporários gerados durante a preparação dos dados.

- Utilizado para inspeções, validações e tratamentos pontuais
- Pode conter CSVs auxiliares criados durante a exploração dos dados
- Facilita o debug e a verificação de etapas específicas do processo

Esses arquivos **não representam o dataset final**, apenas etapas do caminho
até ele.

### `processed/` — Dados Tratados (Prontos para Análise)
Contém os dados finais, já tratados e estruturados para análise.

- Dados limpos, padronizados e consistentes
- Gerados automaticamente a partir dos notebooks
- Prontos para análises exploratórias, visualizações e aplicações
  (ex: dashboards)

> Este diretório não é versionado no repositório, pois os arquivos podem ser
reproduzidos a qualquer momento executando o pipeline do projeto.

## Metodologia

A organização dos dados segue o framework **CRISP-DM**, especialmente nas fases:

- Data Understanding  
- Data Preparation  

Todo o processo de tratamento, decisões técnicas e validações está documentado
nos notebooks localizados no diretório `notebooks/`, com destaque para:

- `03_data_preparation`

## Reprodutibilidade

Este projeto prioriza **reprodutibilidade em vez de armazenamento de artefatos**.

Qualquer pessoa pode:
1. Acessar os dados brutos em `raw/`
2. Executar os notebooks do projeto
3. Recriar os dados finais em `processed/`

Essa abordagem é amplamente utilizada em projetos profissionais de dados e
ambientes de produção.

## Público-Alvo

Este projeto foi desenvolvido para:
- Facilitar o entendimento dos dados pela população
- Demonstrar habilidades práticas em Ciência de Dados
- Servir como portfólio técnico para recrutadores e profissionais da área

A clareza na organização dos dados reflete a preocupação com:
- Qualidade analítica
- Governança de dados
- Boas práticas de engenharia analítica

---
