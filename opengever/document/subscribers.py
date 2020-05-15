from opengever.document import _
from opengever.ogds.models.service import ogds_service
from zope.globalrequest import getRequest
from zope.i18n import translate


def resolve_document_author(document, event):
    if getattr(document, 'document_author', None):
        user = ogds_service().fetch_user(document.document_author)
        if user:
            document.document_author = user.fullname()
            document.reindexObject(idxs=['sortable_author'])


def set_digitally_available(doc, event):
    """Set the digitally_available field, if a file exist the document is
    digitally available.
    """
    if doc.file:
        doc.digitally_available = True
    else:
        doc.digitally_available = False


def set_copyname(doc, event):
    """Documents wich are copied, should be renamed to copy of filename."""
    key = 'prevent-copyname-on-document-copy'
    request = getRequest()

    if request.get(key, False):
        return
    doc.title = u'%s %s' % (
        translate(_('copy_of', default="copy of"), context=request),
        doc.title)
