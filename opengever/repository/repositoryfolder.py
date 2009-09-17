
from zope import schema
from zope.interface import implements, invariant, Invalid

from plone.dexterity import content
from plone.directives import form
from plone.directives import dexterity
from plone.app.dexterity.behaviors import metadata

from opengever.repository import _
from opengever.repository.interfaces import IRepositoryFolder

class IRepositoryFolderSchema(metadata.IBasic):
    """ A Repository Folder
    """

    form.omitted('title')
    form.order_before(effective_title = '*')
    effective_title = schema.TextLine(
            title = u'Title',
            required = True
    )

    reference_number = schema.Int(
            title = _(u'label_reference_number', default=u'Reference'),
            description = _(u'help_reference_number', default=u''),
            required = False,
            min = 1,
    )


@form.default_value(field=IRepositoryFolderSchema['reference_number'])
def reference_number_default_value(data):
    highest_reference_number = 0
    for obj in data.context.listFolderContents():
        if IRepositoryFolder.providedBy(obj):
            if obj.reference_number > highest_reference_number:
                highest_reference_number = obj.reference_number
    highest_reference_number += 1
    return highest_reference_number


class RepositoryFolder(content.Container):

    implements(IRepositoryFolder)

    def Title(self):
        title = u' %s' % self.effective_title
        obj = self
        while IRepositoryFolder.providedBy(obj):
            if hasattr(obj, 'reference_number'):
                title = unicode(obj.reference_number) + '.' + title
            obj = obj.aq_inner.aq_parent
        return title

