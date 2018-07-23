from opengever.document import _
from opengever.ogds.base.utils import ogds_service
from plone.i18n.normalizer.interfaces import IFileNameNormalizer
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.i18n import translate
import os.path


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


def sync_title_and_filename_handler(doc, event):
    """Syncs the document and the filename (#586):

    - If there is no title but a file, use the filename (without extension) as
    title.
    - If there is a title and a file, use the normalized title as filename

    """
    normalizer = getUtility(IFileNameNormalizer, name='gever_filename_normalizer')

    if not doc.file:
        return

    basename, ext = os.path.splitext(doc.file.filename)
    if not doc.title:
        # use the filename without extension as title
        doc.title = basename
        doc.file.filename = normalizer.normalize(basename, extension=ext)
    elif doc.title:
        # use the title as filename
        doc.file.filename = normalizer.normalize(doc.title, extension=ext)


def set_copyname(doc, event):
    """Documents wich are copied, should be renamed to copy of filename."""
    key = 'prevent-copyname-on-document-copy'
    request = getRequest()

    if request.get(key, False):
        return
    doc.title = u'%s %s' % (
        translate(_('copy_of', default="copy of"), context=request),
        doc.title)
