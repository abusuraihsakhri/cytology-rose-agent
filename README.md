# Cytology ROSE Agent

Research prototype for organizing rapid on-site evaluation (ROSE) specimen parameters, experimental threshold flags, and simple audit records. The repository contains a Python CLI, a local FastAPI service, and a self-contained browser demonstration.

> **Not a clinically validated medical device.** The numerical boundaries (primary >25 and secondary >12), keyword checks, Bethesda heuristics, and needle-pass recommendations are experimental software logic, not established cytopathology adequacy criteria. They must not be used for diagnosis, specimen acceptance, procedural decisions, or patient management.

## Features

- Python command-line evaluation, CSV batch processing, and local API.
- Three deterministic Python workers: primary-metric threshold, secondary-metric/priority flag, and status-descriptor keyword review.
- In-memory HMAC-SHA256 audit ledger with per-entry signature and chain-link verification.
- A static, JavaScript-based browser demonstration under `web/` using the same basic thresholds, with JSON export.
- Legacy ROSE modules and experimental Bethesda, needle-pass, and crush-artifact utilities. Their heuristics are not clinically validated.
- Supervisory chat currently uses a deterministic mock response, **not** a connected language-model service.

## Browser demonstration

The source lives in [web/index.html](web/index.html). When GitHub Pages is enabled, the Pages workflow publishes `web/`. Without Pages, run a local static server:

```bash
python -m http.server 8080 --directory web
```

Then open `http://127.0.0.1:8080/`. Calculations occur locally in JavaScript; no backend, Python runtime, Pyodide, account, or remote inference is required. Results are **not signed** and are cleared on reload. The browser demonstration is intentionally separate from the authenticated Python API.

## Install and use Python

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[server,test]"
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python cli.py audit --task-id TASK-001 --target SPECIMEN-01 --primary 28.5 --secondary 14.2
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python -m pytest -v
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` and set environment variables using `$env:AUDIT_SECRET_KEY = ...`.

The primary CLI accepts CSV columns `task_id`, `target_identifier`, `primary_metric`, `secondary_metric`, `status_descriptor`, and `is_critical_flag`. It also recognizes the legacy names in `sample.csv`, including `case_id`, `metric_primary`, `metric_secondary`, and `is_stat`. Boolean values such as `True` and `False` are parsed explicitly. Validation errors return a nonzero exit code instead of silently applying numeric defaults.

## Local API and containers

The primary FastAPI application is `agents.api:app`. Start it locally:

```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

`GET /health` is public for service checks. All other endpoints (`/api/audit`, `/api/chat`, `/api/audit/logs`, `/metrics`) require an `X-API-Key` header when `CYTOLOGY_API_KEY` is configured. Without an API key, they are accessible only from loopback. Set a strong `CYTOLOGY_API_KEY` for any container or proxy deployment.

```bash
export CYTOLOGY_API_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

Compose requires **both** environment variables and binds port 8000 to the host loopback interface. API access control is not a replacement for TLS, access management, or deployment-specific security review.

## Privacy and audit limitations

**Use synthetic identifiers and non-patient data only.** The regex-based identifier guard is incomplete and is not a PHI anonymization or HIPAA compliance guarantee. The Python API retains dossiers and audit records in process memory; batch CSV output is written to the specified local path. Audit signatures are verified in memory and are not persisted or anchored to external storage, so restart destroys the ledger and terminal-entry deletion is not independently detectable. The browser demonstration does not persist or transmit entries, and its JSON export is downloaded to your device.

## Verification and technology

Run `python -m pytest -v` for Python tests and `node --test web/test.mjs` for JavaScript behavior; `node --check web/app.mjs` checks JavaScript syntax. GitHub Actions runs Python 3.10–3.12 checks and a static Pages deployment workflow. Modern browsers supporting JavaScript modules are required for the browser demonstration.

Technology: Python, Pydantic 2, FastAPI/uvicorn (optional server), pytest, JavaScript modules, and GitHub Actions. No browser Python runtime is used because this small standalone demonstration needs none.

## License

[MIT](LICENSE).
