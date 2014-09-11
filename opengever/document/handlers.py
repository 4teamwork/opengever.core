from five import grok
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import IObjectCheckedInEvent
from opengever.document.interfaces import IObjectCheckedOutEvent
from opengever.dossier.docprops import DocPropertyWriter
from zope.lifecycleevent import IObjectMovedEvent
from zope.lifecycleevent import IObjectRemovedEvent


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

    _update_docproperties(context)


def _update_docproperties(document):
    DocPropertyWriter(document).update()
