
from zope import schema
from zope.interface import implements

from plone.dexterity import content
from plone.directives import form
from plone.directives import dexterity
from plone.app.dexterity.behaviors import metadata

from opengever.repository import _
from opengever.repository.interfaces import IRepositoryFolder

class IRepositoryFolderSchema(form.Schema):
    """ A Repository Folder
    """

    record_pos = schema.Int(
            title = _(u'Record Position'),
            required = False,
    )
    real_title = schema.TextLine(
            title = u'Title',
            required = True
    )

    form.omitted('title')
    title = schema.TextLine(
            title = u'_title_',
            required = False
    )


@form.default_value(field=IRepositoryFolderSchema['record_pos'])
def record_pos_default_value(data):
    highest_record_pos = -1
    for obj in data.context.listFolderContents():
        if IRepositoryFolder.providedBy(obj):
            if obj.record_pos > highest_record_pos:
                highest_record_pos = obj.record_pos
    highest_record_pos += 1
    return highest_record_pos


class RepositoryFolder(content.Container):

    implements(IRepositoryFolder)

    def Title(self):
        title = u' %s' % self.real_title
        obj = self
        while IRepositoryFolder.providedBy(obj):
            if hasattr(obj, 'record_pos'):
                title = unicode(obj.record_pos) + '.' + title
            obj = obj.aq_inner.aq_parent
        return title

