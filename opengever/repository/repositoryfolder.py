from Acquisition import aq_inner, aq_parent
from zope import schema
from zope.interface import implements
from plone.dexterity import content
from plone.directives import form
from plone.directives import dexterity
from opengever.repository import _
from opengever.repository.interfaces import IRepositoryFolder
from plone.app.content.interfaces import INameFromTitle
from five import grok

class IRepositoryFolderSchema(form.Schema):
    """ A Repository Folder
    """

    #form.omitted('title')
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

    description = schema.Text(
        title = _(u'label_description', default=u'Description'),
        description =  _(u'help_description', default=u'A short summary of the content.'),
        required = False,
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
            obj = aq_parent(aq_inner(obj))
        return title


class NameFromTitle(grok.Adapter):
    """ An INameFromTitle adapter for namechooser
        gets the name from effective_title
    """
    grok.implements(INameFromTitle)
    grok.context(IRepositoryFolder)
    
    def __init__(self, context):
        self.context = context
    
    @property
    def title(self):
        return self.context.effective_title
