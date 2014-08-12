from zope.interface import Interface


class ITaskQuery(Interface):
    """A global utility for querying opengever tasks.
    """

    def get_tasks_for_responsible(responsible):
        """Returns all tasks assigned to the given responsible.
        """

    def get_tasks_for_issuer(issuer):
        """Returns all tasks issued by the given issuer.
        """
