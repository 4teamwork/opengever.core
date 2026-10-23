---
title: 'Background Tasks Control Panel'
type: 'feature'
created: '2026-09-03'
baseline_commit: 'a9268661a0c926861c760e4de2a253cc7bd20bb5'
status: 'done'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Background tasks are only observable by querying the `background_tasks` SQL table directly. Administrators have no UI to see what is queued, running, or has failed on their admin unit.

**Approach:** Add a Plone control panel (`@@background-tasks-controlpanel`) built on the existing tabbedview/SQL-table-source machinery — mirroring `OGDSControlPanel` + `UsersListing` — that lists `BackgroundTask` rows of the current admin unit with a status filter.

## Boundaries & Constraints

**Always:**
- Read-only listing. No actions (retry, cancel, delete) — `show_selects = False`, empty `enabled_actions`/`major_actions`.
- Scope every query to the current admin unit (`get_current_admin_unit().unit_id`).
- Guard the control panel with the `cmf.ManagePortal` permission.
- Python 2.7; unicode literals for all user-facing strings; `@implementer`/`implements` consistent within a class.
- Column labels are i18n messages; tab label is translated by tab id in the `ftw.tabbedview` domain (see `opengever/base/locales/`).

**Ask First:**
- Adding write/administrative actions to the listing.
- Exposing tasks across admin units.

**Never:**
- Do not add a REST API endpoint or a new SQL model/column — the `BackgroundTask` model is complete.
- Do not add the tab to the existing `OGDSControlPanel`; this is its own control panel.
- Do not render `task_arguments`, `checkpoint_data` or `error_message` in the table.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Default view | Tasks of current admin unit in all four statuses | Rows for `pending`, `running`, `failed`; the `succeeded` row is hidden | N/A |
| Explicit status filter | `?background_task_status_filter=filter_succeeded` | Only `succeeded` rows | N/A |
| All filter | `?background_task_status_filter=filter_all` | All rows incl. `succeeded` | N/A |
| Foreign admin unit | Task rows with a different `admin_unit_id` | Never listed under any filter | N/A |
| Default sort | Several tasks with different `created` timestamps | Newest `created` first | N/A |
| Unfinished task | `started`/`finished` are `NULL` | Empty cell, no traceback | Date helper returns `u''` for `None` |
| No admin unit | `get_current_admin_unit()` returns `None` | Empty listing | Return an empty query, do not raise |

</frozen-after-approval>

## Code Map

- `opengever/bgtasks/model.py` -- `BackgroundTask`, `BackgroundTaskQuery.by_admin_unit()`, `TASK_STATUS_*` constants. Read-only reference.
- `opengever/tabbedview/browser/ogdscontrolpanel.py` -- control-panel `TabbedView` pattern to mirror.
- `opengever/tabbedview/browser/users.py` -- `BaseListingTab` + `Filter`/`FilterList` + `SqlTableSource` adapter pattern to mirror.
- `opengever/journal/tab.py` -- reference for `sort_reverse = True` and `ftw.table.helper.readable_date_time`.
- `opengever/tabbedview/browser/configure.zcml` -- registers the adapter, `ogds-controlpanel` page and `tabbedview_view-*` tab pages.
- `opengever/core/profiles/default/controlpanel.xml` -- configlet registrations.
- `opengever/base/locales/{ftw.tabbedview.pot,{de,en,fr}/LC_MESSAGES/ftw.tabbedview.po}` -- tab-id labels (e.g. `ogds-cp-alltasks`).
- `opengever/tabbedview/locales/{opengever.tabbedview.pot,{de,en,fr}/LC_MESSAGES/opengever.tabbedview.po}` -- column/filter labels.
- `opengever/tabbedview/tests/test_user_listing.py` -- listing test pattern (`browser.css('.listing').first.lists()`).
- `opengever/bgtasks/tests/test_model.py` -- how `BackgroundTask` rows are created in tests.

## Tasks & Acceptance

**Execution:**
- [x] `opengever/tabbedview/browser/backgroundtasks.py` -- new module with: `BackgroundTasksControlPanel(TabbedView)` exposing one tab `bgtasks-cp-tasks`; `IBackgroundTasksTableSourceConfig(ITableSourceConfig)`; a `StatusFilter(Filter)` filtering `status == <value>` and a `NotSucceededFilter(Filter)` filtering `status != succeeded` (default); `BackgroundTasksListing(BaseListingTab)` with `model = BackgroundTask`, `show_selects = False`, `sort_on = 'created'`, `sort_reverse = True`, `filterlist_name = 'background_task_status_filter'`, columns `created`, `started`, `finished` (transform `ftw.table.helper.readable_date_time`), `task_id`, `task_type`, `status`, and a `get_base_query()` returning `BackgroundTask.query.by_admin_unit(...)` (empty query when there is no admin unit); `BackgroundTasksTableSource(SqlTableSource)` adapter with `searchable_columns` on `task_id`, `task_type`, `status`. -- Mirrors the OGDS control panel so the tabbedview machinery works unchanged.
- [x] `opengever/tabbedview/browser/configure.zcml` -- register `.backgroundtasks.BackgroundTasksTableSource` adapter, the `background-tasks-controlpanel` browser page (`for` `IPloneSiteRoot`, permission `cmf.ManagePortal`, `allowed_interface="ftw.tabbedview.interfaces.ITabbedViewEndpoints"`) and the `tabbedview_view-bgtasks-cp-tasks` page (`for` `IPloneSiteRoot`, permission `cmf.ManagePortal`). -- Unregistered components are silently ignored.
- [x] `opengever/core/profiles/default/controlpanel.xml` -- add a `Background Tasks Control Panel` configlet (`action_id="background-tasks-controlpanel"`, `appId="opengever.bgtasks"`, category `Products`, permission `Manage portal`). -- Makes the panel reachable from site setup.
- [x] `opengever/core/upgrades/20260903120000_add_background_tasks_controlpanel/` -- new upgrade step directory with empty `__init__.py`, a `controlpanel.xml` containing only the new configlet, and `upgrade.py` defining an `UpgradeStep` subclass whose `__call__` runs `self.install_upgrade_profile()`. -- GenericSetup profile changes need an upgrade step for existing deployments.
- [x] `opengever/base/locales/ftw.tabbedview.pot` + `de|en|fr/LC_MESSAGES/ftw.tabbedview.po` -- add msgid `bgtasks-cp-tasks` (de: `Hintergrundaufgaben`, fr: `Tâches en arrière-plan`, en: `Background tasks`). -- Tab labels are resolved by tab id in this domain.
- [x] `opengever/tabbedview/locales/opengever.tabbedview.pot` + `de|en|fr/LC_MESSAGES/opengever.tabbedview.po` -- add the new column and filter msgids with de/fr/en translations. -- All user-facing strings must be translatable.
- [x] `opengever/tabbedview/tests/test_background_tasks_listing.py` -- integration tests covering every row of the I/O & Edge-Case Matrix. -- Locks in default filter, admin-unit scoping and sort order.

**Acceptance Criteria:**
- Given a site administrator, when they open the Plone control panel overview, then a "Background Tasks Control Panel" entry is listed and opens `@@background-tasks-controlpanel`.
- Given a non-manager user, when they request `@@background-tasks-controlpanel`, then access is denied (`cmf.ManagePortal`).
- Given the listing is rendered, when the header row is read, then the columns are `created`, `started`, `finished`, `task_id`, `task_type`, `status` in that order.
- Given the status filter list, when it is rendered, then it offers one entry per `TASK_STATUS_ALL` value plus "all" and the default "not succeeded", with the latter preselected.

## Spec Change Log

## Design Notes

`BackgroundTask.query` already returns a `BackgroundTaskQuery`, so the base query composes directly:

```python
def get_base_query(self):
    admin_unit = get_current_admin_unit()
    if admin_unit is None:
        return BackgroundTask.query.filter(false())
    return BackgroundTask.query.by_admin_unit(admin_unit.unit_id)
```

`SqlTableSource` sorts via `self.config.sort_reverse` (not `sort_order`), so descending order requires `sort_reverse = True`.

The listing extends `FilteredListingTab`, not `BaseListingTab` as `users.py` does. `BaseListingTab` renders `generic.pt`, which omits the whole container - filters included - when `view/contents` is empty; that would trap the user on the default "not succeeded" filter on a healthy system where every task has succeeded. `FilteredListingTab` renders `generic_with_filters.pt`, which keeps the filters reachable on an empty result.

`created`/`started`/`finished` use a local `readable_datetime` wrapper around `ftw.table.helper.readable_date_time` so a NULL `started`/`finished` renders as an empty cell instead of raising.

`status` is deliberately absent from `searchable_columns`: the column is rendered translated, so a text search over the raw token could never match what the user sees.

Filters must only narrow the query; the admin-unit restriction lives in `get_base_query()` so no filter can widen it.

## Verification

**Commands:**
- `bin/test opengever.tabbedview.tests.test_background_tasks_listing` -- expected: all pass (buildout may not be installed in this checkout; then rely on manual checks)
- `python -c "import opengever.tabbedview.browser.backgroundtasks"` -- expected: no ImportError

**Manual checks (if no CLI):**
- `@@background-tasks-controlpanel` renders one tab whose table shows the six columns, newest `created` first, without `succeeded` rows until the filter is switched; rows belonging to another `admin_unit_id` never appear.
