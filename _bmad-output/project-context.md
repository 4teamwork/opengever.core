---
project_name: 'opengever.core'
user_name: 'Thomas'
date: '2026-06-12'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'upgrade_db_rules', 'workflow_rules', 'anti_patterns']
status: 'complete'
rule_count: 42
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

- **Python**: 2.7 (all code must be Python 2.7 compatible)
- **Plone**: 4.3.20 (Zope 2 + Zope 3 component architecture)
- **plone.restapi**: 6.14.0 (REST API services)
- **plone.rest**: 1.2.0
- **SQLAlchemy**: 1.3.24 (OGDS database layer, not for content)
- **SQLAlchemy-i18n**: 1.0.3
- **alembic**: 1.4.3 (DB schema migrations)
- **Redis**: 3.5.3 (pinned < 4)
- **Solr**: via `ftw.solr` (full-text search)
- **ftw.***: 4teamwork internal framework packages (see `versions.cfg`)
- **Build system**: zc.buildout with `.cfg` files
- **Dependency management**: `setup.py` + `versions.cfg` (KGS)

## Critical Implementation Rules

### Language-Specific Rules (Python 2.7)

- **Unicode strings**: Always use `u'...'` prefix for string literals that contain text (messages, titles, labels). Never use bare `'...'` for user-facing strings.
- **All msg-strings must be unicode** — enforced in PR checklist.
- **Imports**: Use `from urllib import urlencode`, NOT `urllib.parse`. Use `from Products.CMFPlone.utils import safe_unicode` to coerce to unicode safely.
- **`implements()` vs `@implementer`**: Both styles exist in the codebase. New code should use `@implementer` (Zope 3 style), but don't mix them in the same class.
- **`print`**: Don't use `print()` as a function without `from __future__ import print_function` — use logging instead.
- **Integer division**: `5/2 == 2` by default. Use explicit float conversion or `from __future__ import division` where needed.
- **Exception syntax**: `except SomeException as e:` (not the old comma style).
- **String formatting**: Use `%` formatting or `.format()` — f-strings are Python 3 only.
- **`super()`**: Must use `super(ClassName, self).method()` — not bare `super()`.
- **`range`/`xrange`**: Prefer `xrange` for iteration over large sequences.

### Framework-Specific Rules (Plone / Zope CA)

**Component Architecture (ZCML)**
- All new views, adapters, utilities, and REST API services must be registered in `configure.zcml` in the relevant sub-package. Code without ZCML registration is silently ignored.
- Use `z3c.autoinclude` — each sub-package's `configure.zcml` is auto-included; don't add manual includes unless overriding.

**Content Types (Dexterity)**
- Content types use `plone.dexterity`. Schemas defined via `plone.supermodel` XML or Python interfaces with `zope.schema` fields.
- If `missing_value` is specified on a field, `default` must be set to the same value (enforced in PR checklist).

**REST API Services (plone.restapi)**
- Services inherit from a base class (e.g., `RemoteTaskBaseService`) or directly from `plone.restapi` service classes.
- Register with `<plone:service>` in ZCML.
- Return errors as `zExceptions.BadRequest` — not Python exceptions — so they become proper 400 JSON responses.

**Feature Flags**
- Features are toggled via `plone.registry`. Use `FEATURE_FLAGS` dict in `IntegrationTestCase` to enable them in tests: `self.activate_feature('feature-name')`.
- Never hardcode feature availability — always check the registry flag.

**Content Access**
- Use `plone.api` for content operations where possible. Fall back to direct Zope/CMF APIs only when `plone.api` doesn't cover the use case.
- Use `api.content.find()` for catalog queries, but prefer `unrestrictedSearch` when security checks would incorrectly filter results.

**Workflow**
- Workflow states and transitions are defined in GenericSetup profiles (`profiles/default/`).
- Use `IInternalWorkflowTransition` request layer to suppress side-effects during programmatic transitions.

**OGDS (OpenGever Directory Service)**
- OGDS data (users, org units, admin units) lives in SQLAlchemy, NOT in the ZODB. Never mix ZODB content operations with OGDS SQL operations in the same transaction without understanding the implications.
- Access OGDS via `ogds_service()` from `opengever.ogds.models.service`.

### Testing Rules

**Base Classes — pick the right one**
- `IntegrationTestCase` — standard for all new tests; uses a shared fixture for speed.
- `SolrIntegrationTestCase` — only when the test requires real Solr indexing/querying.
- `FunctionalTestCase` / `SolrFunctionalTestCase` — legacy; avoid for new tests.
- All test classes live in `<package>/tests/test_<module>.py`.

**Test fixtures (ftw.builder)**
- Create objects with `create(Builder('content-type').having(field=value))`.
- Never create content directly via `portal.invokeFactory` in new tests — use builders.
- Pre-built fixture objects (e.g., `self.dossier`, `self.regular_user`) are available on `IntegrationTestCase` — check `opengever.testing` before creating new ones.

**Browser tests (ftw.testbrowser)**
- Browser-based tests use the `@browsing` decorator; the `browser` argument is injected automatically.
- Always call `self.login(user, browser)` before browser interactions — the fixture starts logged out.
- Use `browser.open(url, method='POST', data=json.dumps({...}), headers=self.api_headers)` for REST API calls.
- Use `with browser.expect_http_error(code=400):` to assert error responses.

**Assertions**
- Use `unittest` assert methods (`assertEqual`, `assertIn`, etc.) — not bare `assert`.
- `browser.json` gives the parsed JSON response body directly.

**Cross-type coverage**
- If a feature applies to `document`, it must also be tested for `mail`.
- If a feature applies to `task`, it must also be tested for `forwarding`.
- This is enforced in the PR checklist — agents must not forget it.

**Solr in tests**
- Solr is not available in standard `IntegrationTestCase`. Use `obj2solr()` / `solr_data_for()` helpers to inspect what would be indexed without a real Solr instance.
- Only use `SolrIntegrationTestCase` when you genuinely need search-result ordering or faceting.

### Upgrade Steps & DB Migration Rules

**When upgrade steps are required**
- Any change to a GenericSetup profile (new content type, workflow, registry entry, etc.) needs an upgrade step in the relevant package's `upgrades/` directory.
- Any SQLAlchemy model change (add/remove/alter column, add index, add constraint) needs both an Alembic migration AND an upgrade step.

**Critical: SQL operations in upgrade steps must NOT use imported models**
- Never do `from opengever.somepackage.model import SomeModel` inside an upgrade step and then query/insert via the ORM.
- Use raw SQL (`op.execute(...)`) or Alembic operations instead. The model may have evolved past the state the upgrade step assumes.

**Alembic constraint naming**
- All constraint names (primary key, foreign key, unique, check, index) must be **shorter than 30 characters** — Oracle has a 30-char identifier limit and this project supports Oracle.

**Make upgrade steps deferrable and conditional**
- If the operation is safe to defer, mark it as deferrable.
- Execute conditionally (check if column exists before adding) so steps are re-runnable without error.

**DB schema migrations**
- Every model change (column add/remove/rename, type change, new index, new constraint) must be accompanied by an Alembic migration. No exceptions.

### Development Workflow Rules

**Branch naming**
- Pattern: `{initials}/{ticket-id}/{short-description}`
- Example: `ran/TI-3358/fix-local-ogds`
- Ticket IDs are Jira format: `TI-XXXX`

**Commit messages**
- Plain English, imperative mood, no ticket prefix in the message body.
- Example: `Add is_local is none to ogds plugin`
- Reference the ticket in the PR body, not in every commit.

**Changelog**
- Every PR needs a changelog entry via `towncrier` in the `changes/` directory.
- File naming: `changes/{ticket-id}.{type}` where type is `feature`, `bugfix`, or `other`.

**PR requirements**
- PR body must explain: why the change is necessary, the goal, and key design decisions — written for an outsider who hasn't read the code or Jira issue.
- Link to Jira issue (`TI-XXXX`) in the PR body; add backlink in Jira.
- API changes: update docs + add API Changelog entry. Breaking changes need `api-change` label and team notification.

**Post-merge**
- After merge, Dev on Kubernetes must be updated.

**SQLAlchemy column length constants**
- Use named constants from `opengever.base.model` for column lengths (e.g., `CONTENT_TITLE_LENGTH`, `USER_ID_LENGTH`, `UNIT_ID_LENGTH`) — never hardcode magic numbers for column sizes.

### Critical Don't-Miss Rules

**Type symmetry**
- A feature touching `document` must also work for `mail` (they share many behaviors but are separate content types).
- A feature touching `task` must also work for `forwarding`.
- Tests must cover both. This is a frequent source of bugs.

**CSRF protection**
- Internal service-to-service endpoints that must bypass CSRF must explicitly call `alsoProvides(self.request, IDisableCSRFProtection)`.
- Never disable CSRF on user-facing endpoints.

**Oguid — the cross-unit object reference**
- Objects referenced across admin units use `Oguid` (e.g., `fd:12345`). Always parse with `Oguid.parse()` and wrap exceptions (`MalformedOguid`, `InvalidOguidIntIdPart`) as `BadRequest`.
- Never construct Oguid strings manually by concatenation.

**Security: unrestricted methods**
- `unrestrictedSearch`, `unrestrictedTraverse`, etc. bypass Plone's permission checks. Only use them in internal/system-triggered code paths, never when handling direct user requests.

**Oracle compatibility**
- The production stack includes Oracle. Any raw SQL or schema change must be Oracle-compatible:
  - Constraint names ≤ 30 characters.
  - Avoid PostgreSQL-specific syntax (`ON CONFLICT`, `RETURNING`, `::` cast operator).
  - Use `is_oracle()` from `opengever.base.model` to branch where unavoidable.

**Sentry / error handling**
- When fixing a bug, resolve any linked Sentry issues — don't just fix the code.

**New functionality follow-up**
- If a change is too large to complete fully, create follow-up Jira stories and link them in the PR and Jira issue — don't leave silent TODOs in code.

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code in this project.
- Follow ALL rules exactly as documented.
- When in doubt, prefer the more restrictive option.
- Update this file if new patterns emerge.

**For Humans:**
- Keep this file lean and focused on agent needs.
- Update when the technology stack or conventions change.
- Review quarterly for outdated rules.

Last Updated: 2026-06-12
