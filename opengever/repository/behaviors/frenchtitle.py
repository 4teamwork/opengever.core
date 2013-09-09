from plone.directives import form
from collective import dexteritytextindexer
from zope import schema
from opengever.repository import _
from zope.interface import alsoProvides
from plone.autoform.interfaces import IFormFieldProvider

class IFrenchTitleBehavior(form.Schema):
    """Additional behavior providing a french title.
    """

    dexteritytextindexer.searchable('title_fr')
    title_fr = schema.TextLine(
        title=_(u'label_title_fr', default=u'French title'),
        description=_(u'help_title_fr', default=u''),
        required=True)


alsoProvides(IFrenchTitleBehavior, IFormFieldProvider)