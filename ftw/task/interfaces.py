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

    instructions = schema.Dict(
        title = u'Instructions Vocabulary',
        description = u'',
        default = {u'Zur Kenntnisnahme': u'unidirektional',
                   u'Zur direkten Erledigung': u'unidirektional',
                   u'Zur Stellungnahme': u'bidirektional',},
        key_type = field.TextLine(title=u"Name"),
        value_type = field.TextLine(title=u"Typ"),
    )
