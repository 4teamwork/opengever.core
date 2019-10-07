from zope.interface import Interface


class IReminderStorage(Interface):
    """Storage abstraction for reminders.
    """

    def __init__(context):
        """Adapts the context for reminders to be stored on.
        """

    def set(option_type, user_id=None):
        """Set a reminder on the adapted object.

        option_type -- The kind of reminder to set
        user_id -- User to set the reminder for

        If no user_id is given, defaults to the currently logged in user.
        """

    def get(user_id=None):
        """Return reminder for adapted object, or None if no reminder exists.

        user_id -- User to get the reminder for

        If no user_id is given, defaults to the currently logged in user.
        """

    def list():
        """Return user_id -> reminder mapping of all reminders for adapted obj.
        """

    def clear(user_id=None):
        """Clear an existing reminder.

        user_id -- User to clear the reminder for

        If no user_id is given, defaults to the currently logged in user.
        """


class IReminderSupport(Interface):
    """Implements support for reminders for a particular content type.
    """

    def set_reminder(reminder, user_id=None):
        """Sets a reminder for the given object for a specific user or for the
        current logged in user.

        A previously set reminder for the given user for the given object will
        be overridden by the new reminder.
        """

    def get_reminder(user_id=None):
        """Get the reminder for the given object for a specific user or for
        the current logged in user.

        Returns None, if no reminder is set.
        """

    def get_reminders():
        """Get all reminders for this obj as a {userid: reminder} mapping.
        """

    def clear_reminder(user_id=None):
        """Removes a registered reminder for the given object for a specific
        user or for the current logged in user.
        """
