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
