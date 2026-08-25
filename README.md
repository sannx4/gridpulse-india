# GridPulse India

**GridPulse India** is a production-oriented real-time Indian power-grid telemetry and analytics platform.

The project is being built incrementally from a single permitted grid-data source into a larger streaming platform supporting ingestion, time-series storage, APIs, realtime dashboards, anomaly detection, forecasting, cold-data storage, observability, and reliability engineering.

The project intentionally starts with a simple architecture and introduces distributed components only when they solve a demonstrated engineering problem.

---

## Project Status

Current development milestone:

**Day 9 — Resilient Source HTTP Client**

Completed:

* Monorepo bootstrap
* Python and TypeScript development environment
* Formatting, linting, testing and pre-commit hooks
* Docker Compose infrastructure
* PostgreSQL + TimescaleDB
* Dedicated database users
* Container health checks
* Persistent database volume
* Alembic database migrations
* Canonical telemetry schema
* Example frequency and demand telemetry
* Telemetry quality constraints
* Schema version validation
* Reusable source HTTP client
* Request IDs
* Configurable timeouts
* Retry handling
* Exponential backoff
* Structured HTTP exceptions
* Unit tests for timeout, HTTP 5xx and invalid content

Current architecture:

```text
External Grid Source
        │
        ▼
Source HTTP Client
        │
        ├── Timeout
        ├── Retry
        ├── Exponential Backoff
        ├── X-Request-ID
        └── Structured Errors
        │
        ▼
Source Adapter / Parser
        │
        ▼
Canonical Telemetry
        │
        ▼
PostgreSQL + TimescaleDB
```

The parser and live source-to-database integration are the next development stages.

---

## Long-Term Architecture

The planned platform evolves toward:

```text
              PUBLIC / PERMITTED DATA SOURCES

      GRID-INDIA      RLDCs      SLDCs      IMD
           │             │          │         │
           └─────────────┴──────────┴─────────┘
                         │
                         ▼
                   Source Adapters
                         │
                         ▼
                Kafka / Redpanda
                         │
               ┌─────────┴─────────┐
               │                   │
               ▼                   ▼
           Normalizer             DLQ
               │
               ▼
        Canonical Telemetry
               │
        ┌──────┴─────────┐
        │                │
        ▼                ▼
   TimescaleDB       Parquet / S3
        │
        ├─────────┬─────────────┐
        ▼         ▼             ▼
    Anomaly    Forecasting   Grid Analytics
     Engine       Engine
        │         │
        └────┬────┘
             ▼
           Redis
             │
      ┌──────┴──────┐
      ▼             ▼
   REST API      WebSocket
      │             │
      └──────┬──────┘
             ▼
        React + D3/visx
```

Operational components planned for later phases include:

```text
GitHub Actions
      ↓
Docker / Kubernetes
      ↓
Prometheus + Grafana
      ↓
Structured Logs / Traces
      ↓
SLOs + Alerts
      ↓
Load / Chaos / Restore Tests
```

---

# Repository Structure

```text
gridpulse-india/
│
├── apps/
│   └── web/
│
├── services/
│   ├── api/
│   └── ingestion/
│       ├── http/
│       │   ├── __init__.py
│       │   ├── client.py
│       │   └── exceptions.py
│       ├── __init__.py
│       └── main.py
│
├── packages/
│   └── shared/
│
├── infra/
│   └── postgres/
│       ├── init/
│       └── migrations/
│
├── tests/
│   └── unit/
│       └── ingestion/
│
├── docs/
│
├── .env.example
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
├── alembic.ini
├── compose.yaml
├── package.json
├── pyproject.toml
├── tsconfig.json
└── README.md
```

---

# Technology Stack

## Backend

* Python
* HTTPX
* SQLAlchemy
* Alembic
* PostgreSQL
* TimescaleDB

Planned:

* FastAPI
* WebSockets
* Redis
* Kafka / Redpanda

## Frontend

* TypeScript

Planned:

* React
* D3
* visx

## Infrastructure

* Docker
* Docker Compose
* Git
* GitHub
* Pre-commit

Planned:

* GitHub Actions
* Kubernetes / k3s
* Terraform
* Prometheus
* Grafana

## Testing and Code Quality

* pytest
* Ruff
* Black
* pre-commit

---

# Canonical Telemetry Model

GridPulse normalizes different source formats into one canonical telemetry representation.

The current telemetry model contains:

| Field            | Purpose                               |
| ---------------- | ------------------------------------- |
| `id`             | Internal database identifier          |
| `source`         | Originating data source               |
| `entity`         | Grid/geographical entity              |
| `metric`         | Measurement type                      |
| `value`          | Numeric measurement                   |
| `unit`           | Unit such as Hz or MW                 |
| `observed_at`    | Time the measurement was observed     |
| `ingested_at`    | Time GridPulse stored the measurement |
| `quality`        | Data-quality classification           |
| `schema_version` | Canonical-schema version              |

Example:

```text
source         = grid_india_fixture
entity         = all_india
metric         = grid_frequency
value          = 49.98
unit           = Hz
quality        = good
schema_version = 1
```

Another example:

```text
source         = grid_india_fixture
entity         = all_india
metric         = demand_met
value          = 218400
unit           = MW
quality        = good
schema_version = 1
```

Supported quality states currently include:

```text
good
suspect
bad
estimated
unknown
```

The database rejects unsupported quality states and invalid schema versions.

---

# Resilient Source HTTP Client

All future source adapters use a common HTTP client rather than implementing network behavior independently.

Current capabilities include:

### Timeout handling

Requests have configurable timeout limits.

### Retry handling

Temporary server failures can be retried automatically.

Current retryable HTTP statuses include:

```text
500
502
503
504
```

### Exponential backoff

Retries do not happen continuously.

For example:

```text
attempt 1
   ↓
wait 0.5 s

attempt 2
   ↓
wait 1.0 s

attempt 3
```

### Request IDs

Every logical HTTP operation receives an:

```text
X-Request-ID
```

The same request ID is preserved across retries.

This will later allow one source poll to be traced across logs and services.

### Structured exceptions

The ingestion layer currently distinguishes:

```text
SourceTimeoutError
SourceNetworkError
SourceResponseError
SourceInvalidContentError
```

This allows future source-health and retry logic to distinguish a slow source from malformed data or an HTTP failure.

---

# Tests

Run the complete test suite:

```bash
pytest -v
```

Run the HTTP-client tests:

```bash
pytest tests/unit/ingestion/test_http_client.py -v
```

Current tests cover:

* Successful JSON response
* Request-ID generation
* Timeout behavior
* Timeout retry exhaustion
* Temporary HTTP 5xx recovery
* HTTP 5xx retry exhaustion
* Invalid JSON/content

---

# Local Development Setup

## Requirements

Install:

* Git
* Python 3.11+
* Node.js
* Docker Desktop

---

## Clone

```bash
git clone https://github.com/sannx4/gridpulse-india.git
cd gridpulse-india
```

---

## Create Python Environment

Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

Upgrade pip:

```cmd
python -m pip install --upgrade pip
```

Install Python dependencies:

```cmd
pip install black ruff pytest pre-commit sqlalchemy alembic "psycopg[binary]" python-dotenv httpx
```

Install Git hooks:

```cmd
pre-commit install
```

---

## Install JavaScript Dependencies

```cmd
npm install
```

---

# Environment Configuration

Copy:

```cmd
copy .env.example .env
```

Then configure local database credentials.

Example:

```env
POSTGRES_DB=gridpulse

POSTGRES_ADMIN_USER=grid_admin
POSTGRES_ADMIN_PASSWORD=change_me

APP_DB_USER=grid_app
APP_DB_PASSWORD=change_me

POSTGRES_PORT=5433

DATABASE_URL=postgresql+psycopg://grid_app:change_me@localhost:5433/gridpulse
MIGRATION_DATABASE_URL=postgresql+psycopg://grid_admin:change_me@localhost:5433/gridpulse
```

Never commit the real `.env` file.

---

# Start TimescaleDB

Make sure Docker Desktop is running.

Then:

```cmd
docker compose up -d
```

Check:

```cmd
docker compose ps
```

The database should eventually show:

```text
healthy
```

---

# Database Migrations

Apply all migrations:

```cmd
alembic upgrade head
```

Check the current revision:

```cmd
alembic current
```

Inspect the database:

```cmd
docker compose exec db psql -U grid_admin -d gridpulse
```

---

# Code Quality

Run Ruff:

```cmd
ruff check .
```

Run formatting:

```cmd
black .
```

Run all pre-commit checks:

```cmd
pre-commit run --all-files
```

---

# Git Workflow

Development should happen through feature branches rather than directly on `main`.

Update local `main`:

```cmd
git checkout main
git pull origin main
```

Create a feature branch:

```cmd
git checkout -b feature/my-feature
```

After development:

```cmd
git add .
git commit -m "feat: describe the change"
git push -u origin feature/my-feature
```

Then open a Pull Request into:

```text
main
```

---

# Development Roadmap

## Month 1

Goal:

```text
One real source
    ↓
TimescaleDB
    ↓
FastAPI
    ↓
WebSocket
    ↓
React + D3
    ↓
Public deployment
```

# Future Engineering Areas

The complete GridPulse roadmap will progressively add:

### Data Engineering

* Multiple permitted grid sources
* Kafka-compatible event streaming
* Schema Registry
* Normalization
* Dead-letter queue
* Replay
* Parquet cold storage
* DuckDB historical queries

### Grid Analytics

* Frequency monitoring
* Demand analysis
* Generation mix
* State-level grid visualization
* Net-load / duck-curve analytics
* Renewable-share analytics
* Ramp analysis

### Machine Learning

* Frequency anomaly detection
* Demand anomaly detection
* Explainable incidents
* Day-ahead demand forecasting
* Prediction intervals
* Forecast accuracy monitoring

### Backend

* REST APIs
* WebSockets
* Redis caching
* API keys
* Authentication
* Rate limiting
* API versioning

### Reliability

* Source-health monitoring
* Duplicate handling
* Idempotent replay
* Crash recovery
* DLQ recovery
* Backup and restore
* Chaos testing
* Soak testing

### Production Engineering

* CI/CD
* Docker images
* Kubernetes
* Terraform
* TLS
* Prometheus
* Grafana
* Structured logging
* SLOs
* Load testing
* Security hardening

---

# Engineering Principles

GridPulse follows several rules throughout development.

### Use permitted data sources

Do not assume every grid website exposes a stable public API. Each source adapter must respect the actual source format, refresh cadence, and access conditions.

### Preserve provenance

Every measurement must remain attributable to its originating source.

### Keep timestamps explicit

`observed_at` and `ingested_at` represent different events and must never be treated as interchangeable.

### Treat data quality as first-class information

Missing, stale, malformed, estimated, or suspect measurements should be represented explicitly.

### Prefer idempotency over magical exactly-once claims

Later streaming components will use deterministic event identities and idempotent storage behavior.

### Introduce infrastructure only when justified

Kafka, Redis, Kubernetes and other components are added when the architecture develops an actual requirement for them.

---

# Project Goal

The finished GridPulse India platform is intended to demonstrate production-level engineering across:

```text
Backend Engineering
Data Engineering
Database Engineering
Full-Stack Development
Data Visualization
Machine Learning
Distributed Systems
Cloud / Platform Engineering
DevOps
SRE
Testing
System Design
```

The goal is not simply to create another electricity dashboard.

The goal is to build a system where an engineer can answer questions such as:

```text
What happens if a source times out?

What happens if the source sends malformed data?

What happens if an observation arrives twice?

What happens if the source schema changes?

How fresh is the current grid measurement?

How do we replay historical events?

How do we query one year of telemetry efficiently?

How does the system recover after a consumer crash?

How accurate is tomorrow's demand forecast?

How does the API behave under load?

How do we know production is healthy?

How quickly can the system recover from failure?
```

That engineering evidence is the core of GridPulse India.
