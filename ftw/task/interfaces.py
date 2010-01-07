from zope.interface import Interface
from zope.interface import directlyProvides
from zope.interface import Attribute
from zope import schema
from zope.viewlet.interfaces import IViewletManager
from zope.contentprovider.interfaces import ITALNamespaceData
from plone.registry import field


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
        value_type = field.TextLine(title=u"Name"),
    )

    task_types_uni_val = schema.List(
        title = u'Unidirectional by Value',
        description = u'',
        default = [u'Zur direkten Erledigung',],
        value_type = field.TextLine(title=u"Name"),
    )
        
    task_types_bi_ref = schema.List(
        title = u'Bidirectional by Reference',
        description = u'',
        default = [u'Zur Stellungnahme',
                   u'Zur Genehmigung',
                   u'Zur Pruefung/Korrektur',
                   u'Zum Bericht/Antrag',],
        value_type = field.TextLine(title=u"Name"),    
    )

    task_types_bi_val = schema.List(
        title = u'Bidirectional by Value',
        description = u'',
        default = [],
        value_type = field.TextLine(title=u"Name"),
    )    

