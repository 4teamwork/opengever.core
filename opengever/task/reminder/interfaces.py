from zope.interface import Interface


class IReminderStorage(Interface):
    """
    """

    def __init__(self, context, request):
        """
        """

    def set(self, reminder, user_id=None):
        """
        """

    def get(self, user_id=None):
        """
        """

    def list(self):
        """
        """

    def clear(self, user_id=None):
        """
        """


class IReminderSupport(Interface):
    """
    """
