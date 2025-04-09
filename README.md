## Introdução

Este repositório contém a solução para o case de expansão estratégica de uma rede de laboratórios diagnósticos. O projeto integra a análise exploratória dos dados (EDA) e o desenvolvimento de uma pipeline automatizada que processa e analisa dados demográficos, econômicos, transacionais e referentes aos exames realizados, com o objetivo final de recomendar três ZCTAs ideais para a instalação de novos laboratórios.

## Estrutura do Projeto

```
├── README.md                      # Este arquivo de documentação
├── requirements.txt               # Lista de dependências do projeto
├── notebooks/                     # Notebooks Jupyter utilizados na análise
│   ├── README.md                  # Documentação interna dos notebooks
│   ├── analytics/                 # Notebooks de análises e validação de hipóteses
│   │   ├── hypothesis/            # Análises detalhadas das hipóteses de negócio
│   │   │   ├── README.md          # Descrição e justificativas das hipóteses
│   │   │   ├── age.ipynb          # Análise da hipótese sobre idade dos pacientes
│   │   │   ├── density.ipynb      # Análise de saturação de mercado por quantidade de laboratórios
│   │   │   ├── gender.ipynb       # Análise de impacto da proporção de gênero
│   │   │   ├── income.ipynb       # Análise da relação entre renda e desempenho financeiro
│   │   │   └── population.ipynb   # Análise do impacto da população (ZCTA)
│   │   └── results/               # Consolidação e sumarização dos resultados obtidos
│   │       ├── README.md          # Sumário dos resultados e critérios de seleção
│   │       └── consolidated.ipynb # Consolidação dos insights para resposta à pergunta inicial
│   └── pre_processing/            # Notebooks para pré-processamento e limpeza dos dados
│       ├── demographic.ipynb      # Limpeza e transformação dos dados demográficos
│       ├── economic.ipynb         # Tratamento dos dados econômicos
│       ├── exams.ipynb            # Preparo dos dados dos exames
│       ├── geocode.ipynb          # Processamento dos dados de geolocalização dos laboratórios
│       └── transactional.ipynb    # Pré-processamento dos dados transacionais
└── pipe/                          # Pipeline automatizada da solução
    ├── main.py                    # Script principal para orquestração das etapas do pipeline
    ├── preprocess/                # Módulo responsável pelo pré-processamento
    │   ├── main.py                # Execução paralela do pré-processamento de cada dataset
    │   └── utils.py               # Funções utilitárias para limpeza, normalização e tratamento dos dados
    └── select/                    # Módulo responsável pela seleção dos ZCTAs para expansão
        ├── main.py                # Módulo para o cálculo do indicador de expansão e seleção dos três melhores ZCTAs
        └── utils.py               # Funções utilitárias para o cálculo
```

## Requisitos e Configuração do Ambiente

Antes de executar o projeto, certifique-se de ter o Python (preferencialmente Python 3.7 ou superior) instalado em seu sistema.

### 1. Criação do Ambiente Virtual

Abra o terminal (ou prompt de comando) na raiz do projeto e execute:

```bash
# Cria o ambiente virtual
python3 -m venv venv

# Ativa o ambiente virtual (Linux/Mac)
source venv/bin/activate

# Ou no Windows:
venv\Scripts\activate
```

### 2. Instalação das Dependências

Com o ambiente virtual ativado, instale as dependências listadas no arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Importação de Data sets

Todos os data sets devem ser importados para a pasta `data/raw` antes de executar os notebooks ou a pipeline.


## Execução e Leitura dos Notebooks

A pasta `notebooks/` contém todos os Jupyter Notebooks necessários para:
- Pré-processamento dos dados (limpeza, transformação e validação);
- Análises exploratórias com teste de hipóteses e geração de gráficos/insights;
- Consolidação dos resultados para resposta à pergunta inicial do case.

Para abrir e executar os notebooks, utilize:

```bash
jupyter notebook
```

Navegue até a pasta desejada e execute cada notebook conforme a ordem lógica descrita:
1. [Executar os notebooks de pré-processamento em `notebooks/pre_processing`](notebooks/pre_processing)
2. [Ler a Análise Prévia de Negócio em `hypothesis/README.md`](notebooks/analytics/hypothesis/README.md)
3. [Analisar os notebooks de hipóteses em `analytics/hypothesis/`](notebooks/analytics/hypothesis/)
4. [Ler a Sumarização dos Resultados em `results/README.md`](notebooks/analytics/results/README.md)
5. [Verificar a consolidação dos resultados em `/results/consolidated.ipynb`](notebooks/analytics/results/consolidated.ipynb)


Cada pasta contém um README.md adicional com instruções específicas e descrição dos conteúdos.

## Execução da Pipeline Automatizada

A pasta `pipe/` contém os módulos para automatizar o tratamento dos dados e a seleção dos melhores ZCTAs para expansão.

### Passos para execução:

1. **Pré-processamento:**  
   Para rodar o pré-processamento de todos os datasets e gerar os arquivos limpos, execute:

   ```bash
   python -m pipe.main --preprocess
   ```

   Este comando lê os arquivos brutos da pasta `data/raw`, aplica as transformações necessárias e salva os arquivos processados na pasta configurada (por padrão, `data/processed_pipe`).

2. **Seleção dos ZCTAs:**  
   Para executar a etapa de seleção dos ZCTAs, utilize o seguinte comando:

   ```bash
   python -m pipe.main --select
   ```

   Este comando utiliza os dados processados para calcular o indicador de expansão e os filtros necessário, por fim imprime os três ZCTAs recomendados.

3. **Executar ambas as etapas:**  
   Se desejar executar as duas etapas de uma só vez, combine os argumentos:

   ```bash
   python -m pipe.main --preprocess --select
   ```

## Considerações Finais

- **Atualização dos Dados:**  
  A pipeline foi projetada para que, assim que novos dados sejam adicionados à pasta `data/raw`, seja possível reexecutar as análises automaticamente pela pipeline.

- **Logs e Depuração:**  
  Durante a execução dos scripts da pipeline, mensagens de log serão exibidas para informar o progresso e ajudar na identificação de problemas. Se ocorrer algum erro, verifique os logs para detalhes.

- **Customização:**  
  O projeto é modular. Caso sejam necessárias novas análises ou ajustes nas transformações, as funções estão distribuídas nos notebooks (para análise manual) e nos módulos da pasta `pipe/`.

- **Documentação Complementar:**  
  Consulte os READMEs internos nas pastas `notebooks/` para informações mais detalhadas sobre cada etapa e sobre a lógica de negócios aplicada.
