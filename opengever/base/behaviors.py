
from zope.interface import Interface, alsoProvides, implements
from zope import schema

from plone.app.dexterity.behaviors import metadata
from plone.directives import form

from opengever.base import _

class IOpenGeverBase(form.Schema):
    """ IOpengeverBase contains title and description fields
    This is a schema interface, not a marker interface!
    """
    title = schema.TextLine(
        title = _(u'label_title', default=u'Title'),
        required = True
        )
        
    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        description = _(u'help_description', default=u'A short summary of the content.'),
        required = False,
        missing_value = u'',
        )
    
    form.order_before(description = '*')
    form.order_before(title = '*')

alsoProvides(IOpenGeverBase, form.IFormFieldProvider)


class OpenGeverBase(metadata.MetadataBase):
    implements(IOpenGeverBase)

    title = metadata.DCFieldProperty(IOpenGeverBase['title'], get_name = 'Title', set_name = 'setTitle')
    description = metadata.DCFieldProperty(IOpenGeverBase['description'], get_name = 'Description', set_name = 'setDescription')
