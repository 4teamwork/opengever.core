from opengever.base.browser.helper import get_css_class
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from opengever.base.sentry import log_msg_to_sentry
from opengever.document.activities import DocumentAuthorChangedActivity
from opengever.document.activities import DocumentTitleChangedActivity
from opengever.document.activities import DocumenVersionCreatedActivity
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.docprops import DocPropertyWriter
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ITemplateDocumentMarker
from opengever.dossier.templatefolder.utils import is_directly_within_template_folder
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent
from traceback import format_exc
from zope.container.interfaces import IContainerModifiedEvent
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from zope.lifecycleevent import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectMovedEvent
import logging


DISABLE_DOCPROPERTY_UPDATE_FLAG = 'disable_docproperty_update'


logger = logging.getLogger('opengever.document.handlers')


def unshadow_on_upload(context, event):
    if context.is_shadow_document() and context.has_file():
        context.leave_shadow_state()


def checked_out(context, event):
    # Don't prevent checkout by failure to update DocProperties
    _update_docproperties(context, raise_on_error=False)
    _update_favorites_icon_class(context)


def checked_in(context, event):
    _update_favorites_icon_class(context)


def checkout_canceled(context, event):
    _update_favorites_icon_class(context)


def before_documend_checked_in(context, event):
    # Don't prevent checkin by failure to update DocProperties
    _update_docproperties(context, raise_on_error=False)


def document_or_mail_moved_or_added(context, event):
    if IObjectRemovedEvent.providedBy(event):
        return

    if IObjectMovedEvent.providedBy(event):
        context.reindexObject(
            idxs=["getObjPositionInParent", "reference", "sortable_reference", "metadata"]
        )

    if IDocumentSchema.providedBy(context):
        document_moved_or_added(context, event)


def document_moved_or_added(context, event):
    if context.REQUEST.get(DISABLE_DOCPROPERTY_UPDATE_FLAG):
        return

    if IObjectAddedEvent.providedBy(event):
        # Be strict when adding new documents to GEVER, lenient on moving
        # ones that already made it into the system
        _update_docproperties(context, raise_on_error=False)
    else:
        _update_docproperties(context, raise_on_error=False)


def mark_as_template_document(context, event):
    if context.portal_type != 'opengever.document.document':
        # we do not want to mark sablon templates and such.
        return
    if is_directly_within_template_folder(context):
        alsoProvides(context, ITemplateDocumentMarker)
        context.reindexObject(idxs=['object_provides'])
    elif ITemplateDocumentMarker.providedBy(context):
        noLongerProvides(context, ITemplateDocumentMarker)
        context.reindexObject(idxs=['object_provides'])


def _update_docproperties(document, raise_on_error=False):
    try:
        DocPropertyWriter(document).update()
    except Exception as exc:
        if not raise_on_error:
            path = '/'.join(document.getPhysicalPath())
            logger.warn('Failed to update DocProperties for %r' % path)
            logger.warn('\n%s' % format_exc(exc))
            logger.warn('Updating of DocProperties has therefore been skipped')
            log_msg_to_sentry(
                'DocProperties update skipped', level='warning',
                extra={'document_that_failed': repr(document)})
            return

        raise


def set_archival_file_state(context, event):
    # Because every filewidget is always marked as changed, in the event
    # descriptions, even when no file has changed, we have to check the request
    request = context.REQUEST

    if request.get('ACTUAL_URL').endswith('edit_archival_file'):
        field_name = 'archival_file'
    else:
        field_name = 'IDocumentMetadata.archival_file'

    fileupload = request.get('form.widgets.{}'.format(field_name))
    action = request.get('form.widgets.{}.action'.format(field_name), '')

    if bool(fileupload):
        ArchivalFileConverter(context).handle_manual_file_upload()

    file_removed = action == u'remove'
    file_removed_in_archival_form = isinstance(action, list) and u'remove' in action

    if file_removed or file_removed_in_archival_form:
        ArchivalFileConverter(context).remove_state()


def _update_favorites_icon_class(context):
    """Event handler which updates the icon_class of all existing favorites for
    the current context.
    """
    favorites_query = Favorite.query.filter(
        Favorite.oguid == Oguid.for_object(context))

    for favorite in favorites_query.all():
        favorite.icon_class = get_css_class(context, for_user=favorite.userid)


def document_reverted_to_version(context, event):
    if event.create_version:
        document_version_created(context, event)


def document_version_created(context, event):
    DocumenVersionCreatedActivity(
        context, getRequest(), getattr(event, "comment", None)).record()


def author_or_title_changed(context, event):
    if IContainerModifiedEvent.providedBy(event):
        return
    if ILocalrolesModifiedEvent.providedBy(event):
        return

    author_changed = False
    title_changed = False
    for desc in event.descriptions:
        for attr in desc.attributes:
            if attr in ['IDocumentSchema.title', 'IOGMail.title', 'title']:
                title_changed = True
            if attr == 'IDocumentMetadata.document_author':
                author_changed = True
    if title_changed:
        DocumentTitleChangedActivity(context, getRequest()).record()
    if author_changed:
        DocumentAuthorChangedActivity(context, getRequest()).record()


def mark_pending_changes(context, event):
    if context.REQUEST.method == 'PUT':
        context.has_pending_changes = True
    else:
        for desc in event.descriptions:
            if 'IDocumentSchema.file' in desc.attributes or 'file' in desc.attributes:
                context.has_pending_changes = True
                return


def unmark_pending_changes(context, event):
    context.has_pending_changes = False
