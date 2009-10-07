
from five import grok

from zope.event import notify 
from zope.app.container.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from ftw.journal.events.events import JournalEntryEvent

from opengever.document.document import IDocumentSchema

from opengever.journal import _



ACTION_DOCUMENT_MODIFIED = 'Document modified'
@grok.subscribe(IDocumentSchema, IObjectModifiedEvent)
def document_modified(context, event):
    REQUEST = context.REQUEST
    entry = {
            'obj' : context,
            'action' : {
                    'type' : ACTION_DOCUMENT_MODIFIED,
                    'title' : _('default_comment_document_modified', 'Document modified'),
            },
            'comment' : REQUEST.get('cmfeditions_save_new_version', ''),
    }
    notify(JournalEntryEvent(**entry))



