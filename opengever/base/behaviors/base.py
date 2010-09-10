
from zope.interface import Interface, alsoProvides
from zope import schema

from plone.app.dexterity.behaviors import metadata
from plone.directives import form

from opengever.base import _

class IOpenGeverBase(form.Schema):
    """ IOpengeverBase contains title and description fields
    This is a schema interface, not a marker interface!
    """
    form.fieldset(
        u'common',
        label = _(u'fieldset_common', default=u'Common'),
        fields = [
            u'title',
            u'description',
            ],
        )

    title = schema.TextLine(
        title = _(u'label_title', default=u'Title'),
        required = True
        )

    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        description = _(u'help_description', default=u''),
        required = False,
        )


alsoProvides(IOpenGeverBase, form.IFormFieldProvider)

class IOpenGeverBaseMarker(Interface):
    pass

class OpenGeverBase( metadata.MetadataBase ):

    title = metadata.DCFieldProperty( metadata.IBasic['title'],
                                      get_name = 'title',
                                      set_name = 'setTitle')
    description = metadata.DCFieldProperty( metadata.IBasic['description'],
                                            get_name = 'Description',
                                            set_name = 'setDescription')
