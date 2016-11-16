from five import grok
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import IObjectBeforeCheckInEvent
from opengever.document.interfaces import IObjectCheckedOutEvent
from opengever.dossier.docprops import DocPropertyWriter
from zope.lifecycleevent import IObjectMovedEvent
from zope.lifecycleevent import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


DISABLE_DOCPROPERTY_UPDATE_FLAG = 'disable_docproperty_update'


@grok.subscribe(IDocumentSchema, IObjectCheckedOutEvent)
def checked_out(context, event):
    _update_docproperties(context)


@grok.subscribe(IDocumentSchema, IObjectBeforeCheckInEvent)
def update_docproperties(context, event):
    _update_docproperties(context)


@grok.subscribe(IDocumentSchema, IObjectMovedEvent)
def update_moved_doc_properties(context, event):
    if IObjectRemovedEvent.providedBy(event):
        return

    if context.REQUEST.get(DISABLE_DOCPROPERTY_UPDATE_FLAG):
        return

    _update_docproperties(context)


def _update_docproperties(document):
    DocPropertyWriter(document).update()


@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
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
