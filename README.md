# LumeQuery — AI-Powered Data Intelligence Platform

**Transformando perguntas em linguagem natural em análises de negócio com SQL, Python e Inteligência Artificial.**

O **LumeQuery** é uma plataforma de inteligência de dados desenvolvida para explorar a integração entre análise de dados, bancos relacionais e agentes de Inteligência Artificial.

A solução permite consultar dados de um marketplace fictício utilizando linguagem natural. A partir de uma pergunta, agentes de IA geram e validam consultas SQL, executam análises no PostgreSQL e transformam os resultados em insights compreensíveis.

Desenvolvido como projeto independente de portfólio, o LumeQuery demonstra a aplicação prática de tecnologias de dados, IA e automação em uma solução integrada.

---

## Objetivo do projeto

Reduzir a barreira técnica entre usuários e dados, permitindo explorar informações de negócio sem a necessidade de escrever consultas SQL manualmente.

O projeto busca demonstrar como agentes de IA podem atuar em conjunto com ferramentas tradicionais de análise de dados para facilitar consultas, interpretação de resultados e apoio à tomada de decisões.

## Funcionalidades

- **Natural Language to SQL:** conversão de perguntas em linguagem natural em consultas SQL.
- **SQL Validation:** validação das consultas geradas antes da execução.
- **Business Intelligence:** exploração de indicadores e informações operacionais.
- **AI-Powered Insights:** interpretação dos resultados e geração de insights em linguagem natural.
- **Multilingual Interaction:** respostas no idioma identificado na pergunta.
- **Interactive Interface:** interação por meio de uma aplicação Streamlit.
- **REST API:** disponibilização das funcionalidades através de endpoints FastAPI.
- **Workflow Automation:** integração com n8n para automatizar o fluxo de consultas.

## Como funciona

O LumeQuery utiliza uma arquitetura multiagente em que cada componente possui uma responsabilidade específica.

1. O usuário envia uma pergunta em linguagem natural.
2. O **SQL Agent** interpreta a solicitação e gera uma consulta SQL.
3. A camada de validação verifica se a consulta respeita as regras de segurança.
4. O PostgreSQL executa a consulta sobre as views analíticas autorizadas.
5. O **Insights Agent** interpreta os resultados e produz uma resposta em linguagem natural.
6. O **Orchestrator** coordena o fluxo entre os agentes e retorna o resultado à aplicação.

## Arquitetura

<text weight="medium" color="secondary" size="sm">Fluxo geral da aplicação</text>

```text
                USER QUESTION
                      |
                      v
              STREAMLIT / API
                      |
                      v
                 ORCHESTRATOR
                      |
                      v
                  SQL AGENT
                      |
                      v
                SQL VALIDATION
                      |
                      v
                 POSTGRESQL
                ANALYTICS VIEWS
                      |
                      v
                INSIGHTS AGENT
                      |
                      v
              BUSINESS INSIGHTS
```

A integração com n8n permite utilizar a API em workflows automatizados.

A arquitetura técnica detalhada está documentada em [`docs/architecture.md`](docs/architecture.md).

## Tecnologias

| Tecnologia | Aplicação |
|---|---|
| Python | Desenvolvimento da aplicação e lógica dos agentes |
| PostgreSQL | Armazenamento e consultas analíticas |
| SQL | Modelagem e exploração dos dados |
| Pandas | Processamento e análise de dados |
| Google Gemini API | Geração de SQL e insights com IA |
| SQLGlot | Parsing e validação de consultas SQL |
| Streamlit | Interface interativa |
| FastAPI | API REST |
| n8n | Automação de workflows |
| Docker | Execução do ambiente de automação |
| Pytest | Testes automatizados |

## Base de dados

O projeto utiliza um cenário fictício de marketplace e delivery, com dados sintéticos que representam operações de clientes, restaurantes, pedidos, entregas e pagamentos.

O banco PostgreSQL está organizado em dois schemas:

- `raw`: armazenamento dos dados operacionais.
- `analytics`: views estruturadas para consultas e análises.

**Volume de dados:**

| Entidade | Registros |
|---|---:|
| Regions | 10 |
| Customers | 5.000 |
| Restaurants | 100 |
| Menu items | 500 |
| Couriers | 150 |
| Orders | 20.000 |
| Order items | 49.570 |
| Deliveries | 19.002 |
| Payments | 20.000 |

As principais views analíticas são:

- `analytics.vw_order_summary`
- `analytics.vw_daily_performance`
- `analytics.vw_restaurant_performance`

Mais detalhes sobre tabelas, relacionamentos e views: [`docs/data_model.md`](docs/data_model.md).

## Segurança das consultas

Como as consultas SQL são geradas por Inteligência Artificial, o projeto implementa mecanismos de validação antes da execução.

Entre as proteções implementadas:

- Aceitação exclusiva de consultas `SELECT`.
- Restrição às views analíticas autorizadas.
- Bloqueio de operações de alteração de dados.
- Rejeição de consultas múltiplas.
- Limite máximo de 100 registros.
- Execução em transação somente leitura.
- Timeout de execução SQL de 5 segundos.

Esses mecanismos adicionam uma camada de controle entre os agentes de IA e o banco de dados.

## Organização do projeto

| Diretório / arquivo | Responsabilidade |
|---|---|
| `src/` | Lógica da aplicação, processamento e agentes de IA |
| `sql/` | Scripts de criação, views e validação do banco |
| `docs/` | Documentação técnica |
| `tests/` | Testes automatizados |
| `data/` | Arquivos gerados durante as análises |
| `app.py` | Interface Streamlit |
| `api.py` | API FastAPI |
| `docker-compose.yml` | Configuração do ambiente n8n |
| `requirements.txt` | Dependências Python |

## Executando o projeto

### Pré-requisitos

- Python 3.12
- PostgreSQL
- Docker Desktop
- Chave de API do Google Gemini

### 1. Clonar o repositório

```bash
git clone https://github.com/lucyteff/lumequery.git
cd lumequery
```

### 2. Criar o ambiente virtual

```bash
python -m venv .venv
```

No Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar as variáveis de ambiente

Criar um arquivo `.env` na raiz do projeto:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lumequery
DB_USER=postgres
DB_PASSWORD=sua_senha

GEMINI_API_KEY=sua_chave
GEMINI_MODEL=seu_modelo
```

Utilize suas próprias credenciais locais. O arquivo `.env` não deve ser enviado ao GitHub.

### 5. Preparar o banco de dados

Criar o banco PostgreSQL e executar os scripts SQL na seguinte ordem:

1. `sql/01_create_tables.sql`
2. `sql/02_create_analytics_views.sql`
3. `sql/03_validate_data.sql`

Depois, gerar os dados sintéticos utilizando os módulos disponíveis em `src/`.

### 6. Iniciar a interface

```bash
streamlit run app.py
```

### 7. Iniciar a API

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

Documentação interativa:

`http://localhost:8000/docs`

### 8. Iniciar o n8n

```bash
docker compose up -d
```

Interface local:

`http://localhost:5678`

A API precisa estar em execução para que o workflow consiga processar as perguntas.

## API

A aplicação disponibiliza os seguintes endpoints:

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/health` | Verificação de disponibilidade |
| POST | `/ask` | Processamento de perguntas em linguagem natural |

Exemplo de requisição:

```json
{
  "question": "Qual foi a taxa de cancelamento?"
}
```

A resposta contém a pergunta original, o SQL executado, a quantidade de registros retornados e os insights gerados.

## Testes

Para executar a suíte automatizada:

```bash
python -m pytest -v
```

Os testes contemplam validações da API e mecanismos de segurança das consultas SQL.


## Documentação técnica

- [Arquitetura do sistema](docs/architecture.md)
- [Modelo de dados](docs/data_model.md)
- [Funcionamento dos agentes](docs/ai_agents.md)
- [Integração com n8n](docs/n8n_integration.md)

## Autora

**Luciana Estefanía Pécora**

- GitHub: [@lucyteff](https://github.com/lucyteff)
- LinkedIn: [Perfil profissional](https://www.linkedin.com/in/luciana-estefania-pecora/)