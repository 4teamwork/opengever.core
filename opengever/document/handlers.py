from opengever.base.browser.helper import get_css_class
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from opengever.base.sentry import log_msg_to_sentry
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.docprops import DocPropertyWriter
from traceback import format_exc
from zope.lifecycleevent import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectAddedEvent
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


def document_moved_or_added(context, event):
    if IObjectRemovedEvent.providedBy(event):
        return

    if context.REQUEST.get(DISABLE_DOCPROPERTY_UPDATE_FLAG):
        return

    if IObjectAddedEvent.providedBy(event):
        # Be strict when adding new documents to GEVER, lenient on moving
        # ones that already made it into the system
        _update_docproperties(context, raise_on_error=True)
    else:
        _update_docproperties(context, raise_on_error=False)


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
