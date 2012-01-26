from zope.interface import Interface
from zope.interface import directlyProvides
from zope.interface import Attribute
from zope import schema
from zope.viewlet.interfaces import IViewletManager
from zope.contentprovider.interfaces import ITALNamespaceData


class IResponseAdder(IViewletManager):

    mimetype = Attribute("Mime type for response.")
    use_wysiwyg = Attribute("Boolean: Use kupu-like editor.")

    def transitions_for_display():
        """Get the available transitions for this issue.
        """

    def severities_for_display():
        """Get the available severities for this issue.
        """

    def releases_for_display():
        """Get the releases from the project.
        """

    def managers_for_display():
        """Get the tracker managers.
        """

directlyProvides(IResponseAdder, ITALNamespaceData)


class ICreateResponse(Interface):
    pass

class ITaskSettings(Interface):

    crop_length = schema.Int(title=u"Crop length", default=20)

    unidirectional_by_reference = schema.List(
        title = u'Task Types Unidirectional by Reference',
        description = u'',
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.task.unidirectional_by_reference',
        ),
        required = False,
    )

    unidirectional_by_value = schema.List(
        title = u'Unidirectional by Value',
        description = u'',
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.task.unidirectional_by_value',
        ),
        required = False,
    )

    bidirectional_by_reference = schema.List(
        title = u'Bidirectional by Reference',
        description = u'',
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.task.bidirectional_by_reference',
        ),
        required = False,
    )

    bidirectional_by_value = schema.List(
        title = u'Bidirectional by Value',
        description = u'',
        value_type=schema.Choice(
            title=u"Name",
            vocabulary=u'opengever.task.bidirectional_by_value',
        ),
        required = False,
    )


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


class IWorkflowStateSyncer(Interface):
    """The state syncer syncs workflow states of related tasks (successors and
    predecessors).

    It is triggered by workflow changes, such as the direct_response view or the
    response add form. It automatically decides if it is necessary to change
    the state of a related task and performs the change.

    IStateSyncer is an adapter interface.
    """

    def __init__(context, request):
        pass

    def get_tasks_to_sync(transition):
        """Returns all related tasks which have to be updated when performing this
        `transition` on the current task in the current state.
        """

    def change_remote_tasks_workflow_state(transition, text):
        """Performs `transition` on related tasks and creates a response with
        `text`.
        """
