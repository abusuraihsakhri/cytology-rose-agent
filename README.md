# Cytology ROSE Agent

> **Domain:** Digital Pathology & Quantitative Histopathology  
> **Reference Guidelines & Standards:** `College of American Pathologists (CAP) Synoptic Protocols & DICOM WSI`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.11-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Cytology ROSE Agent** is an advanced analytical and computational platform implementing Rapid On-Site Evaluation (ROSE) Cytology Adequacy & Smear QC. It provides multi-agent consensus evaluation of cytopathology specimens with cryptographic audit trails and zero-PHI outbound protection.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — Enumeration for severity levels (INFO, ADVISORY, WARNING, CRITICAL_ACTION_REQUIRED).
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — Structured alert model with urgency, technical details, and remediation.
- **`CellularityAssessmentAgent`**: Specialized Sub-Agent 1 for cytology-rose-agent
- **`AdequacyScorerAgent`**: Specialized Sub-Agent 2 for cytology-rose-agent
- **`SlideSmearQCAgent`**: Specialized Sub-Agent 3 for cytology-rose-agent

### 🏗️ Enterprise Agent Architecture

- **`InvariantQCWorker`**: Primary mathematical & protocol boundary auditor.
- **`SafetyEscalationWorker`**: Safety boundary, toxicity & emergency interlock worker.
- **`ProtocolConformanceWorker`**: Spec conformance, anomaly triage & discordance checker.
- **`SystemSupervisor`**: Master orchestrator coordinating multi-worker evaluations.

---

## 💻 CLI Quickstart & Usage

### Installation
```bash
pip install -e .
```

### 1. Run Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Query Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch Process CSV Records
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch FastAPI REST Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task/case identifier | Required |
| `target_identifier` | Entity or specimen target key | Required |
| `primary_metric` | Primary domain measurement (float) | Required |
| `secondary_metric` | Secondary kinetic/confidence score | Optional |
| `status_descriptor` | Status code or phenotype descriptor | Optional |
| `is_critical_flag` | Emergency escalation trigger | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, DOBs, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

### Security Configuration

The `AUDIT_SECRET_KEY` environment variable **must** be set to a secure random value. The application will refuse to start without it:

```bash
export AUDIT_SECRET_KEY="your-secure-random-key-here"
```

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

### Docker
```bash
docker build -t cytology-rose-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY="your-secure-key" cytology-rose-agent
```

### Docker Compose
```bash
AUDIT_SECRET_KEY="your-secure-key" docker-compose up
```

---

## 📁 Project Structure

```
cytology-rose-agent/
├── agents/                  # Enterprise agent modules
│   ├── api.py              # FastAPI REST server
│   ├── base.py             # Security, PHI guard, audit trail
│   ├── models.py           # Pydantic data models
│   ├── supervisor.py       # Master orchestrator
│   ├── workers.py          # Specialized domain workers
│   ├── llm_factory.py      # LLM provider factory
│   ├── metrics.py          # Prometheus metrics
│   ├── learning.py         # Bayesian calibration engine
│   └── streamer.py         # WebSocket telemetry
├── tests/                  # Pytest test suite
├── web/                    # Operations console (HTML)
├── cli.py                  # Command-line interface
├── cyto_rose.py            # Legacy CLI & coordinator
├── enrichment.py           # Enrichment feature modules
├── simulator.py            # High-throughput simulator
├── pyproject.toml          # Project configuration
├── Dockerfile              # Container build
└── docker-compose.yml      # Multi-container orchestration
```
