---
title: 'TI-3947: Alternative email address for notifications'
type: 'feature'
created: '2026-10-30'
status: 'done'
baseline_commit: 'd3161d5000b69c731d2b16210200ca5add6032c3'
route: 'dispatch'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Users must authenticate with their organisation's accounts while optionally receiving system notifications at a private or business address maintained outside AD.

**Approach:** Store an optional personal notification address in GEVER, expose it in the new UI, and centrally resolve notification recipients behind an installation flag. Preserve the supplied `docs/bmad/TI-3947-implementation-plan.md` as source evidence.

## Boundaries & Constraints

**Always:** Default disabled. Support individual notifications, digests and workspace content sharing. Only the account owner can read/change this setting through application interfaces. Preserve it across OGDS sync and deactivation. Preserve primary identity, permissions, sender and Reply-To addresses. Prepare customer activation in installation configuration; do not deploy or run production migrations.

**Never:** Use `User.email2`; change AD/sync; expose the setting in listings, profiles, reports or document properties; add administrator editing, verification mail, per-workspace choices, dual delivery or classic-UI controls. Invitation delivery remains unchanged.

**Activation decision:** The feature must work in both GEVER and Teamraum installations. Enable it for the requesting customer only in the Teamraum (`tr`) profile and its upgrade; leave that customer's other installations disabled. Do not restrict the shared implementation or new-UI setting to Teamraum.

**Sharing decision:** Follow the original implementation plan, as explicitly requested after discussing the header implications. Resolve recipient addresses directly, preserving existing To/Cc/Bcc behavior; alternative addresses in To/Cc can therefore be visible to other mail recipients. Privacy applies to application settings, listings, profiles and document properties. Do not introduce envelope/header separation or individual copies.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| Disabled | Stored alternative or none | Primary address; field hidden | PATCH of field rejected |
| Enabled | Valid alternative | Deliver to alternative only | Existing delivery handling |
| Enabled | Empty/null alternative | Deliver to primary | No delivery if primary also absent |
| Update | Valid replacement or empty/null | Save replacement or clear | Invalid format/type/length rejected atomically |
| Missing user | No OGDS recipient | Skip delivery | No invalid mail queued |

</frozen-after-approval>

## Code Map

Paths are relative to `opengever.core` unless prefixed otherwise.

- `opengever/ogds/models/user_settings.py`: local SQL settings and schema; `get_setting()` assumes every column has a default. `users.email2` remains public/sync-owned.
- `opengever/api/user_settings.py`: current-user GET/PATCH; serializer also supplies config. Normalize clearing before schema validation; disabled writes must fail before mutations.
- `opengever/base/interfaces.py`, `configuration.py`: `IOGMailSettings` and config features.
- `opengever/core/upgrades/20191004104638_add_user_settings_column_seen_tours/upgrade.py`: column migration precedent; `20200609102902_add_iog_mail_settings_registry_record/`: registry precedent.
- `opengever/activity/{mail,mailer,digest}.py`: presence check, recipient preparation, digest dispatch. Digest currently lacks an empty-address guard and records sends unconditionally.
- `opengever/api/share_content.py`, `opengever/workspace/content_sharing_mailer.py`: actor representatives are OGDS users; shared headers currently also determine envelope recipients.
- `gever-ui/src/components/notification-settings/GeneralNotificationTable.vue`: UI insertion; `src/store/modules/notification-settings.js`: existing channel preferences. `src/store/index.js`: config features/current-user email; `src/models/validators.js`: reusable optional email validator.
- `<customer-policy>/tr/profiles/default/registry.xml`: customer Teamraum activation; `tr/upgrades/`: existing-installation upgrades. Leave the shared `base` profile unchanged.

## Tasks & Acceptance

**Execution:**
- [x] `opengever/ogds/models/user_settings.py` — add nullable `notification_email` with bounded email validation and safe missing-row default.
- [x] `opengever/base/{interfaces,configuration}.py`, `opengever/core/upgrades/` — default-off `alternative_notification_email_enabled`, config feature and additive column/registry upgrades.
- [x] `opengever/api/user_settings.py` — current-user read/write, normalize clear, reject disabled updates, preserve unrelated settings.
- [x] `opengever/activity/notification_email.py` — central flag-aware resolver; integrate in `mail.py`, `mailer.py`, `digest.py`, `opengever/api/share_content.py` and `opengever/workspace/content_sharing_mailer.py`. Skip empty delivery, including digest bookkeeping. Preserve direct-email callers and identify user-addressed self-notifications by userid.
- [x] `gever-ui/src/components/notification-settings/`, `src/store/modules/notification-settings.js`, `src/locale/{de,en,fr}.json` — independent email save via user-settings, primary-address hint, visibility, validation and backend errors. Channel reset must not clear email.
- [x] `<customer-policy>/tr/profiles/default/registry.xml`, `tr/upgrades/` — enable only the customer's Teamraum; separate feature branches for UI and policy repositories.
- [x] Backend `api/tests/test_{user_settings,share_content,config}.py`, `activity/tests/test_{mail,digest}.py`, `workspace/tests/test_content_sharing_mail.py`, `base/tests/test_configuration_adapter.py` — extend regression tests and add model/resolver/privacy coverage.
- [x] `gever-ui/tests/unit/store/notification-settings.spec.js`, new component tests — visibility, hint, set/change/clear and error cases.
- [x] `docs/public/dev-manual/api/{usersettings,config}.rst`, API changelog and `changes/` — document contract, activation and customer limitations.

**Acceptance Criteria:**
- Given either a GEVER or Teamraum installation with the flag enabled, when managing the setting and sending supported notifications, then the alternative address works; customer activation enables only Teamraum.
- Given each matrix state, when resolving/sending or saving, then its stated delivery and validation behavior holds.
- Given another account or administrator, when reading application user listings/profiles/properties/settings, then the private setting is not disclosed or editable for someone else.
- Given saved settings, when sync updates/deactivates a user, then the alternative survives.
- Given a self-notification or invitation, when sending, then identity checks and original sender/Reply-To/invitation routing remain correct.
- Given multiple sharing recipients, when sending, then resolved addresses retain existing To/Cc/Bcc semantics as specified in the original plan.
- Given no deliverable digest address, when processing, then no mail or successful-send record is produced.

## Implementation Notes

- Implemented across backend branch `ti-3947-alternative-notification-email`, UI and customer policy branches `feature/ti-3947-alternative-notification-email`. UI baseline: `448c167ec2f1f332e68cc36a8597d3c7350d979b`; customer policy baseline: `84d7d9c7c62ca19fd35fff6b4b20c2fbafd4d1d7`.
- Disabled installations omit the setting from serialized responses. Legacy notification-channel write/reset routes now allow only their existing channel settings, preventing validation bypass without adding classic-UI controls.
- Content sharing preserves its original primary-address sender comparison separately from resolved recipients; direct-email callers retain their behavior.
- Verified in isolated Python 2.7 Docker runtime with repository-pinned ftw.testing/testbrowser and Sablon: 160 passed, one pre-existing skip across 14 modules. `test_config_contains_is_readonly_flag` excluded after reproducing its identical failure on original HEAD with the same pinned dependencies.
- UI: 23 tests passed, targeted ESLint and i18n-ci passed. Additive column migration and registry import tests passed; XML parsing and diff checks passed. No deployment or production migrations executed.
- Matrix audit: resolver test covers disabled/enabled/fallback/missing user; API tests cover atomic set/change/clear/rejections; dispatcher/digest/sharing tests cover delivery and missing-address suppression; UI tests cover visibility and editing. All covering tests ran successfully.
- All three independent review layers completed. All 13 findings were addressed through ten grouped, minimal patches; nothing was deferred. Added actual OGDS import/update/deactivation coverage, parent UI embedding/channel-reset coverage, and fresh/shared/upgrade customer policy registry imports. Sender handling now also preserves shared-primary-mailbox behavior and safely handles missing primary addresses; mailbox component lengths and whitespace-only recipients are validated.
- Final combined verification: 177 backend tests selected, 176 passed and one existing skip (`test_config_contains_url_to_private_folder` is skipped in the repository for its userid-change fixture); no failures/errors. The separate baseline-proven readonly test remains excluded. UI: 24 passed; ESLint, i18n-ci and all diff checks passed.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and route |
|---|---|---|
| Blind 1: shared primary mailbox changes sender | medium | Verified userid-only comparison changes disabled behavior for distinct users sharing a mailbox. Patch: retain original primary-address equality alongside userid equality. |
| Blind 2: failed load has no retry | low | Fetch rejection leaves controls disabled, correctly protecting unknown state; error misleadingly requests retry. Patch direct correction: tell users to reload the page on load failure, retaining the disabled state. |
| Blind 3: missing primary sender | medium | `make_addr_header` stringifies None; newly deliverable alternative-only self-notifications emit invalid sender headers. Patch existing actor guard to use deployment sender when primary is absent, never private sender/Reply-To. |
| Blind 4: whitespace digest marked sent | medium | Resolver returns truthy whitespace while queue strips it. Patch normalization in resolver; test no successful digest record. |
| Blind 5: mailbox component lengths | medium | Regex accepts overlong local parts/domain labels under total bound. Patch bounded validator and boundary tests. |
| Blind 6: visibility explanation absent in UI | low | To/Cc exposure is intentional but only developer docs explain it. Patch a short translated informational hint beside the field. |
| Blind 7: customer activation untested | medium | Only core registry import is covered; fresh policy/upgrade could silently disable feature. Patch policy import tests, including sender-setting preservation and non-Teamraum baseline. |
| Blind 8: sync test uses direct identity updates | medium | Current test demonstrates SQL independence but misses existing updater path. Patch regression using OGDS updater test helpers; no sync code change. |
| Blind 9: empty channel-reset test | low | Empty general list does not exercise requests/mutations. Patch test with an actual channel reset and preserved email. |
| Edge 1: whitespace digest marked sent | medium | Same verified mismatch as Blind 4; grouped into resolver normalization patch. |
| Edge 2: overlong domain label | medium | Same validator defect as Blind 5; grouped into component-length patch. |
| Verification 1: editor not tested through parent | medium | Pre-verified: deleting parent embedding leaves isolated editor tests passing. Patch mounted GeneralNotificationTable integration test. |
| Verification 2: customer policy imports not exercised | medium | Pre-verified: flipping policy value bypasses existing tests. Grouped with Blind 7 profile-import coverage. |

## Verification

- Backend: Python 2.7 `zope-testrunner --test-path=/app` in an isolated `4teamwork/ogcore:2026.3.4` container, with `SABLON_URL` pointing to an isolated Sablon service. Test dependencies use repository-pinned `ftw.testbrowser==2.1.2`, `ftw.testing==2.0.7` and the testserver requirements. Source is copied into `/app`; actual customer policy registry files/interfaces/tests are copied without unrelated policy ZCML. Local IDE SDK remains unchanged.
- Modules: activity `test_mail`, `test_digest`, `test_notification_email`, `test_settings`; API `test_user_settings`, `test_share_content`, `test_config`, `test_notification_settings`; base `test_configuration_adapter`; core `test_notification_email_upgrade`; models `test_user_settings`; OGDS base `test_ogds_updater` excluding the unrelated legacy `TestOGDSUpdater` class; workspace `test_content_sharing_mail`, `test_invitation`; customer policy `test_notification_email_registry`. Exclude `test_config_contains_is_readonly_flag` only after its baseline comparison; all new tests execute.
- UI: `yarn test:unit tests/unit/store/notification-settings.spec.js tests/unit/components/notification_email_setting.spec.js`; targeted ESLint and `yarn i18n-ci`.
- Checked actual sharing envelopes/headers, default-off responses, privacy surfaces, fresh/additive schema behavior, registry imports and `git diff --check` in each repository.
