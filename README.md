[![CI](https://github.com/NelsonVasudevan/cicd-pipeline-github-actions/actions/workflows/ci.yml/badge.svg)](https://github.com/NelsonVasudevan/cicd-pipeline-github-actions/actions/workflows/ci.yml)

# CI/CD Pipeline with GitHub Actions

A fully automated CI/CD pipeline for a FastAPI + PostgreSQL app, built on GitHub Actions — covering linting, testing, containerization, SAST scanning, container vulnerability scanning, and registry publishing.

## Pipeline Architecture

git push
│
▼
Lint ──▶ Test ──┬──▶ Build (artifact upload) ──▶ Trivy Scan ──┬──▶ Push to GHCR
│                                              │
└──▶ CodeQL Security Scan ────────────────────
Six automated stages, two running in parallel (Build and CodeQL), with the image only published if every security gate passes.

## Tech Stack
- **GitHub Actions** — CI/CD orchestration
- **flake8** — Python linting
- **pytest** — automated testing
- **CodeQL** — static application security testing (SAST)
- **Trivy** — container image vulnerability scanning
- **GitHub Container Registry (GHCR)** — image publishing

## What This Demonstrates
- A multi-stage pipeline with proper dependency ordering (cheap checks first, expensive checks later)
- Parallel job execution for independent stages (Build and CodeQL don't depend on each other)
- Passing build artifacts between jobs instead of redundantly rebuilding — the image scanned by Trivy is the exact image that gets published, not a fresh rebuild
- Security gates that actually fail the pipeline (`exit-code: 1` on CRITICAL/HIGH findings), not just informational reports
- Least-privilege permissions scoped per job (e.g. `security-events: write` only on jobs that need it)
- Registry publishing restricted to `main` branch pushes only — feature branches and PRs never publish images

## How to Run Locally

```bash
git clone https://github.com/NelsonVasudevan/cicd-pipeline-github-actions.git
cd cicd-pipeline-github-actions
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
docker compose up --build
```

## Pipeline Stages Explained

| Stage | What it does | Fails the build if... |
|---|---|---|
| Lint | Runs flake8 against `app/` and `tests/` | Any style/logic issue found |
| Test | Runs pytest unit tests | Any test fails |
| Build | Builds the Docker image, uploads as artifact | Docker build fails |
| CodeQL | Static analysis of source code | Security vulnerability found in code |
| Trivy Scan | Scans the built image for known CVEs | CRITICAL or HIGH severity finding |
| Push to GHCR | Publishes validated image to registry | (Only runs if all above pass, and only on `main`) |

## Design Decisions & Trade-offs

- **Artifact passing over rebuilding**: initially rebuilt the Docker image separately in the Trivy scan job — redundant and technically risks scanning a non-identical image. Switched to `upload-artifact`/`download-artifact` so the exact built image is what gets scanned and published.
- **`needs: test` on both Build and CodeQL** (not chained sequentially): these two stages don't depend on each other, so running them in parallel reduces total pipeline time without sacrificing safety.
- **CRITICAL/HIGH threshold for Trivy, not zero-tolerance on all severities**: blocking on every LOW/MEDIUM finding would make the pipeline impractically noisy; this mirrors realistic organizational policy.
- **Pinned local dev to Python 3.12** (matching the Dockerfile's base image) after hitting a `psycopg2-binary` build failure on Python 3.14 — keeping local and container environments consistent avoided a class of "works differently locally vs. in CI" bugs.

## What I'd Do Differently at Scale
- Add Dependabot or Renovate for automated dependency update PRs, so version drift is caught before a scan does
- Add a `staging` deployment stage that only promotes to `production` after manual approval (this becomes relevant again in Repo 4's Azure Pipelines setup)
- Cache pip/Docker layers between runs to speed up pipeline execution time

## Repo Structure
cicd-pipeline-github-actions/
├── .github/workflows/ci.yml
├── app/
│   ├── main.py
│   ├── database.py
│   └── models.py
├── tests/
│   ├── init.py
│   └── test_main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .flake8
├── .env.example
└── README.md


