from Acquisition import aq_parent
from ftw.journal.interfaces import IAnnotationsJournalizable
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.exportng.utils import Attribute
from opengever.exportng.utils import document_parent
from opengever.exportng.utils import userid_to_email
from opengever.journal.manager import JournalManager


DOCUMENT_ACTION_TYPE_EVENT_MAPPING = {
    'Document added': ('DOCUMENT_CREATED', True, 'DOCUMENT_ADDED'),
    'Object moved to trash': ('DOCUMENT_CANCELLED', False, 'DOCUMENT_CANCELLED'),
    'Object restore': ('DOCUMENT_RESTORED', False, 'DOCUMENT_RESTORED'),
    'Document checked in': ('CONTENT_CHANGED', False, None),
}
DOSSIER_ACTION_TYPE_EVENT_MAPPING = {
    # 'Dossier included in a zip export': 'DOSSIER_DOWNLOADED',
    'Dossier added': ('OBJECT_CREATED', True, 'SUBDOSSIER_ADDED'),
    'Dossier state changed': ('_DOSSIER_STATE_CHANGED', False, '_DOSSIER_STATE_CHANGED'),
}
DOSSIER_STATE_CHANGES = {
    'Dossier state changed to dossier-state-resolved': 'DOSSIER_CLOSED',
    'Dossier state changed to dossier-state-inactive': 'DOSSIER_CANCELLED',
    'Dossier state changed to dossier-state-active': 'DOSSIER_RESTORED',
}

JOURNAL_TABLE = 'journal_entries'
JOURNAL_MAPPING = [
    Attribute('UID', 'objexternalkey', 'varchar'),
    Attribute('relatedobj', 'historyobject', 'varchar'),
    Attribute('action', 'event', 'varchar'),
    Attribute('time', 'timestamp', 'datetime'),
    Attribute('actor', 'user', 'varchar'),
    Attribute('journal', '_journal', 'varchar'),
]


def get_journal_entries_from_document(obj):
    res = []
    if IAnnotationsJournalizable.providedBy(obj):
        journal_entries = JournalManager(obj).list()
        for entry in journal_entries:
            action_type = entry.get('action', {}).get('type')
            obj_event, has_histobj, parent_event = DOCUMENT_ACTION_TYPE_EVENT_MAPPING.get(
                action_type, (None, False, None))

            parent = document_parent(obj)
            if has_histobj and not IDossierMarker.providedBy(parent):
                continue

            if obj_event is not None:
                histobj = parent.UID() if has_histobj else None
                res.append({
                    'objexternalkey': obj.UID(),
                    'timestamp': entry['time'].asdatetime().replace(tzinfo=None),
                    'user': userid_to_email(entry['actor']),
                    'historyobject': histobj,
                    'event': obj_event,
                    '_journal': 'documents',
                })
            if parent_event is not None:
                res.append({
                    'objexternalkey': parent.UID(),
                    'timestamp': entry['time'].asdatetime().replace(tzinfo=None),
                    'user': userid_to_email(entry['actor']),
                    'historyobject': obj.UID(),
                    'event': parent_event,
                    '_journal': 'dossiers',
                })

    return res


def get_journal_entries_from_dossier(obj):
    res = []
    if IAnnotationsJournalizable.providedBy(obj):
        journal_entries = JournalManager(obj).list()
        for entry in journal_entries:
            action_type = entry.get('action', {}).get('type')
            obj_event, has_histobj, parent_event = DOSSIER_ACTION_TYPE_EVENT_MAPPING.get(
                action_type, (None, False, None))
            if obj_event == '_DOSSIER_STATE_CHANGED':
                title = entry.get('action', {}).get('title')
                obj_event = DOSSIER_STATE_CHANGES.get(title)
            if parent_event == '_DOSSIER_STATE_CHANGED':
                title = entry.get('action', {}).get('title')
                parent_event = DOSSIER_STATE_CHANGES.get(title)

            parent = aq_parent(obj)
            if obj_event is not None:
                histobj = parent.UID() if has_histobj else None
                res.append({
                    'objexternalkey': obj.UID(),
                    'timestamp': entry['time'].asdatetime().replace(tzinfo=None),
                    'user': userid_to_email(entry['actor']),
                    'historyobject': histobj,
                    'event': obj_event,
                    '_journal': 'dossiers',
                })
            # XXX: DOSSIER_CLOSED on parent is currently not supported in NG!?
            if parent_event is not None and parent_event != 'DOSSIER_CLOSED':
                if parent.portal_type != 'opengever.repository.repositoryfolder':
                    res.append({
                        'objexternalkey': parent.UID(),
                        'timestamp': entry['time'].asdatetime().replace(tzinfo=None),
                        'user': userid_to_email(entry['actor']),
                        'historyobject': obj.UID(),
                        'event': parent_event,
                        '_journal': 'dossiers',
                    })
    return res
