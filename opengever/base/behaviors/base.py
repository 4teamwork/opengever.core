
from zope.interface import Interface, alsoProvides, implements
from zope import schema
from zope.component import adapts

from plone.app.dexterity.behaviors import metadata
from plone.directives import form

from opengever.base import _

class IOpenGeverBase(metadata.IBasic):
    """ IOpengeverBase contains title and description fields
    This is a schema interface, not a marker interface!
    """
    form.order_before(description = '*')
    form.order_before(title = '*')

alsoProvides(IOpenGeverBase, form.IFormFieldProvider)

class IOpenGeverBaseMarker(Interface):
    pass

class OpenGeverBase(metadata.MetadataBase):
    #XXX wird nicht ausgeführt
    def __init__(self, *args, **kwargs):
        super(OpenGeverBase, self).__init__(*args, **kwargs)
        self.context.addCreator()
    
    #XXX
    def Title(self):
        return self.title

    title = metadata.DCFieldProperty(metadata.IBasic['title'], get_name = 'title', set_name = 'setTitle')
    description = metadata.DCFieldProperty(metadata.IBasic['description'], get_name = 'Description', set_name = 'setDescription')