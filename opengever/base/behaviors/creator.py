from five import grok
from opengever.base import _
from plone.directives import form
from zope import schema
from zope.interface import Interface, alsoProvides
from zope.lifecycleevent.interfaces import IObjectAddedEvent


class ICreatorAware(Interface):
    """ Marker Interface for ICreator behavior
    """


class ICreator(form.Schema):

    form.omitted('creators')
    creators = schema.Tuple(
        title=_(u'label_creators', u'Creators'),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
        default=(),
    )


alsoProvides(ICreator, form.IFormFieldProvider)


@grok.subscribe(ICreatorAware, IObjectAddedEvent)
def add_creator(obj, event):
    obj.addCreator()
