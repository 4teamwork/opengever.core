from five import grok
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.ogds.base.interfaces import IContactInformation
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
import os.path


@grok.subscribe(IDocumentSchema, IObjectAddedEvent)
@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
def resolve_document_author(document, event):
    if getattr(document, 'document_author', None):
        info = getUtility(IContactInformation)
        if info.is_user(document.document_author):
            user = info.get_user(document.document_author)
            if user:
                document.document_author = info.describe(
                    user, with_principal=False, with_email=False)

                document.reindexObject(idxs=['sortable_author'])


@grok.subscribe(IDocumentSchema, IObjectCreatedEvent)
@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
def set_digitally_available(doc, event):
    """set the digitally_available field,
    if a file exist the document is digital available"""

    if doc.file:
        doc.digitally_available = True
    else:
        doc.digitally_available = False


@grok.subscribe(IDocumentSchema, IObjectCreatedEvent)
@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
def sync_title_and_filename_handler(doc, event):
    """Syncs the document and the filename (#586):
    o If there is no title but a file, use the filename (without extension) as
    title.
    o If there is a title and a file, use the normalized title as filename
    """
    normalizer = getUtility(IIDNormalizer)
    if not doc.title and doc.file:
        # use the filename without extension as title
        basename, ext = os.path.splitext(doc.file.filename)
        doc.title = basename
        doc.file.filename = ''.join(
            [normalizer.normalize(basename), ext])
    elif doc.title and doc.file:
        # use the title as filename
        basename, ext = os.path.splitext(doc.file.filename)
        doc.file.filename = ''.join(
            [normalizer.normalize(doc.title), ext])


@grok.subscribe(IDocumentSchema, IObjectCopiedEvent)
def set_copyname(doc, event):
    """Documents wich are copied, should be renamed to copy of filename
    """

    key = 'prevent-copyname-on-document-copy'
    request = getRequest()

    if request.get(key, False):
        return
    doc.title = u'%s %s' % (
        translate(_('copy_of', default="copy of"), context=request),
        doc.title)
