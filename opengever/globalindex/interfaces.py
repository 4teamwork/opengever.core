from zope.interface import Interface


class ITaskQuery(Interface):
    """A global utility for querying opengever tasks.
    """

    def get_task(int_id, client_id):
        """Returns the task identified by the given int_id and client_id.
        """

    def get_tasks_for_responsible(responsible):
        """Returns all tasks assigned to the given responsible.
        """

    def get_tasks_for_issuer(issuer):
        """Returns all tasks issued by the given issuer.
        """


class IGlobalindexMaintenanceView(Interface):
    """"solr maintenance view for the global index"""

    def global_reindex():
        """Start task reindexing on all clients."""

    def local_reindex():
        """Method for reindexing all tasks from this client
        in the globalindex."""

    def check_predecessor_sync():
        """Method for checking if Tasks exists,
        who has a inconsistent Syncronisation."""

    def fix_responsible_synchronisation():
        """Method which fix the not synchron responsibility of tasks."""
