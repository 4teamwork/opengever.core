from five import grok
from zope import schema
from zope.app.container.interfaces import IObjectAddedEvent
from zope.interface import Interface, alsoProvides

from plone.directives import form

from opengever.base import _


class ICreatorAware(Interface):
    """ Marker Interface for ICreator behavior
    """


class ICreator(form.Schema):

    form.omitted('creators')
    creators = schema.Tuple(
        title=_(u'label_creators', u'Creators'),
        description=_(u'help_creators', u''),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
    )


alsoProvides(ICreator, form.IFormFieldProvider)


@grok.subscribe(ICreatorAware, IObjectAddedEvent)
def add_creator(obj, event):
    obj.addCreator()
