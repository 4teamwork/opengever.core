from opengever.activity.browser.settings import NotificationSettingsForm


class PersonalPreferences(NotificationSettingsForm):
    """The personal preferences form, linked in the users personal menu.

    The form currently contains only the NotificationSettingsForm, therefore
    this view inherits the `NotificationSettingsForm`.
    """
