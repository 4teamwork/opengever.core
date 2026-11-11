<!-- bmad:context -->
<!-- Verified 2026-11-09 against 5d0901d98. Managed by bmad-project-context; edits inside this block are replaced on refresh. Keep anything you want preserved outside the markers. -->

## opengever.core

OneGov GEVER backend: Plone 4.3.20 / Zope 2 on Python 2.7, SQLAlchemy 1.3 + Alembic for OGDS, Solr via ftw.solr, Redis. Code is in `opengever/` and `plonetheme/`. Docker (`compose.yaml`, `docker/`) is the way to run tests; the buildout `.cfg` files are the legacy path.

## Policy

- Python 2.7 only: no f-strings, no bare `super()`, `from urllib import urlencode`.
- Keep SQL and schema changes Oracle-compatible: constraint and index names under 30 characters, no `ON CONFLICT`, `RETURNING` or `::`. Use `is_oracle()` from `opengever.base.model` where unavoidable.
- Any GenericSetup profile change needs an upgrade step in the package's `upgrades/`. Any SQLAlchemy model change needs an Alembic migration plus an upgrade step.
- Never import ORM models inside upgrade steps; use raw SQL or Alembic ops, since the model may have moved on.
- Every PR needs a towncrier entry `changes/<TI-id>.<feature|bugfix|other>`.
- Branches are `<initials>/TI-XXXX/<short-description>`. Commit messages are imperative English with no ticket prefix.

## Running and verifying

- Run only specific tests, never the whole suite (it takes very long; CI runs it):
  `docker compose run --rm ogcore-test bin/test -m <module_name> -t <test_name>`
- Lint:
  `docker compose run --rm ogcore-test bin/flake8 opengever plonetheme`
  `docker compose run --rm ogcore-test bin/isort -c`
- `./opengever` is mounted into the container, so host edits need no rebuild. Rebuild (`docker compose --profile test build ogcore-test`, needs `GITLAB_DEPLOY_TOKEN` exported) only after changing `docker/core/` or the requirements.
- Service layers (msgconvert, pdflatex, sablon, weasyprint, redis) start their own Docker containers unless `MSGCONVERT_URL`, `PDFLATEX_URL`, `SABLON_URL`, `WEASYPRINT_URL` or `REDIS_URL` is set; Solr is skipped when `SOLR_HOST` is set. Compose sets them for `ogcore-test`.
- flake8 excludes `tests`.

## Conventions that differ from defaults

- New tests use `IntegrationTestCase` (`SolrIntegrationTestCase` only when real Solr is needed). `FunctionalTestCase` is legacy. Create content with `ftw.builder` (`create(Builder(...))`), never `invokeFactory`.
- Anything that applies to `document` must be tested for `mail`; anything for `task` must be tested for `forwarding`.
- isort style: single-line imports, alphabetical, `from` imports first.
- Use the length constants from `opengever.base.model` (`CONTENT_TITLE_LENGTH`, ...) for column sizes.
- Use `Oguid.parse()`, never string concatenation, for cross-unit references. OGDS data lives in SQL, not ZODB.

<!-- /bmad:context -->
