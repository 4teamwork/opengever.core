from zope.interface import Interface
from zope import schema


class ITaskSettings(Interface):

    crop_length = schema.Int(title=u"Crop length", default=20)

    deadline_timedelta = schema.Int(
        title=u'Default timedelta in days for the deadline offset.',
        default=5)

    unidirectional_by_reference = schema.List(
        title=u'Task Types Unidirectional by Reference',
        description=u'',
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.task.unidirectional_by_reference',
        ),
        required=False,
    )

    unidirectional_by_value = schema.List(
        title=u'Unidirectional by Value',
        description=u'',
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.task.unidirectional_by_value',
        ),
        required=False,
    )

    bidirectional_by_reference = schema.List(
        title=u'Bidirectional by Reference',
        description=u'',
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.task.bidirectional_by_reference',
        ),
        required=False,
    )

    bidirectional_by_value = schema.List(
        title=u'Bidirectional by Value',
        description=u'',
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.task.bidirectional_by_value',
        ),
        required=False,
    )

    private_task_feature_enabled = schema.Bool(
        title=u'Enable private task feature',
        description=u'Whether private task features is enabled',
        default=True)


class ISuccessorTaskController(Interface):
    """The successor task controller manages predecessor and successor
    references between tasks.
    """

    def get_predecessor(self, default=None):
        """Returns the predecessor of the adapted object or ``None`` if it
        has none or if the predecessor does not exist anymore. The
        predecessor is returned as solr flair.
        """

    def set_predecessor(self, oguid):
        """Sets the predecessor on the adapted object to ``oguid``.
        """

    def get_successors(self):
        """Returns all successors of the adapted context as solr flair objects.
        """


class IResponseSyncerSender(Interface):
    """Handles the syncing process between tasks on different admin-units.
    """

    def sync_related_tasks(transition, text, **kwargs):
        """Starts the syncing process of the current task and
        returns all synced tasks in a list.
        """

    def get_related_tasks_to_sync(transition):
        """Returns all the tasks needed to be synced.

        Each task can have copies of itself (successors) or is a copy
        of another task (predecessor). This happens, if if a user delegates
        a task to another admin-unit.

        This function returns all successors/predecessors of a task.
        """

    def sync_related_task(task, transition, text, **kwargs):
        """Syncs the given task with its remote task.
        Raises an exception if syncing failed.
        """

    def extend_payload(payload, task, **kwargs):
        """Extends the payload with additional data.
        Returns the current instance object.
        """

    def raise_sync_exception(task, transition, text, **kwargs):
        """Raises the ResponseSyncerSenderException if syncing the
        task was failed
        """


class ITaskDocumentsTransporter(Interface):
    """Utility for transporting documents related to a task.
    """

    def copy_documents_from_remote_task(task, target, documents=None):
        """Copy documents from a remote `task` to a `target`.

        Copyable documents: the documents need to be either referenced from
        the task (relatedItems) or stored within the task.

        Arguments:
        task -- globalindex task object
        target -- container on the local client where the documents will
        be added
        documents -- if `None`, all related tasks are copied - otherwise a
        list of intids is expected.

        An intids mapping (old => new) is returned.
        """


class IYearfolderStorer(Interface):
    """Interface for the YearfolderStorer adpater, which provide
    the functionality to store a forwarding in the actual yearfolder. """

    def store_in_yearfolder():
        """Move the forwarding (adapted context) in the actual yearfolder."""


class IDeadlineModifier(Interface):

    def is_modify_allowed():
        """Check if the current user is allowed to modify the deadline:
            - state is `in-progress` or `open`
            - AND is issuer or is admin
            """

    def modify_deadline(new_deadline, text, transition):
        """Handles the whole deadline mofication process:
            - Set the new deadline
            - Add response
            - Handle synchronisation if needed
            """


class ICommentResponseHandler(Interface):

    def is_allowed():
        """Check if the current user is allowed to add a comment response
        """

    def add_response(text):
        """Handles the whole repsponse process:
            - Create response obj
            - Append response obj to parent
            - Record activity
            - Sync the response with tasks on other admin-units
        """
