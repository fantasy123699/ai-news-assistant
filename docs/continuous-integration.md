# Continuous integration

`.github/workflows/backend-ci.yml` runs the backend quality checks on pushes to `main` and `codex/config-baseline`, and on pull requests.

The job uses Python 3.12 and verifies:

- the complete standard-library unit test suite;
- the checked-in citation-grounding fixtures;
- Python source compilation;
- OpenAPI schema generation;
- installed dependency consistency.

Tests use mocks and a non-secret placeholder database URL, so the workflow does not require MySQL, Redis, or a model server. Database integration tests should be added later as a separate module with an isolated service and migration setup.

The workflow has read-only repository permissions and a ten-minute timeout. Dependency caching is keyed from `requirements.txt` by `setup-python`.
