from five import grok
from OFS.interfaces import IObjectClonedEvent
from opengever.document import _
from opengever.document.behaviors import IBaseDocument
from opengever.document.document import IDocumentSchema
from opengever.ogds.base.utils import ogds_service
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
import os.path


@grok.subscribe(IDocumentSchema, IObjectClonedEvent)
def create_initial_version(obj, event):
    """When a object was copied, create an initial version.
    """
    portal = getSite()
    pr = portal.portal_repository
    history = pr.getHistory(obj)

    if history is not None and not len(history) > 0:
        comment = translate(_(u'label_initial_version_copied',
                            default="Initial version (document copied)"),
                            context=getRequest())
        # Create an initial version
        pr._recursiveSave(obj, {}, pr._prepareSysMetadata(comment),
            autoapply=pr.autoapply)


@grok.subscribe(IDocumentSchema, IObjectAddedEvent)
@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
def resolve_document_author(document, event):
    if getattr(document, 'document_author', None):
        user = ogds_service().fetch_user(document.document_author)
        if user:
            document.document_author = user.fullname()
            document.reindexObject(idxs=['sortable_author'])


@grok.subscribe(IDocumentSchema, IObjectCreatedEvent)
@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
def set_digitally_available(doc, event):
    """Set the digitally_available field, if a file exist the document is
    digitally available.
    """
    if doc.file:
        doc.digitally_available = True
    else:
        doc.digitally_available = False


@grok.subscribe(IDocumentSchema, IObjectCreatedEvent)
@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
def sync_title_and_filename_handler(doc, event):
    """Syncs the document and the filename (#586):

    - If there is no title but a file, use the filename (without extension) as
    title.
    - If there is a title and a file, use the normalized title as filename

    """
    normalizer = getUtility(IIDNormalizer)
    if not doc.file:
        return

    basename, ext = os.path.splitext(doc.file.filename)
    if not doc.title:
        # use the filename without extension as title
        doc.title = basename
        doc.file.filename = u''.join(
            [normalizer.normalize(basename), ext])
    elif doc.title:
        # use the title as filename
        doc.file.filename = u''.join(
            [normalizer.normalize(doc.title), ext])


@grok.subscribe(IBaseDocument, IObjectCopiedEvent)
def set_copyname(doc, event):
    """Documents wich are copied, should be renamed to copy of filename."""
    key = 'prevent-copyname-on-document-copy'
    request = getRequest()

    if request.get(key, False):
        return
    doc.title = u'%s %s' % (
        translate(_('copy_of', default="copy of"), context=request),
        doc.title)
