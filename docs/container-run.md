# Container run baseline

This repository includes a reproducible local container stack:

- FastAPI application on `http://localhost:8000`;
- MySQL 8.4 with schema and seed initialization on the first empty volume;
- Redis 7 for application cache access.

## Start and verify

```bash
docker compose up --build
```

Open `http://localhost:8000` and verify `http://localhost:8000/health` returns:

```json
{"status":"ok"}
```

Compose waits for MySQL and Redis health checks before starting the application. The application container runs as a non-root user.

The AI endpoints expect an Ollama-compatible service on the host at port `11435`. Override it when needed:

```bash
CONTAINER_LLM_BASE_URL=http://host.docker.internal:11434 docker compose up --build
```

In PowerShell, set `$env:CONTAINER_LLM_BASE_URL` before running the Compose command.

## Stop or reset

Stop containers while keeping database data:

```bash
docker compose down
```

`docker compose down --volumes` also deletes the local MySQL volume and all data in it. Use that reset command only when the stored development data is no longer needed.

## Deployment boundary

This Compose file is a local reproducibility baseline, not a production manifest. Its fallback passwords are development-only. A production deployment still requires managed secrets, HTTPS, database backups, migration controls, monitoring, and a verified rollback target.
