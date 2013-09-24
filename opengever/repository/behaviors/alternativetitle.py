from collective import dexteritytextindexer
from opengever.repository import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from zope import schema
from zope.interface import Interface
from zope.interface import alsoProvides


class IAlternativeTitleBehaviorMarker(Interface):
    """Marker interface for the alternative title behavior."""


class IAlternativeTitleBehavior(form.Schema):
    """Additional behavior providing a alternative title.
    """

    dexteritytextindexer.searchable('alternative_title')
    alternative_title = schema.TextLine(
        title=_(u'label_alternative_title',
                default=u'Title in alternative language'),
        description=_(u'help_alternative_language', default=u''),
        required=True)


alsoProvides(IAlternativeTitleBehavior, IFormFieldProvider)
