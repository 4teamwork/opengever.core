from collective import dexteritytextindexer
from opengever.base import _
from plone.app.dexterity.behaviors import metadata
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import Interface, alsoProvides


class IOpenGeverBase(model.Schema):
    """ IOpengeverBase contains title and description fields
    This is a schema interface, not a marker interface!
    """
    model.fieldset(
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
        required=False,
        missing_value=u'',
        default=u'',
        )


alsoProvides(IOpenGeverBase, IFormFieldProvider)


class IOpenGeverBaseMarker(Interface):
    pass


class OpenGeverBase(metadata.MetadataBase):

    def _get_title(self):
        return self.context.title

    def _set_title(self, value):
        if isinstance(value, str):
            raise ValueError('Title must be unicode.')
        self.context.title = value

    title = property(_get_title, _set_title)

    def _get_description(self):
        description = self.context.description
        if isinstance(description, str):
            return description.decode('utf-8')

        return description

    def _set_description(self, value):
        if isinstance(value, str):
            raise ValueError('Description must be unicode.')
        self.context.description = value

    description = property(_get_description, _set_description)
