from opengever.base.browser.helper import get_css_class
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from opengever.document.archival_file import ArchivalFileConverter
from opengever.dossier.docprops import DocPropertyWriter
from zope.lifecycleevent import IObjectRemovedEvent


DISABLE_DOCPROPERTY_UPDATE_FLAG = 'disable_docproperty_update'


def checked_out(context, event):
    _update_docproperties(context)
    _update_favorites_icon_class(context)


def checked_in(context, event):
    _update_favorites_icon_class(context)


def before_documend_checked_in(context, event):
    _update_docproperties(context)


def document_moved_or_added(context, event):
    if IObjectRemovedEvent.providedBy(event):
        return

    if context.REQUEST.get(DISABLE_DOCPROPERTY_UPDATE_FLAG):
        return

    _update_docproperties(context)


def _update_docproperties(document):
    DocPropertyWriter(document).update()


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
