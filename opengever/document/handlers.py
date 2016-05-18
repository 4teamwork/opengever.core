from five import grok
from opengever.document.archival_file import ARCHIVAL_FILE_STATE_MANUALLY
from opengever.document.archival_file import ArchivalFileConverter
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import IObjectCheckedInEvent
from opengever.document.interfaces import IObjectCheckedOutEvent
from opengever.dossier.docprops import DocPropertyWriter
from zope.lifecycleevent import IObjectMovedEvent
from zope.lifecycleevent import IObjectRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


DISABLE_DOCPROPERTY_UPDATE_FLAG = 'disable_docproperty_update'


@grok.subscribe(IDocumentSchema, IObjectCheckedOutEvent)
def checked_out(context, event):
    _update_docproperties(context)


@grok.subscribe(IDocumentSchema, IObjectCheckedInEvent)
def checked_in(context, event):
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
    archival_file_changed = False

    for desc in event.descriptions:
        for attr in desc.attributes:
            if attr == 'IDocumentMetadata.archival_file':
                archival_file_changed = True
                break

    if archival_file_changed:
        ArchivalFileConverter(context).set_state(ARCHIVAL_FILE_STATE_MANUALLY)
