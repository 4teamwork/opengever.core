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

    task_types_uni_ref = schema.List(
        title = u'Task Types Unidirectional by Reference',
        description = u'',
        default = [u'Zur Kenntnisnahme',],
        value_type = schema.TextLine(title=u"Name"),
        required = False,
    )
    
    crop_length = schema.Int(title=u"Crop length", default=20)

    task_types_uni_val = schema.List(
        title = u'Unidirectional by Value',
        description = u'',
        default = [u'Zur direkten Erledigung',],
        value_type = schema.TextLine(title=u"Name"),
        required = False,
    )
        
    task_types_bi_ref = schema.List(
        title = u'Bidirectional by Reference',
        description = u'',
        default = [u'Zur Stellungnahme',
                   u'Zur Genehmigung',
                   u'Zur Pruefung/Korrektur',
                   u'Zum Bericht/Antrag',],
        value_type = schema.TextLine(title=u"Name"),
        required = False,
    )

    task_types_bi_val = schema.List(
        title = u'Bidirectional by Value',
        description = u'',
        default = [],
        value_type = schema.TextLine(title=u'Name'),
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
