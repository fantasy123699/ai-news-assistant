# Project Optimization Log

## 2026-09-07 - Configuration baseline

### Scope

- Moved database and Redis configuration to environment-backed settings.
- Added a safe environment template and Python dependency manifest.
- Pinned bcrypt to a passlib-compatible release after validating password hashing.
- Added repository ignore rules and removed generated Python cache files from version control.

### Verification

- Configuration parsing is checked with temporary environment values.
- Python source compilation is checked after each configuration change.
- The committed diff is reviewed for credentials and unrelated changes.

### Follow-up

- Database schema and sample-data initialization remain a separate module.
- Authentication and authorization issues remain a separate module.

## 2026-09-09 - Database initialization

### Scope

- Added a MySQL schema for the eight tables referenced by the current ORM and SQL queries.
- Added foreign keys, uniqueness constraints, and indexes for existing query and deletion paths.
- Added rerunnable development seed data without creating a default account or credential.
- Added database initialization instructions for Bash and Windows PowerShell users.

### Verification

- Schema tables and columns are checked against the current model and CRUD usage.
- Foreign-key creation order and referenced column types are reviewed.
- Seed statements are checked for repeat execution without duplicate categories, articles, or relations.
- The committed diff is limited to database initialization files and this log entry.

### Follow-up

- Authentication and authorization hardening remain a separate module.
- Database migrations remain a later production-readiness module; this module only establishes a reproducible baseline.

## 2026-09-09 - Authentication and authorization hardening

### Scope

- Removed plaintext password verification and made password hashing dependencies fail closed.
- Added practical password and profile-field validation at the API boundary.
- Added a minimal `user`/`admin` role boundary without introducing a separate permission system.
- Restricted user administration and news mutation endpoints to authenticated administrators.
- Kept existing raw access tokens compatible while also accepting the standard Bearer header form.

### Verification

- Password hashing, plaintext rejection, password limits, token parsing, and role enforcement have unit coverage.
- Python compilation and the full standard-library test suite are run before commit.
- Route dependencies are reviewed to confirm that every administrative mutation is protected.
- The committed diff is limited to authentication, its database role migration, tests, and this log entry.

### Follow-up

- Token hashing, revocation of all sessions after password changes, and login rate limiting remain future security work.
- Fine-grained roles are intentionally not added because the current project only needs a small administrator boundary.

## 2026-09-09 - Reliable LLM client

### Scope

- Replaced thread-wrapped blocking HTTP calls with a native asynchronous model client.
- Added configurable request timeout, bounded exponential-backoff retries, and retryable status handling.
- Added safe upstream error mapping and rejected invalid or empty model responses.
- Added latency and retry logs without recording prompts, responses, or upstream error bodies.
- Added input bounds for AI endpoints and concise model-client documentation.

### Verification

- Mocked provider tests cover successful output, transient retries, timeouts, rejected requests, and empty output.
- Existing authentication tests, Python compilation, configuration parsing, and OpenAPI generation are rerun.
- Dependency integrity and the committed diff are reviewed before upload.

### Follow-up

- Retrieval quality, citations, evaluation datasets, and prompt versioning remain a separate RAG-quality module.
- Streaming output and token-usage accounting remain separate product enhancements.

## 2026-09-09 - RAG retrieval baseline

### Scope

- Added Chinese query-term extraction and explicit category detection.
- Replaced whole-question matching with parameterized multi-term retrieval and explainable field weights.
- Added category and recent-news fallback behavior for zero-hit queries.
- Added source identifiers to retrieved context, API references, and citation instructions.
- Added a seed-aligned Hit@K dataset and a reusable database-backed evaluation command.

### Verification

- Unit tests cover extraction, weighted SQL construction, category filtering, and fallback behavior.
- The evaluation dataset is parsed and the evaluator entry point is checked without requiring a running model.
- Existing authentication and LLM-client tests, Python compilation, OpenAPI generation, and dependency integrity are rerun.

### Follow-up

- Collecting anonymized real queries is the next requirement before choosing embeddings or a vector database.
- Prompt versioning and answer-level faithfulness evaluation remain separate improvements.

## 2026-09-09 - Prompt versioning and citation-grounding evaluation

### Scope

- Moved the site-news chat prompt into one versioned builder without changing its behavior.
- Returned the prompt version with site-chat responses for traceability.
- Added a deterministic answer-level check for invalid citations and uncited factual statements.
- Added reusable offline fixtures, a command-line evaluator, tests, and concise limitations documentation.

### Verification

- Unit tests cover prompt construction, version stability, valid citations, unknown citations, and uncited statements.
- The offline fixture evaluator must classify every checked-in case correctly.
- Existing authentication, LLM-client, and retrieval tests, Python compilation, OpenAPI generation, and dependency integrity are rerun.

### Follow-up

- Add reviewed real model responses before tuning prompt wording or thresholds.
- Semantic entailment scoring remains future work and should not be confused with deterministic citation coverage.
