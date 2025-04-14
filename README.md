# Breweries Data Engineering Pipeline

Este projeto implementa um pipeline de dados que extrai dados da API OpenBreweryDB, transforma-os e os carrega em um data lake seguindo a arquitetura medallion.

## Arquitetura

O pipeline segue a arquitetura medallion com três camadas:

1. **Camada Bronze**: Dados brutos da API OpenBreweryDB armazenados em formato JSON
2. **Camada Silver**: Dados transformados em formato Parquet, particionados por localização (estado)
3. **Camada Gold**: Dados agregados mostrando a contagem de cervejarias por tipo e localização

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal
- **Apache Airflow**: Orquestração de workflows
- **Docker**: Containerização
- **Pandas/PyArrow**: Transformação de dados
- **Great Expectations**: Validação de qualidade de dados
- **Prometheus & Grafana**: Monitoramento (descrito na documentação)

## Estrutura do Projeto

\`\`\`
breweries-pipeline/
├── airflow/
│   ├── dags/
│   │   └── breweries_pipeline.py
│   └── Dockerfile
├── src/
│   ├── extractors/
│   │   └── brewery_api.py
│   ├── transformers/
│   │   ├── bronze_to_silver.py
│   │   └── silver_to_gold.py
│   ├── utils/
│   │   ├── config.py
│   │   └── logging_utils.py
│   └── tests/
│       ├── test_extractors.py
│       └── test_transformers.py
├── docker-compose.yml
├── requirements.txt
└── README.md
\`\`\`

## Plano de Inicialização do Projeto

### Pré-requisitos

Antes de iniciar, certifique-se de ter instalado:

- Docker (versão 20.10.0 ou superior)
- Docker Compose (versão 2.0.0 ou superior)
- Git

Você pode verificar as versões instaladas com os seguintes comandos:

\`\`\`bash
docker --version
docker-compose --version
git --version
\`\`\`

### Passo 1: Clonar o Repositório

\`\`\`bash
git clone https://github.com/seu-usuario/breweries-pipeline.git
cd breweries-pipeline
\`\`\`

### Passo 2: Configurar o Ambiente

Crie as pastas necessárias para o data lake:

\`\`\`bash
mkdir -p data/bronze data/silver data/gold logs
\`\`\`

### Passo 3: Iniciar os Containers Docker

\`\`\`bash
docker-compose up -d
\`\`\`

Este comando irá:
1. Baixar as imagens necessárias
2. Criar os containers
3. Inicializar o banco de dados do Airflow
4. Iniciar o webserver e o scheduler do Airflow

### Passo 4: Verificar a Instalação

1. Acesse a interface web do Airflow em http://localhost:8080
   - Usuário: airflow
   - Senha: airflow

2. Verifique se o DAG "breweries_pipeline" está listado na interface

3. Verifique os logs para garantir que não há erros:
   \`\`\`bash
   docker-compose logs -f
   \`\`\`

### Passo 5: Executar o Pipeline

1. Na interface do Airflow, ative o DAG "breweries_pipeline" clicando no botão de toggle
2. Clique no botão "Trigger DAG" para executar o pipeline manualmente

### Passo 6: Verificar os Resultados

Após a execução bem-sucedida do pipeline, você pode verificar os dados gerados:

\`\`\`bash
# Listar arquivos na camada bronze
ls -la data/bronze/breweries/

# Listar arquivos na camada silver
ls -la data/silver/breweries/

# Listar arquivos na camada gold
ls -la data/gold/breweries_by_type_location/
\`\`\`

### Solução de Problemas Comuns

#### Erro de Permissão nos Volumes

Se encontrar erros de permissão ao acessar os volumes, execute:

\`\`\`bash
sudo chown -R $(id -u):$(id -g) ./data ./logs
\`\`\`

#### Erro de Inicialização do Banco de Dados

Se o Airflow não inicializar corretamente, tente reiniciar os containers:

\`\`\`bash
docker-compose down
docker-compose up -d
\`\`\`

#### Erro de Fernet Key

Se encontrar erros relacionados à Fernet Key, verifique se a chave está configurada corretamente no arquivo docker-compose.yml.

## Monitoramento e Alertas

O pipeline inclui:

1. **Monitoramento de Qualidade de Dados**: Usando Great Expectations para validar dados em cada estágio
2. **Monitoramento de Pipeline**: Monitoramento integrado do Airflow para sucesso/falha de tarefas
3. **Alertas**: Notificações por e-mail para falhas de pipeline e problemas de qualidade de dados

## Escolhas de Design e Trade-offs

### Ferramenta de Orquestração
Escolhi o Airflow por sua robusta programação, mecanismos de retry e extensa biblioteca de operadores. O trade-off é o aumento da complexidade em comparação com ferramentas mais simples como Luigi.

### Formato de Armazenamento
Parquet foi selecionado para as camadas silver e gold devido à sua natureza colunar, capacidades de compressão e aplicação de schema. O trade-off é um processamento ligeiramente mais complexo em comparação com CSV.

### Estratégia de Particionamento
Os dados são particionados por estado na camada silver para otimizar consultas que filtram por localização. O trade-off é o aumento da sobrecarga de armazenamento para estados pequenos.

### Containerização
Docker fornece consistência entre ambientes e simplifica a implantação. O trade-off é a curva de aprendizado e a sobrecarga de recursos.

## Melhorias Futuras

1. Implementar carregamento incremental para lidar com volumes crescentes de dados
2. Adicionar verificações de qualidade de dados mais abrangentes
3. Implementar um pipeline de CI/CD para testes e implantação automatizados
4. Adicionar um catálogo de dados para gerenciamento de metadados
5. Implementar um sistema de rastreamento de linhagem de dados
