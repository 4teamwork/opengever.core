from collective import dexteritytextindexer
from opengever.repository import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from zope import schema
from zope.interface import Interface
from zope.interface import alsoProvides

"""TODO Update live search to display result in preferred language"""


class IFrenchTitleBehaviorMarker(Interface):
    """Marker interface for the french title behavior."""


class IFrenchTitleBehavior(form.Schema):
    """Additional behavior providing a french title.
    """

    dexteritytextindexer.searchable('title_fr')
    title_fr = schema.TextLine(
        title=_(u'label_title_fr', default=u'French title'),
        description=_(u'help_title_fr', default=u''),
        required=True)


alsoProvides(IFrenchTitleBehavior, IFormFieldProvider)
