# TI-3947 Implementation plan: alternative email address for notifications

Technical companion to the story. Affects `opengever.core` and `gever-ui`. The OGDS sync (`ogds-sync`) is not changed.

## Overview

- Users manage the alternative address themselves in their personal notification settings.
- It is stored in a new column `notification_email` on the existing `user_settings` table.
- The feature is enabled per installation through a feature flag in the registry (default off).
- A central resolver determines the recipient address for all system notifications.

## Storage: `user_settings` instead of `email2`

The existing field `User.email2` is deliberately not used:

- `email2` is visible to all users:
  - User listing: `opengever/api/ogdsuserlisting.py:25`
  - User serialization: `opengever/api/serializer.py:599`
  - Doc property `ogg.user.email2`: `opengever/dossier/docprops.py:161`
  - User report: `opengever/globalindex/browser/report.py:147`
- `email2` is offered as a second selectable address of the user: `opengever/ogds/base/sources.py:797`.
- `email2` lives in the `users` table, which is owned by the OGDS sync. An entry in the `user_attribute_mapping` of a sync profile would overwrite the values maintained by users.

The `user_settings` table is not written by the OGDS sync. `sync_users` only updates the mapped columns of the `users` table and sets missing users to `active = false` (`ogds_sync/sync.py`). The setting therefore survives for deactivated users as well.

## opengever.core

### Model and upgrade

File: `../../opengever/ogds/models/user_settings.py`

```python
class IUserSettings(Interface):
    ...
    notification_email = schema.TextLine(required=False, constraint=is_valid_email)


class UserSettings(Base):
    ...
    notification_email = Column(String(EMAIL_LENGTH), nullable=True)
```

- Upgrade step adding the column, analogous to `../../opengever/core/upgrades/20190628113055_add_user_settings_table`.
- `UserSettings.get_setting` reads `Column.default.arg` when the user has no settings row. For `notification_email`, which has no default, this case must return `None`.

### Feature flag

File: `../../opengever/base/interfaces.py`, interface `IOGMailSettings`

```python
alternative_notification_email_enabled = schema.Bool(
    title=u'Allow users to set an alternative email address for notifications',
    default=False,
)
```

- Upgrade step registering the new registry record, analogous to `20200609102902_add_iog_mail_settings_registry_record`.
- Exposed as a feature through `@config` (`../../opengever/base/configuration.py`).

### API

File: `../../opengever/api/user_settings.py`

The `@user-settings` endpoint (GET/PATCH) iterates over `IUserSettings`. The new field is therefore readable and writable without an additional endpoint and also appears in `@config` under `user_settings`.

- Email format is validated through the schema constraint.
- An empty string is stored as `None` (removes the address).
- If the feature is disabled, PATCH rejects the field with `BadRequest`.
- Users can only change their own setting (existing behaviour).
- Update the API docs: `../public/dev-manual/api/usersettings.rst`, `docs/public/dev-manual/api/config.rst`, API changelog.

### Central resolver

New file: `opengever/activity/notification_email.py`

```python
def get_notification_email(user):
    if user is None:
        return None

    if is_alternative_notification_email_enabled():
        settings = user.user_settings
        if settings and settings.notification_email:
            return settings.notification_email

    return user.email
```

The resolver is used exclusively for recipient addresses of system notifications.

### Send paths

| File | Change |
|---|---|
| `opengever/activity/mailer.py:102` | Resolve the recipient address for `to_userid` through the resolver. Covers single notifications and digests. |
| `opengever/activity/mailer.py:108` | Detect self-notification via `from_userid == to_userid` instead of comparing email addresses. |
| `opengever/activity/mail.py:33` | Run the "recipient address present" check through the resolver. |
| `opengever/api/share_content.py:27` | Resolve content-sharing recipient addresses through the resolver. |

The sender and Reply-To logic in `mailer.py` keeps using `actor.email`.

To be clarified during implementation: `share_content.py` works with `ActorLookup(...).representatives()`. Verify that the representatives are OGDS users that can be passed to the resolver.

## gever-ui

Directory: `src/components/notification-settings/`

- New input field "Alternative email address for notifications" in the general section (`GeneralNotificationTable.vue`).
- The existing checkboxes there are loaded through `@notification-settings`. The new field is loaded and saved separately through `@user-settings`.
- Only visible when the feature is enabled in `@config`.
- Show the primary address as a hint.
- Clearing the field removes the address.
- Format validation in the frontend; display the backend's error message.
- Translations in `src/locale/de.json`, `fr.json`, `en.json`.

The classic view (`../../opengever/activity/browser/settings.py`) is not changed.

## Tests

### opengever.core

- With the feature disabled, `email` is used even if an alternative address is stored.
- With the feature enabled and an address stored, the alternative address is used.
- Without a stored address, fall back to `email`.
- Both addresses empty: no notification is sent.
- Sender and Reply-To addresses remain unchanged.
- Self-notifications are still detected correctly.
- Digest and content sharing use the resolved address.
- `@user-settings`: set, change and clear the address. Invalid format is rejected. PATCH with the feature disabled is rejected.
- The alternative address does not appear in the user listing, user serialization or doc properties.

### gever-ui

- Field only visible when the feature is enabled.
- Save, change and clear.
- Display of validation errors.

## Affected files

```
opengever/ogds/models/user_settings.py       Column and schema field
opengever/base/interfaces.py                 Feature flag in IOGMailSettings
opengever/base/configuration.py              Feature in @config
opengever/core/upgrades/                     Column and registry record
opengever/api/user_settings.py               Feature check, empty value
opengever/activity/notification_email.py     New resolver
opengever/activity/mailer.py                 Recipient, self-notification
opengever/activity/mail.py                   Recipient address check
opengever/api/share_content.py               Content-sharing recipients
docs/public/dev-manual/api/                  API docs and changelog
gever-ui: src/components/notification-settings/   Input field
gever-ui: src/locale/                        Translations
```

## Effort

| Work package | Effort |
|---|---|
| Column `notification_email`, feature flag, upgrade steps, resolver | 0.5 PD |
| `@user-settings`: field, validation, feature check, API docs | 0.5 PD |
| Mailer, notification dispatcher and content sharing | 0.5–1 PD |
| Automated tests in opengever.core | 1 PD |
| gever-ui: input field, validation, translations, tests | 1 PD |
| Review, bug fixing and documentation | 0.5 PD |
| **Total** | **4–4.5 PD** |
