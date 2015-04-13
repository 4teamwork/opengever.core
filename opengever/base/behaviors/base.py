from collective import dexteritytextindexer
from opengever.base import _
from plone.app.dexterity.behaviors import metadata
from plone.directives import form
from zope import schema
from zope.interface import Interface, alsoProvides


class IOpenGeverBase(form.Schema):
    """ IOpengeverBase contains title and description fields
    This is a schema interface, not a marker interface!
    """
    form.fieldset(
        u'common',
        label=_(u'fieldset_common', default=u'Common'),
        fields=[
            u'title',
            u'description',
            ],
        )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=True
        )

    dexteritytextindexer.searchable('description')
    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        description=_(u'help_description', default=u''),
        required=False,
        missing_value=u'',
        default=u'',
        )


alsoProvides(IOpenGeverBase, form.IFormFieldProvider)


class IOpenGeverBaseMarker(Interface):
    pass


class OpenGeverBase(metadata.MetadataBase):

    title = metadata.DCFieldProperty(
        metadata.IBasic['title'],
        get_name='title',
        set_name='setTitle')

    def _get_description(self):
        return self.context.description

    def _set_description(self, value):
        if isinstance(value, str):
            raise ValueError('Description must be unicode.')
        self.context.description = value
    description = property(_get_description, _set_description)
