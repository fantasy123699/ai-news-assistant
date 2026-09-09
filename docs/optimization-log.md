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
