from AccessControl.unauthorized import Unauthorized
from opengever.document import _
from opengever.document.approvals import IApprovalList
from opengever.document.versioner import Versioner
from opengever.ogds.models.service import ogds_service
from zope.globalrequest import getRequest
from zope.i18n import translate


def resolve_document_author(document, event):
    if getattr(document, 'document_author', None):
        user = ogds_service().fetch_user(
            document.document_author, username_as_fallback=True)
        if user:
            document.document_author = user.fullname()
            document.reindexObject(idxs=['UID', 'document_author'])


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


def cleanup_document_approvals(doc, event):
    """When a document gets copied, only the current version approvals
    should be copied."""

    try:
        current_version = Versioner(event.original).get_current_version_id(
            missing_as_zero=True)
    except Unauthorized:
        # In some cases the current user is not allowed to access the history
        # metadata of the original object, in this case we remove all approvals
        current_version = None

    IApprovalList(doc).cleanup_copied_approvals(current_version)
